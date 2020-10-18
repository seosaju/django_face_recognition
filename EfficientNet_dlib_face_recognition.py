import copy

import cv2
import dlib
import torch
from efficientnet_pytorch import EfficientNet
from skimage import io
from skimage.transform import resize
from torchvision import transforms

labels = ['장혜진', '최우식', '정현준', '정이서', '정지소', '조여정', '이정은', '이선균', '박근록', '박명훈', '박소담', '송강호']


def efficient_net_face_recognition(image_path):
    path = image_path  # Image path

    # Efficient-Net
    model_name = 'efficientnet-b0'
    model = EfficientNet.from_pretrained(model_name, num_classes=12)
    model.load_state_dict(torch.load('actor_model.pt', map_location=torch.device('cpu')))
    loader = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                             std=[0.229, 0.224, 0.225])])
    model.eval()

    # Face Detect
    face_detector = dlib.get_frontal_face_detector()
    original_image = io.imread(path)  # return: ndarray
    result_image = copy.copy(original_image)
    cropped_face, recognition_result = list(), list()
    detected_faces = face_detector(original_image)
    for i, face_rect in enumerate(detected_faces):
        print("Face #{} found at Left: {} Top: {} Right: {} Bottom: {}"
              .format(i, face_rect.left(), face_rect.top(), face_rect.right(), face_rect.bottom()))
        face = original_image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]
        cropped_face.append(face)
        result_image = cv2.rectangle(result_image,
                                     (face_rect.left(), face_rect.top()),  # x, y
                                     (face_rect.right(), face_rect.bottom()),  # x+w, y+h
                                     (255, 0, 0), 3)
        try:
            face = resize(face, (224, 224))
        except IndexError or ValueError:
            pass
        else:
            # Face Recognition
            face = image_loader(face, loader)
            sigmoid = torch.sigmoid(model(face)).tolist()[0]
            accuracy = [str(acc)[2:4] + '.' + str(acc)[4:7] if not int(str(acc)[0]) else "100.000" for acc in sigmoid]
            result = dict()
            for j, acc in enumerate(accuracy):
                result[labels[j]] = acc
            result = sorted(result.items(), reverse=True, key=lambda item: float(item[1]))
            recognition_result.append(result)
    return {"image": result_image, "face": cropped_face, "result": recognition_result}


def image_loader(resize_face, loader):
    face_tensor = loader(resize_face).float()
    face_tensor = face_tensor.unsqueeze(0)
    return face_tensor
