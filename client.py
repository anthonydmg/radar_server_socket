import socket
def client_program():
    host = "192.168.43.1"
    port  = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port)) 

    while True:
        data = client_socket.recv(1024).decode()
        print('Recive from server')
    
    client_socket.close()

if __name__ == '__main__':
    client_program()