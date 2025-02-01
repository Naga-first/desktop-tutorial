import socket
import threading

SERVER = '2409:40d2:5e:15c8:34b0:280f:1b6d:7bb4' 
PORT = 55555

client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def send():
    while True:
        message = input("")
        client.send(message.encode('ascii'))
        if message.strip().upper() == "EXIT":
            client.close()
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()
