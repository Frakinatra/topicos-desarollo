import sys
import mysql.connector
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox,QDialog
from inicio import InicioApp
from agregar.usuarios import AgregarUsuario  # Importar la clase AgregarUsuario desde el archivo correspondiente

class LoginApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Ruta dinámica al archivo UI
        ruta_ui = os.path.join(os.path.dirname(__file__), "proyecto.ui")
        if not os.path.exists(ruta_ui):
            QMessageBox.critical(self, "Error", f"No se encontró el archivo UI en: {ruta_ui}")
            sys.exit(1)
        uic.loadUi(ruta_ui, self)

        # Conectar los botones
        self.pushButton_2.clicked.connect(self.validar_login)  # Botón de login
        self.lineEdit_4.returnPressed.connect(self.validar_login)  # Usuario (Enter)
        self.lineEdit_3.returnPressed.connect(self.validar_login)  # Contraseña (Enter)
        self.pushButton_3.clicked.connect(self.abrir_agregar_usuario)  # Botón para agregar usuario

        self.usuario_id = None  # Almacena el ID del usuario logueado
        self.ventana_agregar = AgregarUsuario(self)  # Pasar la instancia de LoginApp


    def abrir_agregar_usuario(self):
        """Abre la ventana de agregar usuario y cierra la ventana de login"""
        self.close()  # Cierra la ventana de login
        self.ventana_agregar = AgregarUsuario(self)  # Pasamos la instancia de LoginApp a AgregarUsuario
        self.ventana_agregar.show()  # Muestra la ventana de agregar usuario


    def conectar(self):
        """Establece una conexión con la base de datos"""
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="login_db"
            )
            return conexion
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de conexión", f"Error: {err}")
            return None

    def validar_login(self):
        """Valida las credenciales ingresadas"""
        username = self.lineEdit_4.text().strip()   # Captura del usuario
        password = self.lineEdit_3.text().strip()   # Captura de la contraseña
        
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT id, username FROM users WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()

                if user:
                    self.usuario_id = user[0]  # Almacena el ID del usuario
                    QMessageBox.information(self, "Éxito", f"¡Bienvenido, {user[1]}!")
                    self.abrir_inicio()
                else:
                    QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de consulta", f"Error: {err}")
            finally:
                cursor.close()
                conexion.close()

    def abrir_inicio(self):
        """Abre la ventana principal después de un login exitoso"""
        self.ventana_inicio = InicioApp(self.usuario_id)  
        self.ventana_inicio.show()
        self.close()


# Ejecución de la ventana principal (Login)
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec_())

