from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
import os
from proveedores.agregar_Proveedor import AgregarProveedorWindow
from proveedores.agregar_Producto import AgregarProductoWindow

class ProveedorPrincipal(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Asegúrate de usar la ruta completa al archivo proveedores.ui
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proveedores.ui')
        loadUi(ui_path, self)

        self.btnAgregarProveedor.clicked.connect(self.mostrar_agregar_proveedor)
        self.btnGestionarProveedores.clicked.connect(self.mostrar_gestionar_proveedores)
        self.btnAgregarProducto.clicked.connect(self.mostrar_agregar_producto)
        self.btnGestionarProductos.clicked.connect(self.mostrar_gestionar_productos)
        
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()  # Aceptar el evento de cierre para que la ventana se cierre
        
    def mostrar_agregar_proveedor(self):
        self.hide()
        self.ventana = AgregarProveedorWindow()
        self.ventana.closed.connect(self.show)
        self.ventana.show()

    def mostrar_gestionar_proveedores(self):
        self.hide()
        self.ventana = GestionarProveedoresWindow()
        self.ventana.closed.connect(self.show)
        self.ventana.show()

    def mostrar_agregar_producto(self):
        self.hide()
        self.ventana = AgregarProductoWindow()
        self.ventana.closed.connect(self.show)
        self.ventana.show()

    def mostrar_gestionar_productos(self):
        self.hide()
        self.ventana = GestionarProductosWindow()
        self.ventana.closed.connect(self.show)
        self.ventana.show()

"""class GestionarProveedoresWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'con_Edi_Eli_Proveedor.ui')
        loadUi(ui_path, self)

class AgregarProductoWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agregar_Producto.ui')
        loadUi(ui_path, self)

class GestionarProductosWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'con_Edi_Eli_Productos.ui')
        loadUi(ui_path, self)"""
