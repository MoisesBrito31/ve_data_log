import threading 
import subprocess
from time import sleep


"""

script para atualizar o relogio do sistema para a ultima vez que o mesmo foi desligado

"""
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

try:
    fi = open("relogio.txt","r")
    valor = str(fi.read())[2:14]
    print(valor)
    comando = subprocess.check_output(['sudo','date',valor])
    fi.close()
    print(f'retorno do relogio: {comando}')
except Exception as ex:
    print(f'falha em set do relogio: {str(ex)}')


t_relogio = threading.Thread(target=atualizaRelogio).start()