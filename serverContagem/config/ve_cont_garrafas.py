import socket
from datetime import datetime
from time import sleep
from threading import Thread
from pyModbusTCP.server import DataBank, ModbusServer
from .models import Camera


def gravaLog(tipo="Evento", msg="", file="log_contagem.txt"):
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
    faltantes = 0
    contagem = 0
    aprovados = 0
    reprovados = 0
    def __init__(self, ip, port,faltantes=0,contagem=0,aprovados=0,reprovados=0):
        self.lastValue = 0
        self.faltantes = faltantes
        self.contagem = contagem
        self.aprovados = aprovados
        self.reprovados = reprovados
        self.IP=ip
        self.PORT = port
        self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.trans.connect((self.IP,self.PORT))
            self.onLine = True
        except:
            self.onLine = False 

    def read_data(self):
        try:
            if not self.onLine:
                gravaLog(msg="tentando se conectar...")
                sleep(2)
                try:
                    self.trans = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.trans.connect((self.IP,self.PORT))
                    self.onLine = True
                    gravaLog(msg="Conexão Restabelecida!!")
                except:
                    self.onLine = False
                    return "falha"
            resposta = self.trans.recv(self.HEADERSIZE).decode("utf-8")
            if not resposta:
                gravaLog(tipo="Falha de Recepção",msg=f'resposta = {resposta}')
                self.onLine = False
                return "falha"
            try:
                dados_arrey = str(resposta).split(',')
                print(f'dados_Arrey= {len(dados_arrey)}')
                if len(dados_arrey)==5:
                    valorContagem = int(dados_arrey[0])
                    if 24-valorContagem > 24:
                        valorContagem = 24
                    self.lastValue = 24-valorContagem
                    self.faltantes+= valorContagem
                    self.contagem+= 24-valorContagem
                    if valorContagem>0:
                        self.reprovados+=1    
                    else:
                        self.aprovados+=1
                    self.onLine = True
                    return dados_arrey
                else:
                    gravaLog(tipo="Falha recepção",msg=f'formatação do arrey errada - {dados_arrey}')
                    return "falha na formatação do arrey"
            except Exception as ex:
                gravaLog(tipo="Falha ao analisar resposta",msg=f'resposta = {resposta}, msg = {str(ex)}')
                return "Falha"
        except Exception as erro:
            gravaLog(tipo="Falha geral da recepção",msg=f'o erro foi {str(erro)}')
            self.onLine = False 
            return "falha"
    def zerar(self):
        self.faltantes=0
        self.contagem=0
        self.aprovados=0
        self.reprovados=0

gravaLog(msg="drive Contagem Iniciado")
memo = Camera.objects.get(ip="192.168.0.10")
camera = Protocol("192.168.0.10",32100,faltantes=memo.faltantes,contagem=memo.garrafas,aprovados=memo.aprovado,reprovados=memo.reprovado)
server = ModbusServer(host='0.0.0.0', port=502)
data = DataBank()

def gravaBanco():
    try:
        cam = Camera.objects.get(ip=camera.IP)
        if camera.onLine:
            cam.status= "OnLine"
        else:
            cam.status= "OffLine"
        cam.reprovado = camera.reprovados
        cam.aprovado = camera.aprovados
        cam.faltantes = camera.faltantes
        cam.garrafas = camera.contagem
        cam.save()
    except Exception as ex:
       gravaLog(tipo="Falha ao gravar no banco",msg=str(ex),file="log_dados.txt")

def ciclo():
    while True:
        camera.read_data()
        #print("camera_contagem",camera.contagem)

def ciclo_arquivo():
    while True:
        sleep(1)
        gravaBanco()
        try:
            data.set_words(9,[int(camera.onLine)])
            Ms = int(camera.contagem/65536)
            Ls = int(camera.contagem%65536)
            data.set_words(1,[Ms,Ls])
            Ms = int(camera.faltantes/65536)
            Ls = int(camera.faltantes%65536)
            data.set_words(3,[Ms,Ls])
            Ms = int(camera.aprovados/65536)
            Ls = int(camera.aprovados%65536)
            data.set_words(5,[Ms,Ls])
            Ms = int(camera.reprovados/65536)
            Ls = int(camera.reprovados%65536)
            data.set_words(7,[Ms,Ls])
        except Exception as ex:
            gravaLog(tipo="Falha ao gravar no ciclo",msg=str(ex),file="log_dados.txt")
        """    
        arquivo = open("data.log",'w')
        arquivo.write(f'{{"online":"{camera.onLine}","faltantes":{camera.faltantes},"total":{camera.contagem},"aprovados":{camera.aprovados},"reprovados":{camera.reprovados}}}')
        arquivo.close
        if data.get_words(10,number=1)[0]>0:
            camera.zerar()
            data.set_words(10,[0])
        if os.path.isfile('zerar.txt'):
            camera.zerar()
            os.remove('zerar.txt')
        """




def ciclo_modbus():
    server.start()

Tciclo = Thread(target=ciclo)
Tciclo.start()

#Tciclo_modbus = Thread(target=ciclo_modbus)
#Tciclo_modbus.start()

Tciclo_arquivo = Thread(target=ciclo_arquivo)
Tciclo_arquivo.start()
