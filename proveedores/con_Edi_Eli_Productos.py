import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.uic import loadUi
import mysql.connector
from PyQt5.QtGui import QFont

from proveedores.editar_Producto import EditarProductoWindow

class GestionarProductosWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'con_Edi_Eli_Productos.ui')
        loadUi(ui_path, self)

        # Conectar señales
        self.comboBoxProveedor.currentIndexChanged.connect(self.cargar_productos)
        
        # Hacer que el QLabel actúe como botón
        self.regresar.setAttribute(Qt.WA_Hover, True)
        self.regresar.mousePressEvent = self.volver_anterior

        # Inicializar datos
        self.cargar_proveedores()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def volver_anterior(self, event):
        self.close()

    def conectar(self):
        """Establecer conexión con la base de datos."""
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

    def cargar_proveedores(self):
        """Carga la lista de proveedores en el comboBox."""
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT id, nombre FROM proveedores ORDER BY id ASC"
                cursor.execute(query)
                proveedores = cursor.fetchall()

                self.comboBoxProveedor.clear()
                for proveedor in proveedores:
                    self.comboBoxProveedor.addItem(proveedor[1], proveedor[0])  # Nombre como texto y ID como valor

                if proveedores:
                    self.comboBoxProveedor.setCurrentIndex(0)
                    self.cargar_productos()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar los proveedores: {err}")
            finally:
                cursor.close()
                conexion.close()

    def cargar_productos(self):
        """Carga los productos del proveedor seleccionado en la tabla."""
        proveedor_id = self.comboBoxProveedor.currentData()
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                    SELECT id, nombre_producto, descripcion, talla_disponible, precio, fecha_salida
                    FROM productos
                    WHERE proveedor_id = %s
                """
                cursor.execute(query, (proveedor_id,))
                productos = cursor.fetchall()

                self.tableWidgetProductos.clearContents()
                self.tableWidgetProductos.setRowCount(len(productos))
                self.tableWidgetProductos.setColumnCount(7)

                # Establecer encabezados de columna
                headers = ["ID Producto", "Nombre Producto", "Descripción", "Talla", "Precio", "Fecha Salida", "Acciones"]
                self.tableWidgetProductos.setHorizontalHeaderLabels(headers)

                # Ocultar la numeración automática
                self.tableWidgetProductos.verticalHeader().setVisible(False)

                for row_index, producto in enumerate(productos):
                    for col_index, value in enumerate(producto):
                        self.tableWidgetProductos.setItem(row_index, col_index, QTableWidgetItem(str(value)))

                    # Agregar botones de acciones
                    btn_editar = QPushButton("Editar")
                    # Establecer la fuente del botón
                    font = QFont("Arial Rounded MT Bold", 11)  # Fuente Arial Rounded MT Bold, tamaño 12
                    btn_editar.setFont(font)
                    btn_editar.setStyleSheet("""
                        QPushButton {
                            background-color: #ADD8E6; /* Azul pastel */
                            color: #000000; /* Color del texto: negro */
                        }
                        QPushButton:hover {
                            background-color: #87CEEB; /* Azul pastel más claro al pasar el cursor */
                        }
                    """)
                    btn_editar.clicked.connect(lambda _, prod_id=producto[0]: self.editar_producto(prod_id))

                    btn_eliminar = QPushButton("Eliminar")
                    # Establecer la fuente del botón
                    font = QFont("Arial Rounded MT Bold", 11)  # Fuente Arial Rounded MT Bold, tamaño 12
                    btn_eliminar.setFont(font)
                    btn_eliminar.setStyleSheet("""
                        QPushButton {
                            background-color: #FFB6C1; /* Rosa pastel */
                            color: #000000; /* Color del texto: negro */
                        }
                        QPushButton:hover {
                            background-color: #FF69B4; /* Rosa más brillante al pasar el cursor */
                        }
                    """)
                    btn_eliminar.clicked.connect(lambda _, prod_id=producto[0]: self.eliminar_producto(prod_id))

                    action_layout = QHBoxLayout()
                    action_layout.addWidget(btn_editar)
                    action_layout.addWidget(btn_eliminar)

                    action_widget = QWidget()
                    action_widget.setLayout(action_layout)
                    self.tableWidgetProductos.setCellWidget(row_index, 6, action_widget)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar los productos: {err}")
            finally:
                cursor.close()
                conexion.close()

    def editar_producto(self, producto_id):
        self.hide()
        self.ventana = EditarProductoWindow(producto_id)
        self.ventana.closed.connect(lambda: (self.show(), self.cargar_productos()))
        self.ventana.show()
        
    def eliminar_producto(self, producto_id):
        """Elimina un producto existente."""
        confirmacion = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este producto?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacion == QMessageBox.Yes:
            conexion = self.conectar()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    query = "DELETE FROM productos WHERE id = %s"
                    cursor.execute(query, (producto_id,))
                    conexion.commit()

                    QMessageBox.information(self, "Éxito", "Producto eliminado correctamente.")
                    self.cargar_productos()
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Error", f"Error al eliminar el producto: {err}")
                finally:
                    cursor.close()
                    conexion.close()

