import time

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView

from face_recognition.forms import ActorForm
from face_recognition.models import Actor


class ActorImageTV(TemplateView):
    form = ActorForm
    template_name = 'face_recognition/upload_image.html'

    def post(self, request, *args, **kwargs):
        form = ActorForm(request.POST, request.FILES)
        if form.is_valid():
            today = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
            form.name = f'image_{today}'
            obj = form.save()
            return HttpResponseRedirect(reverse_lazy('face_recognition:display', kwargs={'pk': obj.id}))
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActorDisplayDV(DetailView):
    model = Actor
    template_name = 'face_recognition/show_image.html'
    context_object_name = 'actor'
