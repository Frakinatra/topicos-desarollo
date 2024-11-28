import sys
import mysql.connector
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

class LoginApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('proyecto.ui', self)  # Cargar la interfaz principal
        
        # Conectar el botón de iniciar sesión con la función
        self.pushButton.clicked.connect(self.validar_login)  # Botón "Iniciar sesión"

    def conectar(self):
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
        username = self.textEdit.toPlainText().strip()
        password = self.textEdit_2.toPlainText().strip()

        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()

                if user:
                    QMessageBox.information(self, "Éxito", f"¡Bienvenido, {username}!")
                    self.abrir_inicio()  # Llamar a la función que abre la ventana principal de la app
                else:
                    QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de consulta", f"Error: {err}")
            finally:
                cursor.close()
                conexion.close()

    def abrir_inicio(self):
        # Crear una instancia de la ventana principal de la app
        self.ventana_inicio = InicioApp()  
        # Mostrar la ventana principal de la app
        self.ventana_inicio.show()
        # Cerrar la ventana de login
        self.close()

class InicioApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('inicio.ui', self)  # Cargar la interfaz principal de la app

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec_())