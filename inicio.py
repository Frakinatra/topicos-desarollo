from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from proveedores.proveedores import ProveedorPrincipal
import os
from usuarios.usuarios_ui import UsuarioApp

class InicioApp(QMainWindow):
    def __init__(self, usuario_id):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inicio.ui')
        loadUi(ui_path, self)
        
        # Inicializar el ID del usuario
        self.usuario_id = usuario_id
        # print(self.usuario_id)
        

        # Conecta el botón "Proveedor"
        self.pushButton_Proveedor.clicked.connect(self.abrir_proveedores)
        self.pushButton_Comprar.clicked.connect(self.abrir_compras)
        #self.pushButton_Usuarios.clicked.connect(self.abrir_)

    def abrir_proveedores(self):
        self.hide()
        self.ventana_proveedores = ProveedorPrincipal()
        self.ventana_proveedores.closed.connect(self.show)
        self.ventana_proveedores.show()
        
    def abrir_compras(self):
        self.hide()
        self.ventana_compras = UsuarioApp(self.usuario_id)
        self.ventana_compras.closed.connect(self.show)
        self.ventana_compras.show()
