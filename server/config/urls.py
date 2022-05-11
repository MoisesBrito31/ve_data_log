from django.urls import path
from .views import CameraView, CameraIndexView, HistoricoView
from .views import CameraJson, CamerasJson, CameraZera, ImageView
from .views import CameraVisionCall

urlpatterns = [
    path('', CameraView.as_view(), name='cameras'),
    path('camerazerar/', CameraZera.as_view(), name='camera_zerar'),
    path('index/<int:valor>/', CameraIndexView.as_view(), name='cameras_index'),  
    path('hist/<int:valor>/', HistoricoView.as_view(), name='historico'),
    path('camerajson/<int:valor>/', CameraJson.as_view()),
    path('image/<int:valor>/', ImageView.as_view(), name = "image"),
    path('camerasjson/',CamerasJson.as_view()),
    path('visionmanage/',CameraVisionCall.as_view())
]