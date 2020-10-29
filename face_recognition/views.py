import glob
import os
import time

from PIL import Image
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView

from EfficientNet_dlib_face_recognition import efficient_net_face_recognition
from face_recognition.forms import ActorForm
from face_recognition.models import Actor
from video_to_image import video_to_image


class ActorImageTV(TemplateView):
    form = ActorForm
    template_name = 'face_recognition/upload_image.html'

    def post(self, request, *args, **kwargs):
        form = ActorForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.name = f"media_{time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))}"
            file_format = str(obj.file).split(".")[1]
            if file_format in ['jpg', 'jpeg']:
                obj.save()
                return HttpResponseRedirect(reverse_lazy('face_recognition:image_display', kwargs={'pk': obj.id}))
            elif file_format in ['avi', 'mp4']:
                # 1) 영상 받아오기
                obj.save()
                video = str(Actor.objects.filter(id=obj.id)[0].file)
                video_path = f"media/{video}"
                directory = f"media/images/original/{video.split('.')[0]}"
                video_to_image(video_path, directory)
                return HttpResponseRedirect(reverse_lazy('face_recognition:video_display',
                                                         kwargs={'pk': obj.id, 'image_num': 1}))
            else:
                context = self.get_context_data(form=form, error_message="업로드한 파일은 지원하지 않는 포맷입니다.")
                return self.render_to_response(context)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ActorImageTV, self).get_context_data(**kwargs)
        faces = glob.glob('static/images/face/*.jpg')
        context['faces'] = faces
        return context


class ActorImageDisplayDV(DetailView):
    model = Actor
    template_name = 'face_recognition/display_image.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super(ActorImageDisplayDV, self).get_context_data(**kwargs)
        image_path = Actor.objects.filter(name=context['actor'])[0].file
        result_dict = efficient_net_face_recognition(image_path)

        # 결과 이미지를 Context에 저장
        result_image = Image.fromarray(result_dict['image'], 'RGB')
        result_image_path = f"/media/images/detected/detected_{str(image_path).split('/')[-1]}"
        result_image.save("." + result_image_path)

        # 얼굴 이미지를 Context에 저장
        face_list = list()
        for i, face in enumerate(result_dict['face']):
            face_image = Image.fromarray(face, 'RGB')
            face_path = f"/media/images/cropped/cropped_{i}_{str(image_path).split('/')[-1]}"
            face_image.save("." + face_path)
            face_list.append([face_path])

        context['detected_image'] = result_image_path
        if not face_list:
            context['zipped_result'] = None
        else:
            context['zipped_result'] = zip(face_list, result_dict['result'])
        return context


class ActorVideoDisplayDV(DetailView):
    model = Actor
    template_name = 'face_recognition/display_video.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super(ActorVideoDisplayDV, self).get_context_data(**kwargs)
        video = str(Actor.objects.filter(id=self.kwargs['pk'])[0].file)
        video_name = video.split("/")[1].split(".")[0]
        original_image_directory = f"media/images/original/{video.split('.')[0]}"
        context['image_num'] = int(self.kwargs['image_num'])
        context['max_length'] = len(next(os.walk(f"{original_image_directory}/"))[2])
        context['image'] = f"/{original_image_directory}/image_{self.kwargs['image_num']}.jpg"
        if not os.path.exists(f"media/images/detected/videos/{video_name}"):
            os.mkdir(f"media/images/detected/videos/{video_name}")  # for detected_image
            os.mkdir(f"media/images/cropped/videos/{video_name}")   # for cropped image

        result_dict = efficient_net_face_recognition("." + context['image'])

        # 결과 이미지를 Context에 저장
        result_image = Image.fromarray(result_dict['image'], 'RGB')
        result_image_path = f"/media/images/detected/videos/{video_name}/detected_{context['image_num']}.jpg"
        result_image.save("." + result_image_path)
        context['detected_image'] = result_image_path

        # 얼굴 이미지를 Context에 저장
        face_list = list()
        for i, face in enumerate(result_dict['face']):
            face_image = Image.fromarray(face, 'RGB')
            face_path = f"/media/images/cropped/videos/{video_name}/cropped_{context['image_num']}_{i}.jpg"
            face_image.save("." + face_path)
            face_list.append([face_path])

        context['detected_image'] = result_image_path
        if not face_list:
            context['zipped_result'] = None
        else:
            context['zipped_result'] = zip(face_list, result_dict['result'])
        return context
