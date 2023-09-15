from socket import *
import threading
import json
import os

server_name = 'localhost'
server_port = 12004
mutex = threading.Lock()

client = socket(AF_INET , SOCK_STREAM)
client.connect((server_name,server_port))

Name =""
def new_name():
    global Name
    Name = input("Enter your name: ")

#handles connection with server
def connection_handle():
    new_name()
    while True:
        received_message = client.recv(1024).decode('utf-8')
        received_message = received_message.strip()
        if received_message == 'Name':
            client.send(Name.encode('utf-8'))
        elif received_message == 'Retry':
            print("Name already exists,try again")
            new_name()
        elif received_message == 'Terminate':
            exit()
        elif received_message == 'Success':
            break
        else :
            print("Something went wrong")
            exit()

stop_thread = False

#function for receiving messages
def receiver():
    global stop_thread
    while True:
        received_message = client.recv(1024).decode('utf-8')
        if not received_message:
            stop_thread = True        
        if stop_thread:
            break
        
        decoded_message = json.loads(received_message)
        if decoded_message[0] == 1:
            if decoded_message[1] == 0:
                print(f"{decoded_message[2]} has left the chat!")
            elif decoded_message[1] == 1:
                print(f"{decoded_message[2]} joined the chat")
            else:
                print(f"{decoded_message[2]}: {decoded_message[3]}")

        elif decoded_message[0] == 2:
            mutex.acquire()
            with open(f"{decoded_message[2]}",'wb') as image_file:
                file_len = int(client.recv(1024).decode('utf-8').strip())
                
                while file_len > 0:
                    data = client.recv(1024)
                    file_len -= len(data)
                    if not data:
                        break
                    image_file.write(data)
                
                print(f'The file has been received form {decoded_message[1]}')
            
            mutex.release()

#function for sending messages
def sender():
    global stop_thread
    while True:
        if stop_thread:
            break
        task = int(input(""))
        if task == 1:
            client.send("1".encode('utf-8'))
            message = input("")
            client.send(message.encode('utf-8'))    
        elif task ==2:
            client.send("2".encode('utf-8'))
            file_name = input("")
            dir = input("")
            client.send(file_name.ljust(1024).encode('utf-8'))
            client.send((str(os.path.getsize(dir))).ljust(1024).encode('utf-8'))
            with open(dir,'rb') as image_file:
                while True:
                    data = image_file.read(1024)
                    if not data:
                        break
                    client.send(data)
            print('The file has been sent')
        elif task == 3:
            client.send("3".encode('utf-8'))
            exit()

connection_handle()

#creating thread for receiving messages
thread_receive = threading.Thread(target=receiver)
thread_receive.start()

sender()

print("Client is closed")
client.close()