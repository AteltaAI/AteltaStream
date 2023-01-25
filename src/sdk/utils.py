import cv2
import math
import json 
import numpy as np
import mediapipe as mp 
from pathlib import Path 
from typing import List, Union, Tuple, Any
from google.protobuf.pyext._message import RepeatedCompositeContainer

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# TODO: Try to understand mediapipe's plot landmark 
# TODO: Try to crop the side parts of the video for better resolution (1920 x 1080)

class StreamUtils:
    def __init__(self):
        pass 
    
    def _draw_pose(self, image, results):
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(50,122,150), thickness=3, circle_radius=4), 
            mp_drawing.DrawingSpec(color=(100,4,121), thickness=3, circle_radius=2)
            )
        return image 
    
    def preprocess_frames(self, cap):
        with mp_pose.Pose(model_complexity=2 , min_detection_confidence=0.3, min_tracking_confidence=0.28) as pose:
            while cap.isOpened():
                ret, frame = cap.read() 
                if ret: 
                    results = pose.process(frame)
                    if results: 
                        frame_to_send = self._draw_pose(frame, results)
                        yield frame_to_send, results
                    else:
                        yield frame, None 
                else:
                    return None, None 
    
    def save_object_to_device(self, save_path : Union[str, Path], object : Any) -> None:
        """Saves the object to the device 

        Args:
            save_path (Union[str, Path]): The path to save the file 
            object (Any): The object to save 
        
        NOTE: This methos uses json.dumps method to save the object
        """

        try:
            with open(save_path, 'w') as file_to_save :
                json.dump(object, file_to_save)
        except TypeError as e:
            print(f"=> Error saving: {e}")
            return None 
        print(f"=> Saved object as {save_path}")
         

    def convert_pose_landmark_to_list(self, pose_results : RepeatedCompositeContainer) -> List[Tuple[int, int]]:
        """Converts generated mediapipe pose landmarks to list

        Args:
            pose_results (RepeatedCompositeContainer): Mediapipe pose landmarks

        Returns:
            List[Tuple[int, int]]: The list of pose landmarks in the form of [(x, y)]
        """
        landmarks = []
        for landmark in pose_results.pose_landmarks.landmark:
            landmarks.append((landmark.x, landmark.y)) 
        return landmarks 

    def draw_custom_landmark(
        self, 
        image : np.ndarray,
        landmarks : List[Tuple[int, int]],
        connection: List[Tuple[int, int]],
        indices_to_avoid_nodes: List[int]=None,
        indices_to_avoid_edges: List[int]=None,
        dot_color: Tuple[int, int, int]=(0, 255, 0),
        line_color:Tuple[int, int, int]=(0, 0, 255),
        diameter: int=6,
        line_width: int=3) -> np.ndarray:

        """Drawing custom landmarks

        image : numpy.ndarray,
        landmarks : mediapipe_landmarks.landmark,
        indices_to_avoid_nodes : the indices to avoid during drawing for the nodes,
        indices_to_avoid_edges : the indices to avoid during drawing for the edges,
        dot_color : the color of the nodes,
        line_color : the color of the edges,
        diameter : the diameter of the circle of the nodes,
        line_width : the width of the circle

        Returns:
            np.ndarray: The annotated image  
        """

        # TODO : draw a trivial edge as a hand to palm joint
        # TODO : Have to make compatible with multi landmarks, though it could be done explicitely

        height, width, _ = image.shape
        connection = list(connection)
        keypoints = []

        if landmarks:
            for idx, landmark in enumerate(landmarks):
                x, y = landmark

                x_px = int(min(math.floor(x * width), width - 1))
                y_px = int(min(math.floor(y * height), height - 1))
                keypoints.append((x_px, y_px))

                if indices_to_avoid_nodes is not None and idx in indices_to_avoid_nodes:
                    continue

                else:
                    cv2.circle(image, (int(x_px), int(y_px)), diameter, dot_color, -1)

            for inx, conn in enumerate(connection):
                from_ = conn[0]
                to_ = conn[1]
                if indices_to_avoid_edges is not None and from_ in indices_to_avoid_edges:
                    continue
                else:
                    if keypoints[from_] and keypoints[to_]:
                        cv2.line(image, keypoints[from_], keypoints[to_], line_color, line_width)
                    else:
                        continue
        return image 
