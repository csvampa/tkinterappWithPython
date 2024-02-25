'''
Diplomatura en Python Nivel Intermedio.
Alumno: Carla Svampa.
Vista - aplicacion: Registro de Liquidaciones.
Librerías usadas: tkinter.
Módulos importados: modelo.
Python 3.5.11
'''

# Librerías
from tkinter import Label, Entry, StringVar, IntVar, DoubleVar, W, E, Button
from tkinter.messagebox import showerror, showinfo
from tkinter import ttk
from modelo import DataBase, ABMC
import re
from pathlib import Path
import os
import sys
import subprocess
import threading
from observador import Sujeto

theproc=""

# Decorador

def servidorConectado(func):
    def wrapper(self, *args, **kwargs):
        global theproc
        if theproc !="":
            return func(self, *args, **kwargs)
        else:
            showinfo('Alerta', 'El servidor no está conectado.')
        return 
    return wrapper

'''
En la clase Ventana se definen todos sus elementos.
'''
# Clase
class Ventana(Sujeto):
    def __init__(self, window):
        self.ventana = window
        self.db = DataBase()
        self.ventana.title("Liquidaciones")
        self.objeto_base = ABMC()
        self.server = None
        self.server_thread = None
        self.stop_server_event = threading.Event()

        #PASO 1 - AGREGO RUTA A SERVIDOR
        self.raiz = Path(__file__).resolve().parent
        self.ruta_server = os.path.join(self.raiz, 'SRC', 'servidor', 'servidor.py')
                    
        # Accesorios de la ventana gráfica
        self.titulo = Label(window, text='Registro de Liquidaciones', bg='DarkOrchid3', fg='thistle1', height=1, width=60)
        self.titulo.grid(row=0, column=0, columnspan=4, padx=1, pady=1, sticky=W+E)
        '''
        Elementos de sección Agregar Liquidación.
        '''
        self.id = Label(window, text='ID*: (Ingrese un ID único)')
        self.id.grid(row=1, column=0, sticky=W, padx=5)
        self.empresa = Label(window, text='Empresa*:')
        self.empresa.grid(row=2, column=0, sticky=W, padx=5)
        self.detalle = Label(window, text='Detalle*:')
        self.detalle.grid(row=3, column=0, sticky=W, padx=5)
        self.pagado = Label(window, text='Monto Pagado*:')
        self.pagado.grid(row=4, column=0, sticky=W, padx=5)
        self.fecha = Label(window, text='Fecha de cierre*:\n(dd/mm/yyyy)')
        self.fecha.grid(row=5, column=0, sticky=W, padx=5)
        self.comisiones=Label(window, text='Monto Facturado*:')
        self.comisiones.grid(row=6, column=0, sticky=W, padx=5)
        self.pagoRecibido=Label(window, text='Pago Recibido:')
        self.pagoRecibido.grid(row=7, column=0, sticky=W, padx=5)

        
        # Defino variables para tomar valores de campos de entrada
        
        self.id_val, self.emp_val, self.det_val, self.pago_val, self.fecha_val, self.comis_val, self.pagoRec_val = IntVar(), StringVar(), StringVar(), DoubleVar(), StringVar(), DoubleVar(), StringVar()
        w_ancho = 20

        self.entrada1 = Entry(window, textvariable = self.id_val, width = w_ancho) 
        self.entrada1.grid(row = 1, column = 0)
        self.entrada2 = Entry(window, textvariable = self.emp_val, width = w_ancho) 
        self.entrada2.grid(row = 2, column = 0)
        self.entrada3 = Entry(window, textvariable = self.det_val, width = w_ancho) 
        self.entrada3.grid(row = 3, column = 0)
        self.entrada4 = Entry(window, textvariable = self.pago_val, width = w_ancho) 
        self.entrada4.grid(row = 4, column = 0)
        self.entrada5 = Entry(window, textvariable = self.fecha_val, width = w_ancho) 
        self.entrada5.grid(row = 5, column = 0)
        self.entrada6 = Entry(window, textvariable = self.comis_val, width = w_ancho) 
        self.entrada6.grid(row = 6, column = 0)
        self.entrada7 = Entry(window, textvariable = self.pagoRec_val, width = w_ancho) 
        self.entrada7.grid(row = 7, column = 0)
        
        '''
        Elementos de la sección Filtrar.
        '''
        self.filtroEmp = Label(window, text='Buscar por Empresa')
        self.filtroEmp.grid(row=1, column=1, sticky=W)
        self.filtromesyanio = Label(window, text='Buscar por Mes\n(mm/yyyy)')
        self.filtromesyanio.grid(row=2, column=1, sticky=W)

        self.filtroemp_val, self.filtromesyanio_val = StringVar(), StringVar()
        w_ancho = 20

        self.inputEmp = Entry(window, textvariable = self.filtroemp_val, width = w_ancho)
        self.inputEmp.grid(row=1, column=1)
        self.filtromesyanio = Entry(window, textvariable= self.filtromesyanio_val, width=w_ancho)
        self.filtromesyanio.grid(row=2, column=1)


        '''
        Se define la vista de la sección Treeview
        '''

        self.tree = ttk.Treeview(window)
        self.tree['columns']=('col1', 'col2', 'col3', 'col4', 'col5', 'col6')
        self.tree.column('#0', width=90, minwidth=50, anchor=W)
        self.tree.column('col1', width=200, minwidth=80)
        self.tree.column('col2', width=200, minwidth=80)
        self.tree.column('col3', width=200, minwidth=80)
        self.tree.column('col4', width=200, minwidth=80)
        self.tree.column('col5', width=200, minwidth=80)
        self.tree.column('col6', width=200, minwidth=80)
        self.tree.heading('#0', text='ID')
        self.tree.heading('col1', text='Empresa')
        self.tree.heading('col2', text='Detalle')
        self.tree.heading('col3', text='Monto Pagado')
        self.tree.heading('col4', text='Fecha de cierre')
        self.tree.heading('col5', text='Monto Facturado')
        self.tree.heading('col6', text='Pago Recibido')
        self.tree.grid(row=10, column=0, columnspan=3, pady=10, padx=5)

        '''
        Sección Botones
        '''
        self.botonAgregar=Button(window, text='Agregar', command=lambda:self.vistaAlta())
        self.botonAgregar.grid(row=8, column=0, pady=5)
        
        self.botonFiltrar=Button(window, text='Filtrar', command=lambda:self.vistaFiltrar())
        self.botonFiltrar.grid(row=4, column=1, pady=5, padx=1)

        self.botonBorrarFiltro=Button(window, text='Eliminar Filtro', command=lambda:self.vistaActualizarTree())
        self.botonBorrarFiltro.grid(row=5, column=1, columnspan=1, pady=5, padx=1)

        self.botonCalcularTotales=Button(window, text='Calcular Totales', command=lambda:self.vistaTotales())
        self.botonCalcularTotales.grid(row=6, column=1, pady=5, padx=1)

        self.botonDescargar=Button(window, text='Descargar .CSV', command=lambda:self.descargar())
        self.botonDescargar.grid(row=7, column=1, pady=5, padx=1)

        self.botonBorrar=Button(window, text='Borrar Elemento Seleccionado', command=lambda:self.vistaBorrar())
        self.botonBorrar.grid(row=9, column=1, pady=5, columnspan=1)

        self.botonEditar=Button(window, text='Editar Elemento Seleccionado', command=lambda:self.vistaEditar(self.tree, window, w_ancho))
        self.botonEditar.grid(row=9, column=2, pady=5, columnspan=1)

        self.botonPrender=Button(window, text="Prender", command=lambda:self.try_connection())
        self.botonPrender.grid(row=11, column=1)

        self.botonApagar=Button(window, text="Apagar", command=lambda:self.stop_server())
        self.botonApagar.grid(row=11, column=2)
    '''
    Métodos:
        Define la acción de cada botón.
    '''
    # Métodos
    def vistaDataBase(self): 
        self.retorno = DataBase.crearTabla()
        if self.retorno:
            showinfo('Alerta', self.retorno)
    
    def vistaActualizarTree(self):
        self.retorno = self.objeto_base.actualizarTreeview(self.tree)
        if self.retorno:
            showinfo('Alerta', self.retorno)

    def vistaAlta(self,):
        retorno = self.objeto_base.alta(self.id_val, self.emp_val, self.det_val, self.pago_val, self.fecha_val, self.comis_val, self.pagoRec_val, self.tree)
        if retorno:
            showinfo('Alerta', retorno)
    
    def vistaFiltrar(self,):
        self.retorno = self.objeto_base.filtrar(self.filtroemp_val, self.filtromesyanio_val, self.tree)
        if self.retorno:
            showinfo('Alerta', self.retorno)

    def descargar(self,):
        items = self.tree.get_children()
        datos = [self.tree.item(item, 'values') for item in items]
        self.retorno = self.objeto_base.descargarCSV(datos)
        if self.retorno:
            showinfo('Alerta', str(self.retorno))

    @servidorConectado
    def vistaBorrar(self,):
        self.retorno= self.objeto_base.borrar(self.tree)
        if self.retorno:
            showinfo('Alerta', self.retorno)
    
    '''
    Define la función Editar:
        Corrobora que se haya seleccionado una fila a editar.
        Se crean campos de entrada con los valores de la fila a editar y los botones "Guardar" y "Cancelar Edición".
    '''
    def vistaEditar(self, tree, window, w_ancho):
        self.seleccion = tree.selection()
        if not self.seleccion:
            showinfo('Editar', 'Por favor, seleccione una fila para editar:')
            return
        
        self.item = tree.item(self.seleccion)
        self.filaValores = [self.item['text']] + list(self.item['values'])
        self.filaID = self.item['text']  

        self.nombresCampos = ['ID', 'Empresa', 'Detalle', 'Monto Pagado', 'Fecha de cierre:\n(dd/mm/yyyy)', 'Monto Facturado', 'Pago Recibido']

        self.cuadrosEntrada = []
        self.nuevasVariables = []
        self.etiquetas = []

        for i, (nombre, valor) in enumerate(zip(self.nombresCampos, self.filaValores)):
            self.etiqueta = Label(window, text=nombre)
            self.etiqueta.grid(row=i+1, column=2, sticky=W)
            self.etiquetas.append(self.etiqueta)

            self.var = StringVar(value=valor)
            
            self.cuadro = Entry(window, textvariable=self.var, width=w_ancho)
            self.cuadro.grid(row=i+1, column=2)
            
            self.cuadrosEntrada.append(self.cuadro)
            self.nuevasVariables.append(self.var)
            
        '''
        Se definen las acciones para los botones "Guardar" y "Cancelar edición".
        Se corroboran que los datos modificados cumplan con los formatos correspondientes 
        y se generan los mensajes de alerta correspondientes.
        '''
        @servidorConectado
        def guardarEdicion(self):
            self.nuevosValores = [self.nuevasVariables[0].get()] + [var.get() for var in self.nuevasVariables[1:]]  # Excluir el primer valor que es el ID
            self.fecha = self.nuevosValores[4]
            self.patronFecha = '^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$'
            self.montoPagado = self.nuevosValores[3]
            self.montoFacturado = self.nuevosValores[5]
            
            if not re.match(self.patronFecha, self.fecha):
                showerror('Error', 'El formato de fecha ingresado es incorrecto. Utilice dd/mm/yyyy.')
                return
            
            if not self.montoPagado.replace('.', '', 1).isdigit() or not self.montoFacturado.replace('.', '', 1).isdigit():
                showerror('Error', 'Los valores de monto pagado o monto facturado deben ser numéricos.')
                return
            
            if not self.nuevosValores[0] or not self.nuevosValores[1] or not self.nuevosValores[2] or not self.nuevosValores[4]:
                showerror('Error', 'Los campos ID, Empresa, Detalle y Fecha son obligatorios.')
                return
            try: 
                retorno = ABMC.guardar(self, self.nuevosValores, self.filaID)
                self.vistaActualizarTree()
                showinfo('Alerta', retorno)
                cancelarEdicion()
            except Exception as e:
                print(f'Error al guardar cambios: {str(e)}')
                showerror('Error', f'Error al guardar cambios: {str(e)}')

        def cancelarEdicion():
            for cuadro, etiqueta in zip(self.cuadrosEntrada, self.etiquetas):
                cuadro.grid_remove()
                etiqueta.grid_remove()
                botonGuardar.grid_remove()
                botonCancelar.grid_remove()
        # Botones de sección Edtiar
        botonGuardar = Button(window, text='Guardar', command=lambda: guardarEdicion(self))
        botonGuardar.grid(row=7, column=2, pady=5, padx=(100, 50), sticky=E)

        botonCancelar = Button(window, text='Cancelar Edición', command=lambda: cancelarEdicion())
        botonCancelar.grid(row=8, column=2, pady=5, padx=(100, 50), sticky=E)

    def vistaTotales(self):
        retorno = self.objeto_base.calcularTotales(self.tree)
        if retorno:
            showinfo('Alerta', retorno)

    # Métodos para conectar/desconectar la escucha del servidor

    def try_connection(self, ): 
        if theproc != "":
            theproc.kill()
            threading.Thread(target=self.lanzar_servidor, args=(True,), daemon=True).start() 
        else:
            threading.Thread(target=self.lanzar_servidor, args=(True,), daemon=True).start()
        return showinfo('Alerta', 'Conectado al Servidor')
        
    def lanzar_servidor(self, var):
        the_path =  self.ruta_server
        if var==True:
            global theproc
            theproc = subprocess.Popen([sys.executable, the_path])
            theproc.communicate()
        else:
            print("")

    def stop_server(self, ):
        global theproc
        if theproc !="":
            theproc.kill() 
        return showinfo('Alerta', 'Servidor Desconectado')