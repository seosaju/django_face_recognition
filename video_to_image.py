import os

import cv2


def video_to_image(video_path, directory):
    video = cv2.VideoCapture(video_path)
    dirname = str(directory).split("/")[4]
    os.mkdir(f"media/images/original/videos/{dirname}")

    def get_frame(sec):
        video.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        has_frames, image = video.read()
        if has_frames:
            cv2.imwrite(f"{directory}/image_{str(count)}.jpg", image)     # save frame as JPG file
        return has_frames

    second = 0
    frame_rate = 5  # it will capture image in each 5 second
    count = 1
    frame = get_frame(second)
    while frame:
        count = count + 1
        second = second + frame_rate
        second = round(second, 2)
        frame = get_frame(second)
