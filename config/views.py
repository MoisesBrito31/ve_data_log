from django.shortcuts import render, HttpResponse
from django.views.generic import View
from core.views import logado, UserPermission
from datetime import datetime, timedelta
from .models import Camera, Imagem
from .drive import Protocol
from threading import Thread
from django.db.models import Q

#"""
c1_img=Protocol('192.168.0.1',32200)
c1_data = Protocol('192.168.0.1',32100)
def c1_img_loop():
    while True:
        print(c1_img.read_img())

def c1_data_loop():
    while True:
        c1_data.read_data()

c1_img_thr = Thread(target=c1_img_loop)
c1_img_thr.start()

c1_data_thr = Thread(target=c1_data_loop)
c1_data_thr.start()
#"""


class CameraView(View):
    def get(self,request):
        dados = Camera.objects.all()
        return logado('config/cameras/view.html',request,dados=dados,titulo='Cameras',nivel_min=1)

class CameraJson(View):
    def get(self,request,valor):
        dados = Camera.objects.get(id=valor)
        if UserPermission(request,nivel_min=2):
            ret = f'{{\"img\":\"{dados.img}\",\"aprovado\":{dados.aprovado},\"reprovado\":{dados.reprovado}}}'
            return HttpResponse(ret)
        else:
            return HttpResponse('falha')

class CamerasJson(View):
    def get(self,request):
        dados = Camera.objects.all()
        ret = '['
        if UserPermission(request,nivel_min=2):
            for c in dados:
                ret = f'{ret}{{\"id\":{c.id},\"status\":\"{c.status}\",\"aprovado\":{c.aprovado},\"reprovado\":{c.reprovado}}},'
            ret = ret[:len(ret)-1]+']'
            return HttpResponse(ret)
        else:
            return HttpResponse('falha')

class CameraIndexView(View):
    def get(self,request,valor):
        cam = Camera.objects.get(id=valor)
        return logado('config/cameras/camera.html',request,dados=cam,titulo='Cameras Index',nivel_min=1)

class HistoricoView(View):
    def get(self,request,valor):
        ago = datetime.now()
        ini = datetime(ago.year,ago.month,ago.day,0,0,0)
        inis = f'{ago.year}-{ago.month}-{ago.day}T00:00:00'
        fim = datetime(ago.year,ago.month,ago.day,23,59,0)
        fims = f'{ago.year}-{ago.month}-{ago.day}T23:59:00'
        cam = Camera.objects.get(id=valor)
        dado = Imagem.objects.filter(Q(camera__exact=cam) & Q(data__gt=ini) & Q(data__lt=fim)).order_by('data')
        dadof = Imagem.objects.filter(Q(camera__exact=cam) & Q(data__gt=ini) & Q(data__lt=fim)).order_by('data')
        for h in dado:      
            hora = int(h.data.hour) 
            if hora<0:
                hora+=23             
            h.data = f'{hora}:{h.data.minute} {h.data.day}/{h.data.month}/{h.data.year}'
        for hf in dadof:
            hora = int(hf.data.hour) 
            if hora<0:
                hora+=23       
            hf.data = f'{hora}:{hf.data.minute} {hf.data.day}/{hf.data.month}/{hf.data.year}'
        return logado('config/cameras/historico.html',request,titulo=f'historico {cam.nome}',
                        context={
                            'camera_nome': cam.nome,
                            'cameraID': valor,
                            'dadosf':dadof,
                            'ini': inis,
                            'fim': fims
                        },dados=dado,nivel_min=2)
    def post(self,request,valor):
        inis = str(request.POST['ini'])
        fims = str(request.POST['fim'])
        ini = datetime(int(inis[0:4]),int(inis[5:7]),int(inis[8:10]),int(inis[11:13]),int(inis[14:16]),0)
        fim = datetime(int(fims[0:4]),int(fims[5:7]),int(fims[8:10]),int(fims[11:13]),int(fims[14:16]),0)
        cam = Camera.objects.get(id=valor)
        dado = Imagem.objects.filter(Q(camera__exact=cam) & Q(data__gt=ini) & Q(data__lt=fim)).order_by('data')
        dadof = Imagem.objects.filter(Q(camera__exact=cam) & Q(data__gt=ini) & Q(data__lt=fim)).order_by('data')
        for h in dado:      
            hora = int(h.data.hour) 
            if hora<0:
                hora+=23             
            h.data = f'{hora}:{h.data.minute} {h.data.day}/{h.data.month}/{h.data.year}'
        for hf in dadof:
            hora = int(hf.data.hour)
            if hora<0:
                hora+=23       
            hf.data = f'{hora}:{hf.data.minute} {hf.data.day}/{hf.data.month}/{hf.data.year}'
        return logado('config/cameras/historico.html',request,titulo=f'historico {cam.nome}',
                        context={
                            'camera_nome': cam.nome,
                            'cameraID': valor,
                            'dadosf':dadof,
                            'ini': inis,
                            'fim': fims
                        },dados=dado,nivel_min=2)

