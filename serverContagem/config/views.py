from django.shortcuts import render, HttpResponse
from django.views.generic import View
from core.views import logado, UserPermission
from datetime import datetime, timedelta
from .models import Camera, Imagem
from .drive import *
from .ve_cont_garrafas import *
from .ve_cont_garrafas import camera as zerarfunc
from threading import Thread
from django.db.models import Q
from pyModbusTCP.client import ModbusClient as Modbus



class CameraZera(View):
    def get(self,request):
        try:
            zerarfunc.zerar()
            return HttpResponse('ok')
        except Exception as ex:
            print(f'falha em zerar... - {str(ex)}')
            return HttpResponse(f'falha - {str(ex)}')

class CameraView(View):
    def get(self,request):
        dados = Camera.objects.all()
        return logado('config/cameras/view.html',request,dados=dados,titulo='Cameras',nivel_min=1)

class CameraJson(View):
    def get(self,request,valor):
        dados = Camera.objects.get(id=valor)
        if UserPermission(request,nivel_min=2):
            percentFaltantes = str(dados.faltantes/(dados.garrafas+dados.faltantes)*100)[:5]
            percentCaixas = str(dados.reprovado/(dados.aprovado+dados.reprovado)*100)[:5]
            ret = f'{{\"img\":\"{dados.img}\",\"faltantes\":{dados.faltantes},\"total\":{dados.garrafas},\"aprovado\":{dados.aprovado},\"reprovado\":{dados.reprovado},\"percGarrafa\":{percentFaltantes},\"perCaixa\":{percentCaixas}}}'
            return HttpResponse(ret)
        else:
            return HttpResponse('falha')

class CamerasJson(View):
    def get(self,request):
        dados = Camera.objects.all()
        ret = '['
        if UserPermission(request,nivel_min=2):
            for c in dados:
                ret = f'{ret}{{\"id\":{c.id},\"status\":\"{c.status}\",\"faltantes\":{c.faltantes},\"total\":{c.garrafas},\"aprovado\":{c.aprovado},\"reprovado\":{c.reprovado}}},'
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
            hora = int(h.data.hour)-3
            if hora<0:
                hora+=23             
            h.data = f'{hora}:{h.data.minute} {h.data.day}/{h.data.month}/{h.data.year}'
        for hf in dadof:
            hora = int(hf.data.hour) -3
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
        ini = ini + timedelta(hours=3)
        fim = datetime(int(fims[0:4]),int(fims[5:7]),int(fims[8:10]),int(fims[11:13]),int(fims[14:16]),0)
        fim = fim + timedelta(hours=3)
        cam = Camera.objects.get(id=valor)
        dado = Imagem.objects.filter(Q(camera__exact=cam) & Q(data__gt=ini) & Q(data__lt=fim)).order_by('data')
        dadof = Imagem.objects.filter(Q(camera__exact=cam) & Q(data__gt=ini) & Q(data__lt=fim)).order_by('data')
        for h in dado:      
            hora = int(h.data.hour) -3
            if hora<0:
                hora+=23             
            h.data = f'{hora}:{h.data.minute} {h.data.day}/{h.data.month}/{h.data.year}'
        for hf in dadof:
            hora = int(hf.data.hour) -3
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
                        



class ImageView(View):
    def get(self,request,valor):
        dados = Imagem.objects.get(id=valor)
        return logado('config/cameras/image.html',request,dados=dados,titulo='Imagem',nivel_min=1)
