import cv2
import dlib
import torch
from efficientnet_pytorch import EfficientNet
from skimage import io
from skimage.transform import resize
from torchvision import transforms

labels = ['Chang_Hyejin', 'Choei_Usik', 'Jeong_Hyeonjun', 'Jeong_Iseo', 'Jeong_Jiso',
              'Jo_Yeojeong', 'Lee_Jeongeun', 'Lee_Seongyun', 'Park_Geunrok', 'Park_Myeonghun',
              'Park_Sodam', 'Song_Gangho']


def efficient_net_face_recognition(image_path):
    path = image_path   # Image path

    # Efficient-Net
    model_name = 'efficientnet-b0'
    model = EfficientNet.from_pretrained(model_name, num_classes=12)
    model.load_state_dict(torch.load('actor_model.pt', map_location=torch.device('cpu')))
    loader = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                             std=[0.229, 0.224, 0.225])])
    model.eval()

    # Face Detect
    face_detector = dlib.get_frontal_face_detector()
    image = io.imread(path)    # return: ndarray
    detected_faces = face_detector(image)
    for i, face_rect in enumerate(detected_faces):
        print("Face #{} found at Left: {} Top: {} Right: {} Bottom: {}"
              .format(i, face_rect.left(), face_rect.top(), face_rect.right(), face_rect.bottom()))
        face_detect_image = cv2.rectangle(image,
                                          (face_rect.left(), face_rect.top()),      # x, y
                                          (face_rect.right(), face_rect.bottom()),   # x+w, y+h
                                          (255, 0, 0), 5)
        face = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]
        try:
            face = resize(face, (224, 224))
        except IndexError or ValueError:
            pass
        else:
            # Face Recognition
            face = image_loader(face, loader)
            sigmoid = torch.sigmoid(model(face)).tolist()[0]
            accuracy = [str(acc)[0:7] for acc in sigmoid]
            result = dict()
            for j, acc in enumerate(accuracy):
                result[labels[j]] = acc
            result = sorted(result.items(), reverse=True, key=lambda item: item[1])
            return {"image": face_detect_image, "result": result}
            # _, output = torch.max(model(face), 1)
            # print(labels[output.item()])    # Result


def image_loader(resize_face, loader):
    face_tensor = loader(resize_face).float()
    face_tensor = face_tensor.unsqueeze(0)
    return face_tensor
