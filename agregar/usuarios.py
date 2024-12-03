from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
import sys
sys.path.append("C:/Users/merti/Desktop/Proyecto t5/agregar")  # Ruta donde se encuentra conectar_bd.py
from conectar_bd import conectar_bd

class AgregarUsuario(QtWidgets.QMainWindow):
    def __init__(self, ventana_login):
        super().__init__()
        uic.loadUi("C:/Users/merti/Desktop/Proyecto t5/agregar/agregar_usuario.ui", self)  # Ruta completa

        # Guardar la referencia de la ventana de login
        self.ventana_login = ventana_login

        # Conectar los botones
        self.btnGuardar.clicked.connect(self.guardar_usuario)

        # Hacer que el QLabel actúe como botón al hacer clic
        self.regresar.mousePressEvent = self.regresar_a_ingreso

    def guardar_usuario(self):
        username = self.lineEditUsuario.text().strip()
        email = self.lineEditEmail.text().strip()
        password = self.lineEditPassword.text().strip()

        # Validar que todos los campos estén llenos
        if not username or not email or not password:
            QMessageBox.warning(self, "Campos vacíos", "Por favor, complete todos los campos.")
            return
        
        # Llamar a la función que agrega el usuario
        if self.agregar_usuario_db(username, email, password):
            QMessageBox.information(self, "Éxito", "Usuario agregado correctamente.")
            self.close()  # Cierra la ventana después de agregar el usuario
            if self.ventana_login:  # Verificar si la ventana de login está presente
                self.ventana_login.show()  # Muestra la ventana de login nuevamente
            else:
                QMessageBox.warning(self, "Error", "No se encontró la ventana de login.")
        else:
            QMessageBox.critical(self, "Error", "No se pudo agregar el usuario.")

    def agregar_usuario_db(self, username, email, password):
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, email, password))
                conexion.commit()  # Confirmar la transacción
                return True
            except Exception as e:
                print(f"Error al agregar usuario: {e}")
                conexion.rollback()  # Revertir la transacción si hay un error
                return False
            finally:
                cursor.close()
                conexion.close()

    def regresar_a_ingreso(self, event):
        """Regresar a la ventana de login cuando se hace clic en 'Regresar'"""
        self.close()  # Cerrar la ventana de agregar usuario
        if self.ventana_login:
            self.ventana_login.show()  # Muestra la ventana de login nuevamente
        else:
            QMessageBox.warning(self, "Error", "No se encontró la ventana de login.")


# Ejecución de la ventana
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana_agregar = AgregarUsuario(None)  # Aquí se pasa None porque no tienes acceso a LoginApp en este script
    ventana_agregar.show()  # Usamos show() en lugar de exec_()
    sys.exit(app.exec_())



