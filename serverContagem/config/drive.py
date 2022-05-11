import socket, threading
import os
from datetime import datetime, timedelta
from time import sleep
from threading import Thread
from .models import Camera, Imagem
from .ve_cont_garrafas import camera as Contagem
import subprocess

fim_Programa = threading.Event()

def atualizaRelogio():
    while not fim_Programa.is_set():
        sleep(10)
        try:
            arquivo = open("relogio.txt","w")
            a = subprocess.check_output(['sudo','date','+%m%d%H%M%Y'])
            arquivo.write(str(a[:12]))
            arquivo.close()
        except:
            pass

def gravaLog(tipo="Evento", msg="", file="log_imagem.txt"):
    try:
        arquivo = open(file,'r')
        buffer = arquivo.read()
        arquivo.close()
    except:
        buffer = ""
    try:
        now = str(datetime.now())
        arquivoW = open(file,'w')
        arquivoW.write(f'{buffer}[{now}] - [{tipo}] - {msg}\n\r')
        arquivoW.close()
    except:
        pass

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
                print(f'tentando Conectar camera {self.IP}...')
                gravaLog(msg=f'tentando Conectar...')
                sleep(2)
                try:
                    self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.trans.connect((self.IP,self.PORT))
                    self.onLine = True
                    gravaLog(msg=f'Conexão restabelecida!!')
                except:
                    self.onLine = False
                    return resposta
            ret = self.trans.recv(64)
            try:
                valida = str(ret[0:15].decode('UTF-8'))
                if valida.find("VE")<0:
                    self.onLine = False
                    self.trans.close()
                    sleep(2)
                    gravaLog(tipo="Falha",msg=f'Falha de Sync - não retornou VE')
            except Exception as ex:
                self.onLine = False
                self.trans.close()
                sleep(2)
                gravaLog(tipo="Falha",msg=f'Falha de Sync - {str(ex)}')
                return "Falha de Sync"
            if ret:
                frame = int.from_bytes(ret[24:27],"little")
                isJpeg = int.from_bytes(ret[32:33],"little")
                img_size = int.from_bytes(ret[20:23],"little")
                data = self.trans.recv(5000)
                while img_size>len(data) and ret:
                    ret = self.trans.recv(10000)
                    if ret:
                        data = data+ret
                        print(f'{len(ret)}b dados recebidos, total de: {len(data)+64}b')
                    else:
                        gravaLog(tipo="Falha",msg="falha durente recebimento da imagem")
                        self.onLine = False
                        return "falha durente recebimento da imagem"
                hoje = datetime.now()
                idcam = self.IP.split('.')
                try:
                    nomeFile = f'{hoje.day}{hoje.month}{hoje.year}-{idcam[3]}-{frame}'
                    if isJpeg==1:
                        file = open(f'media/{nomeFile}.jpg','wb')
                        nomeFile = f'{nomeFile}.jpg'
                    else:
                        file = open(f'media/{nomeFile}.bmp','wb')
                        nomeFile = f'{nomeFile}.bmp'
                    file.write(data)
                    file.close()
                    #gravaLog(msg=f'tamnho do arquivo: {len(data)} bytes')
                    #print(f'tamnho do arquivo: {len(data)} bytes')
                    if len(data)>65:
                        cam = Camera.objects.get(ip=self.IP)
                        arq = Imagem(camera=cam,data=datetime.now(),img=f'media/{nomeFile}',garrafas=Contagem.lastValue)
                        cam.img = f'media/{nomeFile}'
                        cam.save()
                        arq.save()
                        #gravaLog(msg=f'Salvou image {nomeFile}')
                        resposta = f'Salvou image {nomeFile}'
                        self.onLine = True
                        return resposta
                    else:
                        gravaLog(tipo="Falha",msg=f'falha no processamento da img - len(data):{len(data)}')
                        return "Falha"
                except Exception as ex:
                    sleep(2)
                    gravaLog(tipo="Falha",msg=f'falha na gravação - {str(ex)}')
                    return f'falha na gravação - {str(ex)}'
            else:
                gravaLog(tipo="Falha",msg="retorno da imagem veio nula")
                self.onLine = False
                sleep(2)
                return "falha"
        except Exception as ex:
            gravaLog(tipo="Falha Generica",msg=f'erro {str(ex)}')
            print(f'erro {str(ex)}')
            self.onLine = False
            cam = Camera.objects.get(ip=self.IP)
            cam.save()
            sleep(2)
            return resposta

def c1_img_loop(cam):
    print(f'iniciou camera {cam.IP}')
    while not fim_Programa.is_set():
        print(cam.read_img())

def mainCicle():
    gravaLog(msg='iniciou imagem...')
    print('iniciou drive...')
    cameras = []
    thrs = []
    camQuery = Camera.objects.all()
    for c in camQuery:
        camera = Protocol(c.ip,c.porta_img)
        thrs.append(Thread(target=c1_img_loop,args=(camera,)))
    for t in thrs:
        t.start()
    t_relogio = threading.Thread(target=atualizaRelogio).start()
    while not fim_Programa.is_set():
        cmd = input()
        if cmd == "end":
            fim_Programa.set()
        else:
            print("comando inexistente")
    print("fim do programa")

try:
    fi = open("relogio.txt","r")
    valor = str(fi.read())[2:14]
    print(valor)
    comando = subprocess.check_output(['sudo','date',valor])
    fi.close()
    print(f'retorno do relogio: {comando}')
except Exception as ex:
    print(f'falha em set do relogio: {str(ex)}')

t_main = threading.Thread(target=mainCicle).start()



    
   



    
