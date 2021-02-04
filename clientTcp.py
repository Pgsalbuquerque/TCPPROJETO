import socket
HOST = 'localhost'     # Endereco IP do Servidor
PORT = 3333            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)
msg = input()
while True:
     tcp.send(msg.encode())
     msg = input()
tcp.close()
