import mysql.connector
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
import os
from datetime import datetime
import re  # Importar el módulo re para la validación del correo electrónico

class AgregarProveedorWindow(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agregar_Proveedor.ui')
        loadUi(ui_path, self)

        self.btnGuardar.clicked.connect(self.guardar_proveedor)
        self.btnCancelar.clicked.connect(self.close)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()  # Aceptar el evento de cierre para que la ventana se cierre

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

    def validar_correo(self, correo):
        regex = r"^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
        return re.match(regex, correo)

    def validar_telefono(self, telefono):
        return len(telefono) == 10 and telefono.isdigit()

    def validar_campos(self):
        # Validación de campos vacíos
        if not self.lineEditNombre.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Nombre no puede estar vacío.")
            return False
        if not self.lineEditVinculacion.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Vinculación no puede estar vacío.")
            return False
        if not self.lineEditCorreo.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Correo no puede estar vacío.")
            return False
        if not self.lineEditTelefono.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Teléfono no puede estar vacío.")
            return False
        if not self.lineEditDireccion.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Dirección no puede estar vacío.")
            return False

        # Validación del formato del correo electrónico
        correo = self.lineEditCorreo.text().strip()
        if not self.validar_correo(correo):
            QMessageBox.warning(self, "Correo inválido", "El correo no cumple con el formato válido.")
            return False

        # Validación de la longitud del teléfono
        telefono = self.lineEditTelefono.text().strip()
        if not self.validar_telefono(telefono):
            QMessageBox.warning(self, "Teléfono inválido", "El teléfono debe tener 10 dígitos y ser numérico.")
            return False

        return True

    def validar_duplicados(self, nombre, correo, telefono):
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Verificar si el nombre ya existe
                cursor.execute("SELECT * FROM proveedores WHERE nombre = %s", (nombre,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "El nombre del proveedor ya existe.")
                    return True

                # Verificar si el correo ya existe
                cursor.execute("SELECT * FROM proveedores WHERE correo = %s", (correo,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "El correo del proveedor ya existe.")
                    return True

                # Verificar si el teléfono ya existe
                cursor.execute("SELECT * FROM proveedores WHERE telefono = %s", (telefono,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "El teléfono del proveedor ya existe.")
                    return True

                return False
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de consulta", f"Error: {err}")
                return True
            finally:
                cursor.close()
                conexion.close()

    def guardar_proveedor(self):
        # Validar campos
        if not self.validar_campos():
            return

        # Obtener los datos de los campos
        nombre = self.lineEditNombre.text().strip()
        vinculacion = self.lineEditVinculacion.text().strip()
        correo = self.lineEditCorreo.text().strip()
        telefono = self.lineEditTelefono.text().strip()
        direccion = self.lineEditDireccion.text().strip()
        
        # Obtener la fecha actual en formato 'YYYY-MM-DD'
        fecha_registro = datetime.now().strftime('%Y-%m-%d')

        # Validar duplicados
        if self.validar_duplicados(nombre, correo, telefono):
            return

        # Insertar proveedor en la base de datos
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO proveedores (nombre, vinculacion, correo, telefono, direccion, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (nombre, vinculacion, correo, telefono, direccion, fecha_registro))
                conexion.commit()

                QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente.")
                self.close()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de inserción", f"Error: {err}")
            finally:
                cursor.close()
                conexion.close()
