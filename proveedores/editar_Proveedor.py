import mysql.connector
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
import os
import re

class EditarProveedorWindow(QMainWindow):
    closed = pyqtSignal() 

    def __init__(self, proveedor_id):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'editar_Proveedor.ui')
        loadUi(ui_path, self)

        self.proveedor_id = proveedor_id  # ID del proveedor a editar
        self.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        self.btnCancelar.clicked.connect(self.close)

        # Cargar datos del proveedor en los campos de la interfaz
        self.cargar_datos_proveedor()
        
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def conectar(self):
        try:
            conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='login_db'
            )
            return conexion
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {str(e)}")
            return None

    def validar_correo(self, correo):
        regex = r"^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
        return re.match(regex, correo)

    def validar_telefono(self, telefono):
        return len(telefono) == 10 and telefono.isdigit()

    def validar_campos(self):
        """
        Valida que los campos no estén vacíos y que el correo y teléfono tengan el formato correcto.
        """
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

    def cargar_datos_proveedor(self):
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT * FROM proveedores WHERE id = %s"
                cursor.execute(query, (self.proveedor_id,))
                proveedor = cursor.fetchone()

                if proveedor:
                    # Mostrar datos en los campos correspondientes
                    self.lineEditId.setText(str(proveedor['id']))
                    self.lineEditNombre.setText(proveedor['nombre'])
                    self.lineEditVinculacion.setText(proveedor['vinculacion'])
                    self.lineEditCorreo.setText(proveedor['correo'])
                    self.lineEditTelefono.setText(proveedor['telefono'])
                    self.lineEditDireccion.setText(proveedor['direccion'])
                    self.dateEditFechaRegistro.setDate(proveedor['fecha_registro'])
                else:
                    QMessageBox.warning(self, "Error", "Proveedor no encontrado.")
                    self.close()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {str(e)}")
                self.close()
            finally:
                cursor.close()
                conexion.close()

    def validar_duplicados(self, nombre, correo, telefono):
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Verificar si el nombre ya existe, excluyendo el proveedor actual
                cursor.execute("SELECT * FROM proveedores WHERE nombre = %s AND id != %s", (nombre, self.proveedor_id))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "El nombre del proveedor ya existe.")
                    return True

                # Verificar si el correo ya existe, excluyendo el proveedor actual
                cursor.execute("SELECT * FROM proveedores WHERE correo = %s AND id != %s", (correo, self.proveedor_id))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "El correo del proveedor ya existe.")
                    return True

                # Verificar si el teléfono ya existe, excluyendo el proveedor actual
                cursor.execute("SELECT * FROM proveedores WHERE telefono = %s AND id != %s", (telefono, self.proveedor_id))
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


    def guardar_cambios(self):
        # Validar los campos
        if not self.validar_campos():
            return

        # Obtener valores de los campos
        nombre = self.lineEditNombre.text().strip()
        vinculacion = self.lineEditVinculacion.text().strip()
        correo = self.lineEditCorreo.text().strip()
        telefono = self.lineEditTelefono.text().strip()
        direccion = self.lineEditDireccion.text().strip()
        fecha_registro = self.dateEditFechaRegistro.date().toString("yyyy-MM-dd")

        # Verificar si hay datos duplicados
        if self.validar_duplicados(nombre, correo, telefono):
            return

        # Confirmación antes de guardar
        confirm = QMessageBox.question(self, "Confirmación", 
                                       "¿Estás seguro de que deseas realizar las modificaciones?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            # Actualizar los datos del proveedor en la base de datos
            conexion = self.conectar()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    query = """
                        UPDATE proveedores
                        SET nombre = %s, vinculacion = %s, correo = %s, telefono = %s,
                            direccion = %s, fecha_registro = %s
                        WHERE id = %s
                    """
                    cursor.execute(query, (nombre, vinculacion, correo, telefono, direccion, fecha_registro, self.proveedor_id))
                    conexion.commit()

                    QMessageBox.information(self, "Éxito", "Los datos del proveedor han sido actualizados.")
                    self.close()
                except mysql.connector.Error as e:
                    QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {str(e)}")
                finally:
                    cursor.close()
                    conexion.close()
