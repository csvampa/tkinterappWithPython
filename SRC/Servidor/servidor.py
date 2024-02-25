import socketserver
import sqlite3
import ast
import datetime
import threading

# global HOST
global PORT

# Crea una base de datos para archivar info recibida

class DataBase():
    def __init__(self,):
        pass
    # Métodos
    def conexion(self):
        self.con = sqlite3.connect("registroLog.db")
        return self.con
    def crearTabla(self):
        try:
            self.con = DataBase.conexion(self)
            self.cursor = self.con.cursor()
            self.sql2 = """CREATE TABLE IF NOT EXISTS registroLog
                    (id INTEGER,
                    empresa varchar(20) NOT NULL,
                    detalle varchar(10),
                    pagado real,
                    fecha DATE,
                    comisiones real,
                    pagoRecibido varchar(10),
                    fechaHora varchar(50))
            """
            self.cursor.execute(self.sql2)
            self.con.commit()        
        except sqlite3.Error as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            self.con.close()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        fecha_hora_actual = None
        # self.con = None
        try:
            data = self.request.recv(1024).strip()
            fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_str = data.decode('UTF-8')
            # print(f"Mensaje recibido del cliente: {data_str}")

            try: 
                # si tiene el identificador:
                identifier, message = data_str.split(":", 1)
                if identifier == "EDIT":
                    # Guardar respuesta en un archivo
                    with open('respuesta.txt', 'a') as file:
                        file.write(f'{message} {fecha_hora_actual}\n')
                        print(f'Respuesta guardada en el archivo: {message} {fecha_hora_actual}')
                
            except ValueError:
                identifier = None
                message = data_str

                data_tuple = ast.literal_eval(data_str)
                dataTupla = tuple([None if value == '' else value for value in data_tuple])
                registro = (*dataTupla, fecha_hora_actual)
                
                #   Guarda los datos en la base
                db = DataBase()
                db.crearTabla() 
                self.con = db.conexion()    
                self.cursor = self.con.cursor()
                self.sql2 = 'INSERT INTO registroLog(id, empresa, detalle, pagado, fecha, comisiones, pagoRecibido, fechaHora) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
                self.cursor.execute(self.sql2, registro)
                self.con.commit()
                self.con.close()
                print('Registro borrado: ' + data_str)

               
            response = b"OK"  # Puedes personalizar la respuesta según tus necesidades
            self.request.sendall(response)
        
        except ValueError as ve:
            print(f"Error al procesar los datos del cliente: {ve}")

        except sqlite3.Error as se:
            print(f"Error al trabajar con la base de datos: {se}")
       
        except Exception as e:
            error_message = f"Error en el manejo de datos: {e}"
            # Guardo errores en un archivo .txt y lo informo al cliente
            with open('errores.txt', 'a') as file:
                file.write(f'{error_message} {fecha_hora_actual}\n')

                
if __name__ == "__main__":
    HOST, PORT = "192.168.0.62", 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print(f"Servidor escuchando en {HOST}:{PORT}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"Error en el servidor.")
 