import vlc 
import cv2 
import json 
import time 
import numpy as np
import streamlit as st 
import mediapipe as mp 
from pathlib import Path 
from typing import List, Union
#from procrustes import rotational 
from src.sdk.utils import StreamUtils
from configs import EnvConfig as env

mp_pose = mp.solutions.pose
vlc_instance = vlc.Instance("--no-xlib")

class TwoVideoStreamer(StreamUtils):
    def __init__(self, instruction_video_name: str, source_to_stream: Union[str, int, Path]) -> None:
        super(TwoVideoStreamer, self).__init__()
        self.instruction_video_name, self.source_to_stream = instruction_video_name, source_to_stream
        self.instruction_audio_path = Path(env.DATADIR) / 'processed' / self.instruction_video_name / f'{self.instruction_video_name}.mp4'
        self.instruction_video_preprocessed_path = Path(env.DATADIR) / 'processed' / self.instruction_video_name / f'{self.instruction_video_name}_preprocessed.mp4'
        self.instructor_keypoints_path = Path(env.DATADIR) / 'processed' / self.instruction_video_name / f'{self.instruction_video_name}_key_frames'

        with open(self.instructor_keypoints_path) as keypoints:
            self.instructor_keypoints = json.load(keypoints)
        
        print(self.instruction_video_preprocessed_path)
        print(self.instructor_keypoints_path)

        self.audioPlayer = vlc.MediaPlayer(vlc.Instance())
        self.audioPlayer.set_mrl(self.instruction_audio_path, ":no-video")
    

    # to be implemented later 

    # def _scale_and_align(self, r1, r2):
    #     result = rotational(r1, r2, translate=True)
    #     r1_at = np.dot(result.new_a, result.t)
    #     return r1_at, result.new_b
    
    def convert_results_to_numpy(self, results, _3d=False):
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            if not _3d:
                landmarks.append((landmark.x, landmark.y))
            else:
                landmarks.append((landmark.x, landmark.y, landmark.z))
        return np.array(landmarks)

        
    
    def yield_video_frames(self, instructor_video_source, student_video_source, loop: bool=False): 
        while student_video_source.isOpened():
            instructor_video_status, instructor_video_frame = instructor_video_source.read()
            student_video_status, student_video_frame = student_video_source.read()

            if instructor_video_status and student_video_status:
                instructor_video_frame = cv2.resize(instructor_video_frame, (1920, 1080))
                student_video_frame = cv2.resize(student_video_frame, (1920, 1080))

                yield instructor_video_frame, student_video_frame
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    break 
            else:
                break 

            if not instructor_video_source.isOpened() and loop: # looping the same video 
                instructor_video_source = cv2.VideoCapture(str(self.instruction_video_preprocessed_path)) 

        #instructor_video_source.close()
        cv2.destroyAllWindows()


# mode 1: gamefied matching 
# mode 2: simple matching | green -> match, red -> not match 

    def stream_video_to_app(self, loop: bool=True):
        instructor_video_source = cv2.VideoCapture(str(self.instruction_video_preprocessed_path))
        student_video_source = cv2.VideoCapture(self.source_to_stream) 
        app_window = st.image([])

        time.sleep(5)
        self.audioPlayer.play()

        with mp_pose.Pose(model_complexity=1 , min_detection_confidence=0.3, min_tracking_confidence=0.28) as pose:
            for (instructor_video_frame, student_video_frame), instructor_keypoints in zip(self.yield_video_frames(instructor_video_source, student_video_source, loop), self.instructor_keypoints):
                student_results = pose.process(student_video_frame)
                if student_results is not None and instructor_keypoints is not None:
                    #student_results = self.convert_results_to_numpy(results=student_results)
                    #procusted_instructor_keypoints, procusted_student_keypoints = self._scale_and_align(np.array(instructor_keypoints), student_results)
                    
                    student_video_frame = self._draw_pose(student_video_frame, student_results)
                frame_to_send = cv2.resize(np.concatenate([instructor_video_frame, student_video_frame], axis=1), (1280, 720))

                app_window.image(cv2.cvtColor(frame_to_send, cv2.COLOR_BGR2RGB))
                cv2.waitKey(1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s1', '--source1', type=str, required=True, default='UnderTheInfluenceChoreo'
    )

    parser.add_argument(
        '-s2', '--source2', type=int, required=False, default=0
    )
    args = parser.parse_args()
    streamer = TwoVideoStreamer(instruction_video_name=args.source1, source_to_stream=args.source2)
    
    # stream_video() method is deprecated 
    streamer.stream_video()