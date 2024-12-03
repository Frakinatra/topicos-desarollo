import mysql.connector
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.uic import loadUi
import os

class EditarProductoWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, producto_id):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'editar_Producto.ui')
        loadUi(ui_path, self)

        # Conectar botones
        self.btnGuardar.clicked.connect(self.guardar_producto)
        self.btnCancelar.clicked.connect(self.close)

        # Inicializar el ID del producto
        self.producto_id = producto_id
        
        # Hacer que el QLabel actúe como botón
        self.regresar.setAttribute(Qt.WA_Hover, True)
        self.regresar.mousePressEvent = self.volver_anterior

        # Cargar datos del producto
        self.cargar_datos_producto()

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

    def cargar_datos_producto(self):
        if not self.producto_id:
            QMessageBox.critical(self, "Error", "No se proporcionó un ID de producto para editar.")
            self.close()
            return

        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT * FROM productos WHERE id = %s"
                cursor.execute(query, (self.producto_id,))
                producto = cursor.fetchone()

                if producto:
                    # Cargar datos en los campos
                    self.lineEditIDProducto.setText(str(producto['id']))
                    self.lineEditNombreProducto.setText(producto['nombre_producto'])
                    self.textEditDescripcion.setPlainText(producto['descripcion'])
                    self.lineEditTalla.setText(producto['talla_disponible'])
                    self.lineEditPrecio.setText(str(producto['precio']))
                    self.dateEditFechaSalida.setDate(producto['fecha_salida'])

                    # Cargar listas desplegables de proveedor y categoría
                    self.cargar_datos_combobox(proveedor_id=producto['proveedor_id'], categoria_id=producto['categoria_id'])
                else:
                    QMessageBox.warning(self, "Error", "No se encontró el producto.")
                    self.close()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar el producto: {err}")
            finally:
                cursor.close()
                conexion.close()

    def cargar_datos_combobox(self, proveedor_id=None, categoria_id=None):
        # Cargar proveedores
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query_proveedor = "SELECT id, nombre FROM proveedores ORDER BY id ASC"
                cursor.execute(query_proveedor)
                proveedores = cursor.fetchall()
                for proveedor in proveedores:
                    self.comboBoxProveedor.addItem(proveedor[1], proveedor[0])
                if proveedor_id:
                    index = self.comboBoxProveedor.findData(proveedor_id)
                    self.comboBoxProveedor.setCurrentIndex(index)
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
                query_categoria = "SELECT id, nombre_categoria FROM categorias ORDER BY id ASC"
                cursor.execute(query_categoria)
                categorias = cursor.fetchall()
                for categoria in categorias:
                    self.comboBoxCategoria.addItem(categoria[1], categoria[0])
                if categoria_id:
                    index = self.comboBoxCategoria.findData(categoria_id)
                    self.comboBoxCategoria.setCurrentIndex(index)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar las categorías: {err}")
            finally:
                cursor.close()
                conexion.close()

    def guardar_producto(self):
        # Mostrar un mensaje de confirmación
        confirmacion = QMessageBox.question(
            self,
            "Confirmación",
            "¿Estás seguro de que deseas realizar las modificaciones?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Si el usuario selecciona "No", salir del método
        if confirmacion == QMessageBox.No:
            return

        # Validación de campos
        if not self.validar_campos():
            return

        # Guardar cambios
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                    UPDATE productos 
                    SET nombre_producto = %s, descripcion = %s, talla_disponible = %s, precio = %s, 
                        proveedor_id = %s, categoria_id = %s, fecha_salida = %s
                    WHERE id = %s
                """
                datos = (
                    self.lineEditNombreProducto.text().strip(),
                    self.textEditDescripcion.toPlainText().strip(),
                    self.lineEditTalla.text().strip(),
                    float(self.lineEditPrecio.text().strip()),
                    self.comboBoxProveedor.currentData(),
                    self.comboBoxCategoria.currentData(),
                    self.dateEditFechaSalida.date().toString("yyyy-MM-dd"),
                    self.producto_id
                )
                cursor.execute(query, datos)
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
                self.close()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al guardar el producto: {err}")
            finally:
                cursor.close()
                conexion.close()


    def validar_campos(self):
        if not self.lineEditNombreProducto.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Nombre no puede estar vacío.")
            return False
        if not self.textEditDescripcion.toPlainText().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Descripción no puede estar vacío.")
            return False
        if not self.lineEditTalla.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Talla no puede estar vacío.")
            return False
        if not self.lineEditPrecio.text().strip():
            QMessageBox.warning(self, "Campo vacío", "El campo Precio no puede estar vacío.")
            return False
        try:
            float(self.lineEditPrecio.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "El campo Precio debe ser un número válido.")
            return False
        return True
