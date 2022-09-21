import socket

count = 1 

def server_program():
    host = socket.gethostname()
    print("Hosta name: ",host)
    port = 5025
    
    server_socket = socket.socket()
    server_socket.bind((host, port))

    ## how many clien the server can listen simultaneuslu
    server_socket.listen(2)

    conn, address = server_socket.accept()
    print("Connection From "  + str(address))

    while True:
        # recive 
        if count > 100 :
            break
        conn.send("Count: " + str(count))
        count += 1 
    conn.close()

if __name__ == "__main__":
    server_program()