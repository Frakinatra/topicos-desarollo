import sys
import mysql.connector
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

class LoginApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('proyecto.ui', self) 
       
        self.pushButton.clicked.connect(self.validar_login)  

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
        username = self.lineEdit.text().strip()   # Obtener el texto del QLineEdit
        password = self.lineEdit_2.text().strip()  # Obtener el texto del QLineEdit
        
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()

                if user:
                    QMessageBox.information(self, "Éxito", f"¡Bienvenido, {username}!")
                    self.abrir_inicio()  
                else:
                    QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de consulta", f"Error: {err}")
            finally:
                cursor.close()
                conexion.close()

    def abrir_inicio(self):
        
        self.ventana_inicio = InicioApp()  
        
        self.ventana_inicio.show()
        
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