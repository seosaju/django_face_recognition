from django.urls import path
from face_recognition import views

app_name = 'face_recognition'

urlpatterns = [
    path('', views.ActorImageTV.as_view(), name='index'),
    path('actor/image/<int:pk>', views.ActorImageDisplayDV.as_view(), name='image_display'),
    path('actor/video/<int:pk>/<int:image_num>', views.ActorVideoDisplayDV.as_view(), name='video_display'),
]
