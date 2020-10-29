import copy
import ssl

import cv2
import dlib
import torch
from efficientnet_pytorch import EfficientNet
from skimage import io
from skimage.transform import resize
from torchvision import transforms

# 리스트 순서는 알파벳 기준
labels = ['장혜진', '최우식', '정현준', '정이서', '정지소', '조여정', '이정은', '이선균', '박근록', '박명훈', '박소담', '송강호']


def efficient_net_face_recognition(image_path):
    """
    image_path 주소에서 파일을 가져와 학습된 Efficient-Net 모델의 입력 값으로 삽입하여
    검출한 얼굴의 위치가 기록된 사진, 입력 값에 맞게 잘린 검출된 얼굴, 인식 결과를 딕셔너리 형태로 반환합니다.
    Args:
        image_path (str): 이미지 URL

    Returns:
        dict: {'image': 검출한 얼굴의 위치가 기록된 이미지, 'face': 검출한 얼굴들의 리스트, 'result': 인식 결과}
    """
    path = image_path  # Image path

    # Efficient-Net
    model_name = 'efficientnet-b0'
    ssl._create_default_https_context = ssl._create_unverified_context
    model = EfficientNet.from_pretrained(model_name, num_classes=12)
    model.load_state_dict(torch.load('actor_model.pt', map_location=torch.device('cpu')))
    model.eval()

    face_detector = dlib.get_frontal_face_detector()
    original_image = io.imread(path)  # return: ndarray
    result_image = copy.copy(original_image)
    cropped_face, recognition_result = list(), list()
    loader = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                             std=[0.229, 0.224, 0.225])])

    detected_faces = face_detector(original_image)
    for i, face_rect in enumerate(detected_faces):
        """
        # 검출한 얼굴의 좌표. 테스트를 위해 사용되는 코드이며, 실제 사용시 반드시 주석 처리
        print("Face #{} found at Left: {} Top: {} Right: {} Bottom: {}"
              .format(i, face_rect.left(), face_rect.top(), face_rect.right(), face_rect.bottom()))
        """
        face = original_image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]
        cropped_face.append(face)
        result_image = cv2.rectangle(result_image,
                                     (face_rect.left(), face_rect.top()),  # x, y
                                     (face_rect.right(), face_rect.bottom()),  # x+w, y+h
                                     (255, 0, 0), 3)    # Red
        try:
            face = resize(face, (224, 224))
        except IndexError or ValueError:
            # 리사이징이 제대로 되지 않는 경우지만, 인식에 큰 문제는 없으므로 Error 처리를 따로 하지 않음
            pass
        else:
            face = image_loader(face, loader)

            # sigmoid 결과를 퍼센트로 변환
            sigmoid = torch.sigmoid(model(face)).tolist()[0]
            accuracy = [str(acc)[2:4] + '.' + str(acc)[4:7] if not int(str(acc)[0]) else "100.000" for acc in sigmoid]

            # 결과 값을 정확도를 기준으로 내림차순 정렬
            result = dict()
            for j, acc in enumerate(accuracy):
                result[labels[j]] = acc
            result = sorted(result.items(), reverse=True, key=lambda item: float(item[1]))
            recognition_result.append(result)

    return {"image": result_image, "face": cropped_face, "result": recognition_result}


def image_loader(resize_face, loader):
    """
    이미지를 Efficient-Net 입력 값에 맞게 차원 추가
    Args:
        resize_face: 차원 변환할 얼굴 사진
        loader: numpy 이미지에서 torch 이미지로 변경시켜주는 객체

    Returns:
        Tensor: Tensor 형태로 변환된 얼굴 사진

    """
    face_tensor = loader(resize_face).float()
    face_tensor = face_tensor.unsqueeze(0)
    return face_tensor
