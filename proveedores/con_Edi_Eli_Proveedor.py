import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
import mysql.connector
from proveedores.editar_Proveedor import EditarProveedorWindow

class GestionarProveedoresWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Cargar la ruta completa del archivo UI
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'con_Edi_Eli_Proveedor.ui')
        loadUi(ui_path, self)

        # Cargar los datos iniciales
        self.cargar_proveedores()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

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
        """Carga los datos de los proveedores en la tabla."""
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT id, nombre, vinculacion, correo, telefono, direccion, fecha_registro FROM proveedores"
                cursor.execute(query)
                proveedores = cursor.fetchall()

                # Configurar la tabla
                self.tableWidgetProveedores.clearContents()
                self.tableWidgetProveedores.setRowCount(len(proveedores))
                self.tableWidgetProveedores.setColumnCount(8)

                # Establecer encabezados
                headers = ["ID Proveedor", "Nombre", "Vinculación", "Correo", "Teléfono", "Dirección", "Fecha Registro", "Acciones"]
                self.tableWidgetProveedores.setHorizontalHeaderLabels(headers)

                # Ocultar la numeración automática
                self.tableWidgetProveedores.verticalHeader().setVisible(False)

                for row_index, proveedor in enumerate(proveedores):
                    # Llenar columnas con datos
                    for col_index, value in enumerate(proveedor):
                        self.tableWidgetProveedores.setItem(row_index, col_index, QTableWidgetItem(str(value)))

                    # Agregar botones de acciones
                    btn_editar = QPushButton("Editar")
                    btn_editar.clicked.connect(lambda _, prov_id=proveedor[0]: self.editar_proveedor(prov_id))

                    btn_eliminar = QPushButton("Eliminar")
                    btn_eliminar.clicked.connect(lambda _, prov_id=proveedor[0]: self.eliminar_proveedor(prov_id))

                    action_layout = QHBoxLayout()
                    action_layout.addWidget(btn_editar)
                    action_layout.addWidget(btn_eliminar)

                    action_widget = QWidget()
                    action_widget.setLayout(action_layout)
                    self.tableWidgetProveedores.setCellWidget(row_index, len(proveedor), action_widget)  # Columna de acciones
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar los proveedores: {err}")
            finally:
                cursor.close()
                conexion.close()

    def editar_proveedor(self, proveedor_id):
        """Abre la ventana de edición para un proveedor."""
        self.hide()
        self.ventana = EditarProveedorWindow(proveedor_id)
        self.ventana.closed.connect(lambda: (self.show(), self.cargar_proveedores()))
        self.ventana.show()

    def eliminar_proveedor(self, proveedor_id):
        """Elimina un proveedor existente."""
        confirmacion = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este proveedor?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacion == QMessageBox.Yes:
            conexion = self.conectar()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    query = "DELETE FROM proveedores WHERE id = %s"
                    cursor.execute(query, (proveedor_id,))
                    conexion.commit()

                    QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente.")
                    self.cargar_proveedores()
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Error", f"Error al eliminar el proveedor: {err}")
                finally:
                    cursor.close()
                    conexion.close()
