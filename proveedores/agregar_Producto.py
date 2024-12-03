import mysql.connector
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.uic import loadUi
import os
from datetime import datetime

class AgregarProductoWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agregar_Producto.ui')
        loadUi(ui_path, self)

        # Conectar botones
        self.btnGuardarProducto.clicked.connect(self.guardar_producto)
        self.btnCancelar.clicked.connect(self.close)
        
        # Hacer que el QLabel actúe como botón
        self.regresar.setAttribute(Qt.WA_Hover, True)
        self.regresar.mousePressEvent = self.volver_anterior

        # Cargar proveedores y categorías en los combo boxes
        self.cargar_datos_combobox()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def volver_anterior(self, event):
        self.close()

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

    def cargar_datos_combobox(self):
        # Cargar proveedores
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Cargar proveedores ordenados por ID
                query_proveedor = "SELECT id, nombre FROM proveedores ORDER BY id ASC"
                cursor.execute(query_proveedor)
                proveedores = cursor.fetchall()
                for proveedor in proveedores:
                    self.comboBoxProveedor.addItem(proveedor[1], proveedor[0])  # Agregar nombre como texto y ID como valor
                self.comboBoxProveedor.setCurrentIndex(0)  # Seleccionar el primer valor
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar los proveedores: {err}")
            finally:
                cursor.close()
                conexion.close()

        # Cargar categorías
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Cargar categorías ordenadas por ID
                query_categoria = "SELECT id, nombre_categoria FROM categorias ORDER BY id ASC"
                cursor.execute(query_categoria)
                categorias = cursor.fetchall()
                for categoria in categorias:
                    self.comboBoxCategoria.addItem(categoria[1], categoria[0])  # Agregar nombre_categoria como texto y ID como valor
                self.comboBoxCategoria.setCurrentIndex(0)  # Seleccionar el primer valor
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar las categorías: {err}")
            finally:
                cursor.close()
                conexion.close()

    def validar_campos_producto(self):
        # Validación de campos vacíos
        if not self.lineEditNombreProducto.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Nombre del Producto no puede estar vacío.")
            return False
        if not self.textEditDescripcion.toPlainText().strip():  # Aquí se cambia el nombre del objeto
            QMessageBox.warning(self, "Campo vacío", "El campo Descripción no puede estar vacío.")
            return False
        if self.doubleSpinBoxPrecioProducto.value() == 0:
            QMessageBox.warning(self, "Campo vacío", "El campo Precio no puede estar vacío.")
            return False
        if not self.lineEditTallaProducto.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Talla no puede estar vacío.")
            return False
        if not self.dateEditFechaSalida.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Fecha de Salida no puede estar vacío.")
            return False

        # Validación de la fecha en formato yyyy-MM-dd
        fecha_salida = self.dateEditFechaSalida.text().strip()
        try:
            fecha_obj = datetime.strptime(fecha_salida, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Fecha inválida", "El formato de la fecha debe ser yyyy-MM-dd.")
            return False

        return True

    def guardar_producto(self):
        # Validar campos
        if not self.validar_campos_producto():
            return

        # Obtener los datos de los campos
        nombre_producto = self.lineEditNombreProducto.text().strip()
        descripcion_producto = self.textEditDescripcion.toPlainText().strip()  # Aquí se cambia el nombre del objeto
        proveedor_id = self.comboBoxProveedor.currentData()  # Obtener el ID del proveedor
        categoria_id = self.comboBoxCategoria.currentData()  # Obtener el ID de la categoría
        talla = self.lineEditTallaProducto.text().strip()
        precio = self.doubleSpinBoxPrecioProducto.value()  # Obtener el valor del precio
        fecha_salida = self.dateEditFechaSalida.text().strip()

        # Conectar a la base de datos
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Insertar producto en la base de datos
                query = """
                INSERT INTO productos (nombre_producto, descripcion, proveedor_id, categoria_id, talla_disponible, precio, fecha_salida)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (nombre_producto, descripcion_producto, proveedor_id, categoria_id, talla, precio, fecha_salida))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Producto agregado exitosamente.")
                self.close()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al guardar el producto: {err}")
            finally:
                cursor.close()
                conexion.close()
