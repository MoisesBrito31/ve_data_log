from pyModbusTCP.client import ModbusClient as Modbus
import threading

fim_Programa = threading.Event()


def main_ciclo():
    print("Inicio do Programa")
    camera = Modbus(host='192.168.0.11', port=502)
    camera.open()
    while not fim_Programa.is_set():
        cmd = input()
        if cmd == "end":
            fim_Programa.set()
        elif cmd == "conecta":
            if not camera.is_open():
                camera = Modbus(host='192.168.0.11', port=502)
                camera.open()
        elif cmd == "desconecta":
            if camera.is_open():
                camera.close()
        elif cmd == "status":
            print(camera.is_open())
        elif cmd.find("read")>-1:
            ad = int(cmd.split(' ')[1])
            qtd = int(cmd.split(' ')[2])
            print(camera.read_input_registers(ad,qtd))
        else:
            print("codigo inexistente")
    print("fim do programa")
        
t_cliclo_main = threading.Thread(target=main_ciclo)
t_cliclo_main.start()