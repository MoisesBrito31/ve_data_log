import socket
import os
from datetime import datetime, timedelta
from time import sleep
from .models import Camera, Imagem


class Protocol():
    HEADERSIZE = 100
    IP = "192.168.0.1"
    PORT = 32200
    onLine = False

    def __init__(self, ip, port):
        self.IP=ip
        self.PORT = port
        self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.trans.connect((self.IP,self.PORT))
            self.onLine = True
        except:
            self.onLine = False 

    def read_data(self):
        resposta = 'falha'
        try:
            if not self.onLine:
                print(f'tentando Conectar...\n')
                sleep(2)
                try:
                    self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.trans.connect((self.IP,self.PORT))
                    self.onLine = True
                except:
                    self.onLine = False
                    return resposta
            resposta = self.trans.recv(self.HEADERSIZE).decode("utf-8")
            dados_arrey = str(resposta).split(',')
            cam = Camera.objects.get(ip=self.IP)
            cam.status= 'Online'
            cam.reprovado = dados_arrey[4]
            cam.aprovado = dados_arrey[3]
            cam.save()
            return resposta
        except:
            cam = Camera.objects.get(ip=self.IP)
            cam.status= 'Offline'
            cam.save()
            self.onLine = False 
            return resposta

    def read_img(self):
        resposta = 'falha'
        try:
            if not self.onLine:
                print(f'tentando Conectar...\n')
                sleep(2)
                try:
                    self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.trans.connect((self.IP,self.PORT))
                    self.onLine = True
                except:
                    self.onLine = False
                    return resposta
            ret = self.trans.recv(64)
            frame = int.from_bytes(ret[24:27],"little")
            isJpeg = int.from_bytes(ret[32:33],"little")
            img_size = int.from_bytes(ret[20:23],"little")
            data = self.trans.recv(2048)
            while img_size>len(data):
                ret = self.trans.recv(2048)
                data = data+ret

            hoje = datetime.now()
            idcam = self.IP.split('.')
            nomeFile = f'{hoje.day}{hoje.month}{hoje.year}-{idcam[3]}-{frame}'
            if isJpeg==1:
                file = open(f'media\{nomeFile}.jpg','wb')
                nomeFile = f'{nomeFile}.jpg'
            else:
                file = open(f'media\{nomeFile}.bmp','wb')
                nomeFile = f'{nomeFile}.bmp'
            file.write(data)
            file.close()
            print(f'tamnho do arquivo: {len(data)} bytes')
            if len(data)>0:
                cam = Camera.objects.get(ip=self.IP)
                arq = Imagem(camera=cam,data=datetime.now(),img=f'media/{nomeFile}')
                cam.status = 'Online'
                cam.img = f'media/{nomeFile}'
                cam.save()
                arq.save()
            resposta = f'Salvou image {nomeFile}'
            return resposta
        except Exception as ex:
            print(f'erro {str(ex)}')
            self.onLine = False
            cam = Camera.objects.get(ip=self.IP)
            cam.status = 'Offline'
            cam.save()
            return resposta


    
   



    
