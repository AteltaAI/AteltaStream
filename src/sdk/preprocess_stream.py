import os 
import cv2 
import shutil
import numpy as np
import mediapipe as mp 

from tqdm import tqdm
from stqdm import stqdm
from pathlib import Path 
from typing import List, Tuple, Union, Optional 

from src.sdk.utils import StreamUtils
from configs import EnvConfig as env 

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class StreamerPreprocess(StreamUtils):
    def __init__(self, source_to_process : Union[str, Path]) -> None:
        super(StreamerPreprocess, self).__init__()
        self.source_to_process =  Path(source_to_process) if type(source_to_process) == str else source_to_process
        self.source_to_process = env.DATADIR / self.source_to_process
        #self.source_to_stream = Path(source_to_stream) if type(source_to_stream) == str else source_to_stream # check for the type of int (cam) 
        self.source_to_process_video_file_name, self.source_to_process_video_name = self.source_to_process.name, self.source_to_process.stem 
        self.isProcessed = False # change this to a database of meta data 
    
    @property # temporarily done this 
    def switch_dynamic_model_complexity(self):
        # TODO: Check the FPS during the video frame and then switch the model complexity for better latency 
        model_complexity = 2
        return model_complexity
    
    def _provide_video_writer_config(self, cap):
        """
        Provides the required configuraton to save the video
        args:
        -----
        cap : The capture object
        save_as : The file name to save the generated video file with corresponding predictions.
        """
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        size = (frame_width, frame_height)
        FPS = int(cap.get(cv2.CAP_PROP_FPS))

        file_to_save_as = Path(env.DATADIR) / 'processed' / self.source_to_process_video_name / f'{self.source_to_process_video_name}_preprocessed.mp4'
        if not os.path.isdir(str(Path(env.DATADIR) / 'processed' / self.source_to_process_video_name)):
            os.mkdir(str(Path(env.DATADIR) /  'processed' / self.source_to_process_video_name))
        
        vid_writer = cv2.VideoWriter(str(file_to_save_as), cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), FPS, size)
        return vid_writer

    def pre_process(self, st=False):
        """Preprocess the video and saves to the required directory 
        """
        preprocessed_key_frames = []
        video_source = cv2.VideoCapture(str(self.source_to_process))
        video_writer = self._provide_video_writer_config(video_source)
        total_frames = int(video_source.get(cv2.CAP_PROP_FRAME_COUNT))

        progressbar = stqdm if st else tqdm 
        
        for streamed_frame, results in progressbar(self.preprocess_frames(video_source), total=total_frames):
            if results.pose_landmarks is not None:
                preprocessed_key_frames.append(self.convert_pose_landmark_to_list(results))
            else:
                preprocessed_key_frames.append(None)
            if streamed_frame is not None:
                video_writer.write(streamed_frame)
         
        shutil.copy(self.source_to_process, Path(env.DATADIR) / 'processed' / self.source_to_process_video_name / self.source_to_process_video_file_name)
        print(f"=> Processing of video {self.source_to_process_video_name} finished and saved as {Path(env.DATADIR) / 'processed' / self.source_to_process_video_name / self.source_to_process_video_file_name}")

        key_frames_save_path = Path(env.DATADIR) / 'processed' / self.source_to_process_video_name / f'{self.source_to_process_video_name}_key_frames'
        self.save_object_to_device(save_path=key_frames_save_path, object=preprocessed_key_frames)
        print(f"=> Finished processing Keyframes as: {key_frames_save_path}")
        
        self.isProcessed = True 
        print("=> Preprocessing finished...")
        return True 


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s1', '--source1', type=str, required=True, default='raw/UnderTheInfluenceChoreo.mp4'
    )
    args = parser.parse_args()
    streamer = StreamerPreprocess(source_to_process=args.source1)
    streamer.pre_process()