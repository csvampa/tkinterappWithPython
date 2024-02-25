import socket
import sys

# El cliente manda datos recopilados del observador al servidor

class Cliente:
    def __init__(self):
        self.host = '192.168.0.62'
        self.puerto = 9999
        self.data = " ".join(sys.argv[1:])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



    def conectar(self):
        try:
            print(f"Intentando conectar al servidor en {self.host}:{self.puerto}")
            self.sock.connect((self.host, self.puerto))
            print(f"Conectado al servidor en {self.host}:{self.puerto}")
        except Exception as e:
            print(f"Error al conectar al servidor: {e}")

    def enviar_datosEliminados(self, datosEliminados):
        try:
            self.sock.sendall(datosEliminados.encode('utf-8'))
            print("Datos enviados con éxito.")
            received = self.sock.recv(1024) 
            print(received) # Imprime la respuesta del servidor
        except Exception as e:
            print(f"Error al enviar datos al servidor: {e}")

    def enviar_datosEditados(self, datosEditados):
        # print(datosEditados)
        try:
            editado = "EDIT:" + str(datosEditados)
            self.sock.sendall(editado.encode('utf-8'))
            received = self.sock.recv(1024) 
            print(received) # Imprime la respuesta del servidor
        except Exception as e:
            print(f"Error al enviar datos al servidor: {e}")

    def desconectar(self):
        try:
            self.sock.close()
            print("Desconectado del servidor.")
        except KeyboardInterrupt:
                print(f"Error en el servidor: {e}")
        except Exception as e:
            print(f"Error al enviar datos al servidor: {e}")