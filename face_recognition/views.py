import time
import glob

from PIL import Image
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView

from EfficientNet_dlib_face_recognition import efficient_net_face_recognition
from face_recognition.forms import ActorForm
from face_recognition.models import Actor


class ActorImageTV(TemplateView):
    form = ActorForm
    template_name = 'face_recognition/upload_image.html'

    def post(self, request, *args, **kwargs):
        form = ActorForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.name = f"image_{time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))}"
            obj.save()
            return HttpResponseRedirect(reverse_lazy('face_recognition:display', kwargs={'pk': obj.id}))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ActorImageTV, self).get_context_data(**kwargs)
        faces = glob.glob('static/images/face/*.jpg')
        context['faces'] = faces
        return context


class ActorDisplayDV(DetailView):
    model = Actor
    template_name = 'face_recognition/display_image.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super(ActorDisplayDV, self).get_context_data(**kwargs)
        image_path = Actor.objects.filter(name=context['actor'])[0].image
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
