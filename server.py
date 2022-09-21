import socket
import time
count = 1 

HOST = "127.0.0.1"
PORT = 65432  
COUNT = 0
with socket.socket(socket.AF_INET,  socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            conn.sendall(b"Hello World")
            time.sleep(1)
        
    
#def server_program():
#    host = socket.gethos()
#    print("Hosta name: ",host)
#    port = 5025
    
#    server_socket = socket.socket()
#    server_socket.bind((host, port))

    ## how many clien the server can listen simultaneuslu
#    server_socket.listen(2)

#    conn, address = server_socket.accept()
#    print("Connection From "  + str(address))

#   while True:
        # recive 
#        if count > 100 :
#            break
#        conn.send("Count: " + str(count))
#        count += 1 
#    conn.close()

#if __name__ == "__main__":
#    server_program()