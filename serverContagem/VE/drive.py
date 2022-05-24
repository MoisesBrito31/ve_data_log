import socket
from datetime import datetime
from time import sleep
import urllib.request
from PIL import Image

"""

drive que colata dados da camera VE, imagem e data no seguinte formato: XX,XX,XX,XX

"""

def gravaLog(ip="1",tipo="Evento", msg="", file="log_imagem.txt"):
    try:
        arquivo = open(file,'r')
        buffer = arquivo.read()
        arquivo.close()
    except:
        buffer = ""
    try:
        now = str(datetime.now())
        arquivoW = open(file,'w')
        arquivoW.write(f'{buffer}[{now}] - [{ip}] - [{tipo}] - {msg}\n\r')
        arquivoW.close()
    except:
        pass

class DriveImg():
    HEADERSIZE = 100
    ip = "192.168.0.1"
    port = 32200
    onLine = False

    def __init__(self, ip, port, pasta = "media/"):
        gravaLog(ip=self.ip,msg=f'iniciou drive')
        self.pasta = pasta
        self.ip=ip
        self.port = port
        self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.trans.connect((self.ip,self.port))
            self.onLine = True
        except:
            self.onLine = False 

    def read_img(self):
        resposta = 'Falha'
        try:
            if not self.onLine:
                #print(f'tentando Conectar camera {self.ip}...')
                gravaLog(ip=self.ip,msg=f'tentando Conectar...')
                sleep(2)
                try:
                    self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.trans.connect((self.ip,self.PORT))
                    self.onLine = True
                    gravaLog(ip=self.ip,msg=f'Conexão restabelecida!!')
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
                    gravaLog(ip=self.ip,tipo="Falha",msg=f'Falha de Sync - não retornou VE')
            except Exception as ex:
                self.onLine = False
                self.trans.close()
                sleep(2)
                gravaLog(ip=self.ip,tipo="Falha",msg=f'Falha de Sync - {str(ex)}')
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
                        #print(f'{len(ret)}b dados recebidos, total de: {len(data)+64}b')
                    else:
                        gravaLog(ip=self.ip,tipo="Falha",msg="falha durente recebimento da imagem")
                        self.onLine = False
                        return "falha durente recebimento da imagem"
                hoje = datetime.now()
                idcam = self.ip.split('.')
                try:
                    nomeFile = f'{hoje.day}{hoje.month}{hoje.year}-{idcam[3]}-{frame}'
                    if isJpeg==1:
                        file = open(f'{self.pasta}{nomeFile}.jpg','wb')
                        nomeFile = f'{nomeFile}.jpg'
                    else:
                        file = open(f'{self.pasta}{nomeFile}.bmp','wb')
                        nomeFile = f'{nomeFile}.bmp'
                    file.write(data)
                    file.close()
                except Exception as ex:
                    sleep(2)
                    gravaLog(ip=self.ip,tipo="Falha",msg=f'falha na gravação - {str(ex)}')
                    return "Falha"
                return nomeFile
        except Exception as ex:
            gravaLog(ip=self.ip,tipo="Falha Generica",msg=f'erro {str(ex)}')
            #print(f'erro {str(ex)}')
            self.onLine = False
            sleep(2)
            return resposta
    
    def readLive(self):
        idcam =self.ip.split('.')[3]
        try:
            urllib.request.urlretrieve(f'http://{self.ip}/sensor/liveimagewidth640height480.bmp', f'{self.pasta}{idcam}live.bmp')
            imagem = Image.open(f'{self.pasta}{idcam}live.bmp').convert("RGB")
            imagem.save(f'{self.pasta}{idcam}live.jpg')
            return f'{idcam}live.jpg'
        except Exception as ex:
            gravaLog(ip=self.ip,tipo="Falha readLive",msg=f'erro {str(ex)}')
            return "Falha"

class DriveData():
    HEADERSIZE = 100
    ip = "192.168.0.1"
    port = 32100
    onLine = False

    def __init__(self, ip, port):
        gravaLog(ip=self.ip,msg=f'iniciou drive',file="log_data.txt")
        self.ip=ip
        self.port = port
        self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.trans.connect((self.ip,self.port))
            self.onLine = True
        except:
            self.onLine = False 

    def read_data(self):
        resposta = 'falha'
        try:
            if not self.onLine:
                #print(f'tentando Conectar...\n')
                gravaLog(ip=self.ip,msg=f'tentando Conectar...',file="log_data.txt")
                sleep(2)
                try:
                    self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.trans.connect((self.ip,self.PORT))
                    self.onLine = True
                    gravaLog(ip=self.ip,msg=f'Conexão restabelecida...',file="log_data.txt")
                except:
                    self.onLine = False
                    return resposta
            resposta = self.trans.recv(self.HEADERSIZE).decode("utf-8")
            resposta = str(resposta).split(',')
            return resposta
        except Exception as ex:
            self.onLine = False 
            gravaLog(ip=self.ip,tipo="Falha Generica",msg=f'erro {str(ex)}',file="log_data.txt")
            sleep(2)
            return resposta

   