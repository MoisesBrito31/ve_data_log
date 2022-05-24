import relogio
import threading
from datetime import datetime
from time import sleep
from config.models import Camera, Imagem
from VE.drive import DriveData, DriveImg

fim_Programa = threading.Event()
contagens = []

class Contagem():
    faltantes = 0
    contagem = 0
    aprovados = 0
    reprovados = 0
    lastValue = 0
    ip = "192.168.0.1"
    camera = "192.168.0.1"

    def __init__(self, camera):
        self.camera = DriveData(ip=camera.ip, port=camera.porta_dados)
        self.ip = camera.ip

    def contar(self):
        dado = self.camera.read_data()
        if len(dado) > 1:
            self.faltantes+=dado[0]
            self.contagem+=dado[1]
            self.lastValue = dado[1]
            if dado[0] > 0 or dado[1] > 0:
                if dado[0]>0:
                    self.reprovados+=1    
                else:
                    self.aprovados+=1

    def zerar(self):
        self.faltantes=0
        self.contagem=0
        self.aprovados=0
        self.reprovados=0

def img_loop(cam,index):
    print(f'iniciou imagem {cam.IP}')
    while not fim_Programa.is_set():
        img = cam.read_img()
        if img != None and img.find("Falha") == -1:
            cam = Camera.objects.get(ip=cam.IP)
            arq = Imagem(camera=cam,data=datetime.now(),img=f'media/{img}',garrafas=contagens[index])
            cam.img = f'media/{img}'
            cam.save()
            arq.save()

def img_live_loop(cam):
    print(f'iniciou Live imagem {cam.IP}')
    while not fim_Programa.is_set():
        cam.readLive()
        sleep(1)


def data_loop(contagem):
    print(f'iniciou data {contagem.ip}')
    while not fim_Programa.is_set():
        contagem.contar()

def ciclo_arquivo(conts):
    while not fim_Programa.is_set():
        sleep(1)
        for c in conts:
            cam = Camera.objects.get(ip=c.ip)
            cam.reprovado = c.reprovados
            cam.aprovado = c.aprovados
            cam.faltantes = c.faltantes
            cam.garrafas = c.contagem
            cam.save()

 

def mainCicle():
    cameras = []
    thrs = []
    camQuery = Camera.objects.all()
    number = 0
    for c in camQuery:
        camera = DriveImg(c.ip,c.porta_img)
        contagens.append(Contagem(c))
        thrs.append(threading.Thread(target=img_loop,args=(camera,number)))
        thrs.append(threading.Thread(target=img_live_loop,args=(camera,)))
        thrs.append(threading.Thread(target=data_loop,args=(contagens[number],)))
        number+=1
    for t in thrs:
        t.start()
    t_gravaCliclo = threading.Thread(target=ciclo_arquivo,args=(contagens,)).start()
    while not fim_Programa.is_set():
        cmd = input()
        if cmd == "end":
            relogio.fim_Programa.set()
            fim_Programa.set()
        if cmd.find("contagem")>-1:
            try:
                index = int(cmd.split(" ")[1])
                print(f'total {contagens[index].contagem}')
            except:
                print("erro")
            pass
        if cmd.find("faltantes")>-1:
            try:
                index = int(cmd.split(" ")[1])
                print(f'faltantes {contagens[index].faltantes}')
            except:
                print("erro")
            pass
    print("fim do programa")

t_main = threading.Thread(target=mainCicle).start()