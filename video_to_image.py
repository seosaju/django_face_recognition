import os

import cv2
import dlib


def video_to_image(video_path, directory):
    video = cv2.VideoCapture(video_path)
    face_detector = dlib.get_frontal_face_detector()
    dirname = str(directory).split("/")[4]
    os.mkdir(f"media/images/original/videos/{dirname}")

    def get_frame(sec):
        video.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        has_frames, image = video.read()
        nonlocal i
        try:
            detected_face = face_detector(image)
        except TypeError:
            return
        else:
            if list(detected_face):
                cv2.imwrite(f"{directory}/image_{str(i)}.jpg", image)     # save frame as JPG file
                i = i + 1
        return has_frames

    second = 0
    frame_rate = 3  # it will capture image in each 3 second
    i = 1
    frame = get_frame(second)
    while frame:
        second = second + frame_rate
        second = round(second, 2)
        frame = get_frame(second)
