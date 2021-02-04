import socket
import os
from threading import Thread
import mimetypes
import platform

class ServerTCP:
    def __init__(self):
        self.host = 'localhost'
        self.port = 3333
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.orig = (self.host, self.port)
        self.p = 'C:\\Users\\pdr\\Documents\\repos' #use \\ para windows ou / para linux
        self.startServer()
    
    def startServer(self):
        self.tcp.bind(self.orig)
        self.tcp.listen()
        self.path_replace()
        self.inicializar_pasta()
        print("servidor rodando")
        self.accept()
        
    def previous_paste(self,pasta):
        pasta = pasta.replace("\\","/")
        if pasta == "/":
            return "/"
        pasta = pasta.split("/")
        pasta.pop()
        pasta.pop()
        pasta.pop(0)
        if len(pasta) == 0:
            return "/"
        
        st = ""
        for x in pasta:
            st += x
            st += "/"
        return st

    def path_replace(self):
        self.p = self.p.replace("/", "\\")

    def enviar_arq(self, arq, con):
        path = self.p + arq
        try:
            os.listdir(path)
            self.enviar_pasta(arq, con)
            return
        except:
            pass
        #C:\\Users\\pdr\\Documents\\repos\\favicon.ico
        if platform.system() != "Windows":
            path = path.replace("\\", "/")
        try:
            f = open(path, 'rb')
        except:
            st = b'HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html\r\nContent-Length:22 ; charset=utf-8 \r\n\r\n<h1>404 NOT FOUND</h1>\r\n'
            con.send(st)
            return
        content_type = mimetypes.MimeTypes().guess_type(path)[0]
        if content_type == None:
            content_type = "text/txt"
        text = b''
        f = f.readlines()
        for x in f:
            text += x
        len_f = len(text)
        st = b'HTTP/1.1 200 OK\r\nContent-Length:' + str(len_f).encode() + b'\r\nContent-Type:' + content_type.encode() + b'; charset=utf-8\r\n\r\n'
        st += text
        con.send(st)

    def inicializar_pasta(self):
        path = self.p
        if platform.system() != "Windows":
            path = path.replace("\\", "/")
        try:
            os.listdir(self.p)
        except:
            os.mkdir(self.p)
            print("diretorio criado")

    def checkfolder(self,path):
        try:
            os.listdir(path)
            return True
        except:
            return False
            
    def enviar_pasta(self, pasta, con):
        if pasta[len(pasta)-1] != "\\":
            pasta += "\\"
        path = self.p + pasta
        #\\projetinho\\index.html
        #C:\\Users\\pdr\\Documents\\repos\\
        if platform.system() != "Windows":
            path = path.replace("\\", "/")
        try:
            arquivos_na_pasta = os.listdir(path)
            #["servidor.py", "projeto", "index.html"]
        except:
            st = b'HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html\r\nContent-Length:22 ; charset=utf-8 \r\n\r\n<h1>404 NOT FOUND</h1>\r\n'
            con.send(st)
            return
        if "index.html" in arquivos_na_pasta:
            pasta += "index.html"
            self.enviar_arq(pasta, con)
            return
        if "index.htm" in arquivos_na_pasta:
            pasta += "index.htm"
            self.enviar_arq(pasta, con)
            return
        #localhost:3333/TCPROJETO/projetinho
        #/
        #/TCPROJETO/
        previous = self.previous_paste(pasta) #projetinho/projeto
        if previous[0] != "/":
            previous = "/" + previous
        sf = b'HTTP/1.1 200 OK\r\n'
        
        st = b'<pre> <p>Name                  Size</p><hr> <a href="' + previous.encode() + b'"> <--- Parent Directory</a><p/>\r\n'
        for arquivo in arquivos_na_pasta:
            folder = self.checkfolder(path+arquivo)
            if folder == True:
                s = os.path.getsize(path+arquivo)
                s = f'{s/1024:.2f} KB'
                st += b' <a href="' + arquivo.encode() + b'/">' + arquivo.encode() + b'/</a>       ' + s.encode()  + b' \r\n'
            elif folder == False:
                s = os.path.getsize(path+arquivo)
                s = f'{s/1024:.2f} KB'
                st += b'<a href="' + arquivo.encode() + b'">' + arquivo.encode() + b'</a>       ' + s.encode()  + b'\r\n'

        
        n = f"Content-Length:{len(st)}\r\nContent-Type:text/html\r\n; charset=utf-8\r\n\r\n"
        sf += n.encode()
        sf += st
        con.send(sf)

    def listen(self, con, cliente):
        while True:
            msg = con.recv(1024)
            if not msg: break
            try:
                m = msg.decode()
                a = m.split("\n")[0].replace("\r", "").split(" ")
                #["GET", "/favicon.ico", "HTTP/1.1"]
                if a[0] != "GET":
                    st = b'HTTP/1.1 400 BAD REQUEST\r\nContent-Type: text/html\r\nContent-Length:24 ; charset=utf-8 \r\n\r\n<h1>400 BAD REQUEST</h1>\r\n'
                    con.send(st)
                    
                elif a[2][:4] != "HTTP":
                    st = b'HTTP/1.1 400 BAD REQUEST\r\nContent-Type: text/html\r\nContent-Length:24 ; charset=utf-8 \r\n\r\n<h1>400 BAD REQUEST</h1>\r\n'
                    con.send(st)
                elif a[2][5:] != "1.1":
                    st = b'HTTP/1.1 505 HTTP Version Not Supported\r\nContent-Type: text/html\r\nContent-Length:39 ; charset=utf-8 \r\n\r\n<h1>505 HTTP Version Not Supported</h1>\r\n'
                    con.send(st)
                else:
                    m = a[1].replace("/", "\\")
                    if '.' in m:
                        Thread(target=self.enviar_arq, args=(m, con)).start()
                    else:
                        Thread(target=self.enviar_pasta, args=(m, con)).start()
            except:
                st = b'HTTP/1.1 400 BAD REQUEST\r\nContent-Type: text/html\r\nContent-Length:24 ; charset=utf-8 \r\n\r\n<h1>400 BAD REQUEST</h1>\r\n'
                con.send(st)
    def accept(self):
        while True:
             con, cliente = self.tcp.accept()
             Thread(target=self.listen, args=(con, cliente)).start()
             
ServerTCP()
