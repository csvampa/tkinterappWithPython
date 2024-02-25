from cliente import *

# Uso un observador para recopilar info del sistema y mandarla al cliente

class Sujeto: 
    observadores=[]
    def agregar (self, obj):
        self.observadores.append(obj)
    def quitar(self, obj):
        pass
    def notificarEliminacion(self, datosEliminados):
        for observador in self.observadores:
            observador.update_eliminacion(datosEliminados)
    def notificarEdicion(self, filaID):
        for observador in self.observadores:
            observador.update_edicion(filaID)


class Observador:
   def update_eliminacion(self, ):
        raise NotImplementedError("Delegación de eliminación")
   def update_edicion(self, ):
        raise NotImplementedError("Delegación de edición")

class ConcretObserverA(Observador):
    def __init__(self, obj):
        self.observador_a=obj
        self.cliente = Cliente()
        self.observador_a.agregar(self)
    
    def update_eliminacion(self, datosEliminados):
        self.mensaje = str(datosEliminados) # Agrego la lógica para enviar los datos al servidor usando sockets
        self.cliente.conectar()
        self.cliente.enviar_datosEliminados(self.mensaje)

    def update_edicion(self, filaID):
        self.mensaje2 = str(f"Se ha editado la liquidacion nro: {filaID}")
        self.cliente.conectar()
        self.cliente.enviar_datosEditados(self.mensaje2)
    