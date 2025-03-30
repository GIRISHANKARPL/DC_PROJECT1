import socket

def coordinator_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print("Coordinator listening on port", port)

        conn, addr = server_socket.accept()
        print("Connection received from", addr)

        pos_tags = conn.recv(1024).decode()
        print("Final POS Tags received from POS tagging node:", pos_tags)

        # Save the output to a file
        with open("pos_output.txt", "w", encoding="utf-8") as f:
            f.write(pos_tags)

        print("POS tagging output saved to pos_output.txt")

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5003

    coordinator_server(HOST, PORT)
