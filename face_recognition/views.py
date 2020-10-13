import time

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


class ActorDisplayDV(DetailView):
    model = Actor
    template_name = 'face_recognition/display_image.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super(ActorDisplayDV, self).get_context_data(**kwargs)
        image_path = Actor.objects.filter(name=context['actor'])[0].image
        result_dict = efficient_net_face_recognition(image_path)
        result_image = Image.fromarray(result_dict['image'], 'RGB')
        result_image_path = f"/media/images/detected/detected_{str(image_path).split('/')[-1]}"
        result_image.save("." + result_image_path)
        context['face_detect_image'] = result_image_path
        context['result'] = result_dict['result']
        return context
