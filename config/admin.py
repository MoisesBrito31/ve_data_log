from django.contrib import admin
from .models import Camera, Imagem

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display= ('nome','ip','porta_img','porta_dados','status')

@admin.register(Imagem)
class ImagemAdmin(admin.ModelAdmin):
    list_display=('camera','data','img')