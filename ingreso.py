import sys
import mysql.connector
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from inicio import InicioApp

class LoginApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ruta_ui = os.path.join(os.path.dirname(__file__), "proyecto.ui")  # Ruta dinámica al archivo UI
        if not os.path.exists(ruta_ui):
            QMessageBox.critical(self, "Error", f"No se encontró el archivo UI en: {ruta_ui}")
            sys.exit(1)
        uic.loadUi(ruta_ui, self)
       
        # Conectar el botón y la tecla Enter a la función de validación
        self.pushButton_2.clicked.connect(self.validar_login)
        self.lineEdit_4.returnPressed.connect(self.validar_login)  # Usuario
        self.lineEdit_3.returnPressed.connect(self.validar_login)  # Contraseña

        self.usuario_id = None  # Almacena el ID del usuario logueado

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
        self.ventana_inicio = InicioApp(self.usuario_id)  
        self.ventana_inicio.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec_())