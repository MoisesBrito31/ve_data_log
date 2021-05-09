from django.urls import path
from .views import CameraView, CameraIndexView, HistoricoView
from .views import CameraJson, CamerasJson


urlpatterns = [
    path('', CameraView.as_view(), name='cameras'),
    path('index/<int:valor>/', CameraIndexView.as_view(), name='cameras_index'),  
    path('hist/<int:valor>/', HistoricoView.as_view(), name='historico'),
    path('camerajson/<int:valor>/', CameraJson.as_view()),
    path('camerasjson/',CamerasJson.as_view())
]