from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from proveedores.proveedores import ProveedorPrincipal

class InicioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('inicio.ui', self)

        # Conecta el botón "Proveedor"
        self.pushButton_3.clicked.connect(self.abrir_proveedores)

    def abrir_proveedores(self):
        self.hide()
        self.ventana_proveedores = ProveedorPrincipal()
        self.ventana_proveedores.closed.connect(self.show)
        self.ventana_proveedores.show()
