import asyncore, socket, threading
import urllib.request
import os
from PIL import Image
import sys
from time import sleep
from datetime import datetime
from .models import Camera, Imagem
from pyModbusTCP.client import ModbusClient as Modbus
from .ve_cont_garrafas import camera as Contagem

evento_conectado = [threading.Event(),threading.Event()]
fim_arquivo = [threading.Event(),threading.Event()]
fim_Programa = threading.Event()
client = []



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


class CameraInfo():
    def __init__(self,ip,id,imgPort=32200,dataPort=32100):
        self.ip = ip
        self.id = id
        self.imgPort = imgPort
        self.dataPort = dataPort

class ImagerHeadler(asyncore.dispatcher):

    def __init__(self,host, port, index):
        self.ip = host
        self.index = index
        fim_arquivo[index].set()
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.connect((host,port))
        self.contador = 0
        self.isJpeg = 0
        self.frame = 0
        self.img_size =0
        self.buffer = b''

    def processaBuffer(self,data,index):
        fim_arquivo[self.index].clear()
        if index == 1:
            self.frame = int.from_bytes(data[24:27],"little")
            self.isJpeg = int.from_bytes(data[32:33],"little")
            self.img_size = int.from_bytes(data[20:23],"little")
            print(f"frame: {self.frame}, isJpeg: {self.isJpeg}, img_size: {self.img_size}")
            if self.isJpeg > 1 or self.img_size == 0:
                self.buffer = b''
                self.contador = 0
        else:
            self.buffer = self.buffer + data
            print(f"recebeu pacote de {len(data)} bytes, arquivo com {len(self.buffer)} bytes")
            if len(self.buffer) >= self.img_size:
                self.salvaImg(self.buffer,self.frame,self.isJpeg)
                self.buffer = b''
                self.contador = 0
        fim_arquivo[self.index].set()

    def handle_read(self):
        fim_arquivo[self.index].wait(1)
        if self.contador == 0:
            ret = self.recv(64)
        else:
            ret = self.recv(1024)
        self.contador += 1
        self.processaBuffer(ret,self.contador)

    def handle_connect(self):
        print("conectou")
        evento_conectado[self.index].set()
        return super().handle_connect()

    def salvaImg(self,data,frame,isJpeg):
        print("chamou salvaImg")
        hoje = datetime.now()
        idcam = self.ip.split('.')
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
            gravaLog(msg=f'tamnho do arquivo: {len(data)} bytes')
            cam = Camera.objects.get(ip=self.ip)
            arq = Imagem(camera=cam,data=datetime.now(),img=f'media/{nomeFile}',garrafas=Contagem.lastValue)
            cam.img = f'media/{nomeFile}'
            cam.save()
            arq.save()
            gravaLog(msg=f'Salvou image {nomeFile}')
            resposta = f'Salvou image {nomeFile}'
            self.onLine = True
            return resposta
        except Exception as ex:
            self.onLine = False
            gravaLog(tipo="Falha",msg=f'falha na gravação - {str(ex)}')
            return f'falha na gravação - {str(ex)}'

    def handle_close(self):
        print("desconectou")
        evento_conectado[self.index].clear()
        self.close()

class DataHandler(asyncore.dispatcher):

    def __init__(self,host,port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connect((host,port))
        self.buffer = b''

    def handle_read(self):
        print(f'recebeu: {self.recv(20)}')       

    def handle_connect(self):
        print("conectou")
        return super().handle_connect()

    def handle_close(self):
        print("desconectou")
        self.close()

class ModbusHandler():
    def __init__(self,ip="192.168.0.1",port=502):
        self.aprovados = 0
        self.reprovados =0
        self.IP = ip
        self.port = port
        self.Protocolo = Modbus(port=self.port,host=self.IP)
        try:
            self.Protocolo.open()
        except Exception as ex:
            gravaLog("Erro",f"Não foi possível conectar ao modbus: {str(ex)} ",file="modbusLog.txt")
    def read(self,address,quantity):
        try:
            return self.Protocolo.read_input_registers(address,quantity)
        except Exception as ex:
            gravaLog("Erro",f"Não foi possível ler do modbus: {str(ex)} ",file="modbusLog.txt")
    def reconecta(self):
        sleep(5)
        try:
            self.Protocolo = Modbus(port=self.port,host=self.IP)
            self.Protocolo.open()
            return True
        except Exception as ex:
            gravaLog("Erro",f"Não foi possível conectar ao modbus: {str(ex)} ",file="modbusLog.txt")
            return False

def ciclo_reconect(cameras):
    for c in cameras:
        print("conectando na camera {}".format(c.ip))
        client.append(ImagerHeadler(c.ip,c.imgPort,c.id))
    asyncore.loop() 
    while not fim_Programa.is_set():
        for c in cameras:
            if not evento_conectado[c.id].is_set():
                print("reconectando... camera {}".format(c.ip))
                sleep(1)
                client.append(ImagerHeadler(c.ip,c.imgPort,c.id))
                asyncore.loop()  

def data_loop(cm_mod):
    while not fim_Programa.is_set():
        valor =cm_mod.read(8,4)
        if not valor == None:
            aprovados = valor[0]+valor[1]*65536
            reprovados = valor[2]+valor[3]*65536
            cm_mod.aprovados = aprovados
            cm_mod.reprovados = reprovados
            """
            try:
                cam = Camera.objects.get(ip=cm_mod.IP)
                cam.reprovado = reprovados
                cam.aprovado = aprovados
                cam.save()
            except:
                pass
        """
        else:
            #print('camera OffLine')
            try:
                cm_mod.reconecta()
            except:
                pass
        sleep(1)

def banco_loop(cms_mod):
    while not fim_Programa.is_set():
        for c in cms_mod:
            try:
                cam = Camera.objects.get(ip=c.IP)
                cam.reprovado = c.reprovados
                cam.aprovado = c.aprovados
                cam.save()
                sleep(0.5)
            except:
                pass

def readLive(cameras):
    while not fim_Programa.is_set():
        sleep(2)
        for c in cameras:
            idcam =c.ip.split('.')[3]
            try:
                urllib.request.urlretrieve(f'http://{c.ip}/sensor/liveimagewidth640height480.bmp', f'media/{idcam}live.bmp')
                imagem = Image.open(f'media/{idcam}live.bmp').convert("RGB")
                imagem.save(f'media/{idcam}live.jpg')
                print(f"Imagem salva camera {c.ip}")
            except:
                erro = sys.exc_info()
                print("Ocorreu um erro:", erro)

def main_ciclo():
    print("Inicio do Programa")
    sleep(10)
    c1 = CameraInfo("192.168.0.10",0)
    t_receiveImg = threading.Thread(target=ciclo_reconect, args=([c1],)).start()
    while not fim_Programa.is_set():
        cmd = input()
        if cmd == "end":
            fim_Programa.set()
            asyncore.close_all()
        else:
            print("comando inexistente")
    print("fim do programa")
        
t_cliclo_main = threading.Thread(target=main_ciclo)
t_cliclo_main.start()


