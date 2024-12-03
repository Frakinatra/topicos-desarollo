from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.uic import loadUi
import os
from proveedores.agregar_Proveedor import AgregarProveedorWindow
from proveedores.agregar_Producto import AgregarProductoWindow
from proveedores.con_Edi_Eli_Productos import GestionarProductosWindow
from proveedores.con_Edi_Eli_Proveedor import GestionarProveedoresWindow

class ProveedorPrincipal(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Ruta completa al archivo proveedores.ui
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proveedores.ui')
        loadUi(ui_path, self)

        self.btnAgregarProveedor.clicked.connect(self.mostrar_agregar_proveedor)
        self.btnGestionarProveedores.clicked.connect(self.mostrar_gestionar_proveedores)
        self.btnAgregarProducto.clicked.connect(self.mostrar_agregar_producto)
        self.btnGestionarProductos.clicked.connect(self.mostrar_gestionar_productos)

        # Hacer que el QLabel actúe como botón
        self.regresar.setAttribute(Qt.WA_Hover, True)
        self.regresar.mousePressEvent = self.volver_anterior

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()  # Aceptar el evento de cierre para que la ventana se cierre

    def volver_anterior(self, event):
        self.close()

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
