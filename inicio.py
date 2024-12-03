from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from proveedores.proveedores import ProveedorPrincipal
import os

class InicioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inicio.ui')
        loadUi(ui_path, self)
        

        # Conecta el botón "Proveedor"
        self.pushButton_Proveedor.clicked.connect(self.abrir_proveedores)
        #self.pushButton_Comprar.clicked.connect(self.abrir_)
        #self.pushButton_Usuarios.clicked.connect(self.abrir_)

    def abrir_proveedores(self):
        self.hide()
        self.ventana_proveedores = ProveedorPrincipal()
        self.ventana_proveedores.closed.connect(self.show)
        self.ventana_proveedores.show()
