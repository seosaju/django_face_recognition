from django.urls import path
from face_recognition import views

app_name = 'face_recognition'

urlpatterns = [
    path('', views.ActorImageTV.as_view(), name='index'),
    path('actor/<int:pk>', views.ActorDisplayDV.as_view(), name='display'),
]
