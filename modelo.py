'''
Diplomatura en Python Nivel Intermedio.
Alumno: Carla Svampa.
Modelo - aplicacion: Registro de Liquidaciones.
Librerías usadas: sqlite3 y re.
Python 3.5.11
'''
import sqlite3
import re
from observador import Sujeto
import tkinter as tk
import csv

'''DECORADORES'''

# Imprime la llamada a los métodos Alta y Borrar
def registroLog(funcion):
    def envoltura(*args, **kwargs):
        envoltura.numero+=1
        print("llamada número %s a la función %s" %(envoltura.numero, funcion.__name__))
        return funcion(*args, **kwargs)
    envoltura.numero = 0 
    return envoltura

# Verifica que los datos en ALTA sean numéricos para continuar y emire el mensaje de alerta correspondiente
def verificacionDatos(funcion):
    def envoltura(self, id, empresa, detalle, pagado, fecha, comisiones, pagoRecibido, tree):
        try:
            pagado_numero = float(pagado.get())
            comisiones_numero = float(comisiones.get())
        except tk.TclError as e:
            return 'Los campos "Pagado" y "Comisiones" deben ser números.'
        return funcion(self, id, empresa, detalle, pagado, fecha, comisiones, pagoRecibido, tree)
    return envoltura

'''
En la clase de la Base de datos creo los métodos para la conexión y la creación de la tabla.
'''
# Clase de Base de datos
class DataBase():
    def __init__(self,):
        pass
    def crearTabla(self):
        self.con = self.conexion()
        self.cursor = self.con.cursor()
        self.sql = """CREATE TABLE IF NOT EXISTS liquidaciones
                (id INTEGER PRIMARY KEY,
                empresa varchar(20) NOT NULL,
                detalle varchar(10),
                pagado real,
                fecha DATE,
                comisiones real,
                pagoRecibido varchar(10))
        """
        self.cursor.execute(self.sql)
        self.con.commit()        
        self.con.close()
    
    # Métodos
    def conexion(self):
        self.con = sqlite3.connect("mibase.db")
        return self.con
        
'''
En la clase ABMC uso métodos para realizar:
Actualización de la vista de datos cargados, Alta, Filtro, Calculo de totales, Baja y Guardar cambios realizados.
'''
        
#  Clase de Alta, Baja, Modificación y Consulta 
class ABMC(Sujeto):
    '''
    Actualización de la vista:
        Se eliminan todos los datos de la vista.
        Se conecta con la base para buscar las liquidaciones cargadas.
        Se muestran los resultados encontrados en pantalla y se cierra la conexión con la base.
    '''
    #  Métodos
    def actualizarTreeview(self, tree):
        records = tree.get_children()
        for element in records:
            tree.delete(element)

        DataBase.sql = 'SELECT * FROM liquidaciones ORDER BY id ASC'
        self.con= DataBase.conexion(self)
        self.cursor= self.con.cursor()
        self.datos=self.cursor.execute(DataBase.sql)

        resultado = self.datos.fetchall()
        for fila in resultado:
            tree.insert('', 0, text=fila[0], values=(fila[1], fila[2], fila[3], fila[4], fila[5], fila[6]))
        self.con.close()
    
    '''
    Alta de registro:
        Corrobora que los campos obligatorios hayan sido completados.
        Corrobora que el campo Fecha haya sido cargado en el formato correspondiente con Regex.
        Se conecta a la base de datos y corrobora que el ID a cargar no exista en la base.
        Si todo está bien, carga los datos a la base.
        Limpia los campos de entrada, devuelve el mensaje de éxito correspondiente y se cierra la conexión con la base.
    '''
    @verificacionDatos
    @registroLog
    def alta(self, id, empresa, detalle, pagado, fecha, comisiones, pagoRecibido, tree):
        if not id.get() or not empresa.get() or not detalle.get() or not pagado.get() or not fecha.get() or not comisiones.get():
            return 'Los campos con * son Obligatorios.'
        patronFecha = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
        if not re.match(patronFecha, fecha.get()):
            return 'El formato de fecha ingresado es incorrecto. Utilice dd/mm/yyyy.'

        self.con = DataBase.conexion(self)
        self.cursor = self.con.cursor()

        # Verifica si el ID ya existe en la base de datos
        self.cursor.execute('SELECT id FROM liquidaciones WHERE id = ?', (id.get(),))
        existeID = self.cursor.fetchone()
        if existeID:
            self.con.close()
            return 'El ID ya existe en la base de datos, ingrese un valor diferente.'
        else:
            data = (id.get(), empresa.get(), detalle.get(), pagado.get(), fecha.get(), comisiones.get(), pagoRecibido.get())
            self.sql = 'INSERT INTO liquidaciones(id, empresa, detalle, pagado, fecha, comisiones, pagoRecibido) VALUES (?, ?, ?, ?, ?, ?, ?)'
            self.cursor.execute(self.sql, data)
            self.con.commit()
            self.actualizarTreeview(tree)
        # Limpia los campos de entrada después de la inserción exitosa
        for var in (id, empresa, detalle, pagado, fecha, comisiones, pagoRecibido):
            var.set('')
        self.con.close()

        return 'Liquidacion cargada con éxito.'
    
    '''
    Filtro: Funciona como motor de búsqueda. 
        Permite filtrar por empresa o por mes de liquidación 
        Se conecta con la base de datos y muestra el/los resultados en pantalla.
        En caso de filtrar por fecha, corrobora que se realice en el formato correspondiente.
        Luego deja los campos de entrada en blanco para hacer una nueva búsqueda y se cierra la conexión con la base.
    '''
    def filtrar(self, empresa, mesyanio, tree):
        self.con=DataBase.conexion(self)
        self.cursor=self.con.cursor()
        self.sql = 'SELECT * FROM liquidaciones WHERE 1=1'
        params = []
        if empresa.get():
            empresa_str=str(empresa.get())
            self.sql += ' AND empresa LIKE :empresa'
            params.append(f"%{empresa_str}%")
        
        if mesyanio.get():
            try:
                mes, anio = str(mesyanio.get()).split('/')
                mes = int(mes)
                anio = int(anio)
                self.sql += ' AND substr(fecha, -7) LIKE :fecha'
                params.append(f'%{mes:02d}/{anio}%') 

            except ValueError:
                self.con.close()
                return 'Error','Ingrese una fecha válida en formato mm/aaaa.'
                
        self.cursor.execute(self.sql, params)
        resultado = self.cursor.fetchall()

        for row in tree.get_children():
            tree.delete(row)
        
        for fila in resultado:
            tree.insert('', 0, text=fila[0], values=(fila[1], fila[2], fila[3], fila[4], fila[5], fila[6]))

        empresa.set('')
        mesyanio.set('')
        self.con.close()
        
    def descargarCSV(self, resultado):
        liquidacion = "liquidacion_exportada.csv"
        # Escribir los resultados en un archivo CSV
        with open(liquidacion, "w", newline="", encoding="utf-8") as archivo_csv:
            # Crear un escritor de CSV
            escritor_csv = csv.writer(archivo_csv)

            # Escribir la cabecera (nombre de las columnas)
            escritor_csv.writerow([descripcion[0] for descripcion in self.cursor.description[1:]])
            
            for fila in resultado:
                valores_filtrados = [str(valor) if valor is not None and str(valor) != '' else '' for valor in fila]
                escritor_csv.writerow(valores_filtrados)
        return 'Archivo exportado.'
        
    '''
    Calcular Totales: 
        suma los montos pagados y facturados de todas las liquidaciones que se muestran en pantalla.
    '''
    def calcularTotales(self, tree):
        self.totalPagado = 0
        self.totalFacturado = 0

        for row in tree.get_children():
            fila = tree.item(row)["values"]
            
            self.totalPagado += float(fila[2])
            self.totalFacturado += float(fila[4])

        self.filaTotales = ('Total', '', self.totalPagado, '', self.totalFacturado)
        tree.insert('', 'end', values=self.filaTotales)
    '''
    Borrar: 
        Corrobora que se haya seleccionado una fila, se conecta con la base.
        Obtiene los datos de la fila a eliminar, borra los datos de la base.
        Se cierra la conexión a la base
        y devuelve un mensaje mostrando los datos de la fila eliminada.
        
    '''
    @registroLog
    def borrar(self, tree):
        valor = tree.selection() 
        if not valor:
            return 'Por favor, seleccione una fila para eliminar.'

        item = tree.item(valor)
        mi_id = item['text']

        self.con = DataBase.conexion(self)
        self.cursor = self.con.cursor()
        mi_id = int(mi_id)
        data = (mi_id,)
        
        # Obtengo los datos antes de eliminar la fila
        self.cursor.execute('SELECT * FROM liquidaciones WHERE id = ?;', data)
        filaEliminada = self.cursor.fetchone()
        try:
            self.notificarEliminacion(filaEliminada)
            self.sql = 'DELETE FROM liquidaciones WHERE id = ?;'
            self.cursor.execute(self.sql, data)
            self.con.commit()
            tree.delete(valor)
            self.con.close()

            # Muestro los datos de la fila eliminada
            if filaEliminada:
                return f'Elemento eliminado con éxito.\nDatos eliminados: {filaEliminada}'
            else:
                return 'Elemento eliminado con éxito. Los datos no se pudieron recuperar.'
        except Exception as e:
        # Manejar la excepción (puedes hacer lo que necesites, como notificar al usuario)
            print(f"Error en la eliminación de la fila: {e}")
            return f"Error en la eliminación de la fila: {e}"
        
    '''
    Guardar: 
        En caso de edición de una liquidación, se conecta con la base
        guarda los nuevos datos ingresados para la fila seleccionada
        y se cierra la conexión con la base.
    '''

    def guardar(self, nuevosValores, filaID):
        try:
            self.notificarEdicion(filaID)
            self.con = DataBase.conexion(self)
            self.cursor = self.con.cursor()
            
            self.sql = 'UPDATE liquidaciones SET id=?, empresa=?, detalle=?, pagado=?, fecha=?, comisiones=?, pagoRecibido=? WHERE id=?'
            data = tuple(nuevosValores) + (filaID,) 
        
            self.cursor.execute(self.sql, data)
            self.con.commit()
            self.con.close()
            return 'Los cambios se han guardado exitosamente.'
        except Exception as e:
            print(f'Error al guardar cambios: {str(e)}')
            return f'Error al guardar cambios: {str(e)}'