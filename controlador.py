'''
Diplomatura en Python Nivel Intermedio.
Alumno: Carla Svampa.
Controlador - aplicacion: Registro de Liquidaciones.
Librerías usadas: tkinter.
Módulos importados: vista.
Python 3.5.11
'''
# Librerías
from tkinter import Tk
import vista
import observador


# Clase
class Controlador:
    def __init__(self,root):
        self.root_controlador = root
        self.objeto_vista = vista.Ventana(self.root_controlador)
        self.el_observador = observador.ConcretObserverA(self.objeto_vista.objeto_base)

# Bucle principal
if __name__ == '__main__':
    root_tk = Tk()
    app = Controlador(root_tk)
    app.objeto_vista.vistaActualizarTree()
    root_tk.mainloop()

    # 10/10/2020