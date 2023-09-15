from socket import *
import threading
import json
import os

serverport = 12004
server = socket(AF_INET , SOCK_STREAM)
server.bind(('',serverport))

client_Name = {}

def broadcast(Name,data):
    for i in client_Name:
        if i != Name:
            client_Name[i][0].send(data.ljust(1024).encode('utf-8'))


def close_connection(client,addr,Name):
    client.close()
    client_Name.pop(Name)
    encoded_message = json.dumps([1,0,Name])
    broadcast(Name,encoded_message)

def communication_handel(client,addr,Name):
    global stop_thread
    while True:
        task = client.recv(1024).decode('utf-8')
        if not task:
            close_connection(client,addr,Name)
            break

        if task == '1':
            sentence = client.recv(1024).decode('utf-8')
            encoded_message = json.dumps([1,2,Name,sentence])
            broadcast(Name,encoded_message)

        elif task == '2':
            # mutex.acquire()
            file_name = client.recv(1024).decode('utf-8').strip()
            
            if not file_name:
                close_connection(client,addr,Name)
                break
            file_len = int(client.recv(1024).decode('utf-8').strip())

            if not file_len:
                close_connection(client,addr,Name)
                break
            encoded_message = json.dumps([2,Name,file_name])
            
            broadcast(Name,encoded_message)
            broadcast(Name,str(file_len))
            
            while file_len > 0:
                data = client.recv(1024)
                file_len-= len(data)

                if not data:
                    close_connection(client,addr,Name)
                    break
                
                for i in client_Name:
                    if i!= Name:
                        client_Name[i][0].send(data)
            
            # mutex.release()

def connection_handel(client,addr):
    limit = 0
    while True:
        client.send("Name".ljust(1024).encode('utf-8'))
        Name = client.recv(1024).decode('utf-8')
        Name = Name.title()
        if Name in client_Name:
            if limit == 3:
                client.send("Terminate".ljust(1024).encode('utf-8'))
                client.close()
                exit()
            client.send("Retry".ljust(1024).encode('utf-8'))
            limit += 1        
        else:
            client_Name[Name] = [client,addr]
            client.send("Success".encode('utf-8'))
            encoded_message = json.dumps([1,1,Name])
            broadcast(Name,encoded_message)
            break
    communication_handel(client,addr,Name)


def connect():
    server.listen()
    while True:
        client,addr = server.accept()
        thread_receive = threading.Thread(target=connection_handel,args=(client,addr))
        thread_receive.start()

print("The server is ready to receive")

connect()   

print("Server is closed")
server.close()