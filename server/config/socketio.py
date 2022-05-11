import socketio
import asyncio

sio = socketio.client.Client()

@sio.event
async def connect():
    print(f'se conectou')

@sio.event
async def my_message(data):
    print(f'recebi uma msg de {len(data)}')

@sio.event
async def disconect():
    print('Desconectou')

async def main():
    await sio.connect("192.168.0.10:32200")
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
