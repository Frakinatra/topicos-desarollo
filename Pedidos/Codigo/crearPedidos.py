import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from Pedidos.Codigo.Conect import Conexion  # Conexión adaptada


class VentanaPedidos(QMainWindow):
    regresar_signal = pyqtSignal()  # Señal para regresar a la ventana principal

    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id  # ID del usuario en sesión
        self.productos_seleccionados = []  # Array para almacenar productos seleccionados

        try:
            # Ruta al archivo .ui
            ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Interfaces/FormAddPedidos.ui"))
            if not os.path.exists(ui_path):
                raise FileNotFoundError(f"No se encontró el archivo .ui en la ruta: {ui_path}")
            uic.loadUi(ui_path, self)

            # Configuración inicial
            self.cargar_proveedores()
            self.comboProveedores.currentIndexChanged.connect(self.cargar_productos_por_proveedor)
            self.tableWidget_2.cellClicked.connect(self.seleccionar_producto)
            self.btn_addProducto.clicked.connect(self.agregar_producto_a_array)
            self.btn_AddPedido.clicked.connect(self.guardar_pedido)

            # Botón de cancelar
            self.btn_Cancelar.clicked.connect(self.cancelar_pedido)

            # Inicializar tabla de productos seleccionados
            self.tableWidget.setRowCount(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo inicializar la ventana de pedidos:\n{str(e)}")

    def cargar_proveedores(self):
        """Cargar proveedores en el combo box."""
        try:
            conexion = Conexion.conectar_bd()
            if not conexion:
                raise Exception("No se pudo establecer la conexión con la base de datos.")
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre FROM proveedores")
            proveedores = cursor.fetchall()
            self.comboProveedores.clear()
            for proveedor in proveedores:
                self.comboProveedores.addItem(proveedor[1], proveedor[0])
            conexion.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar proveedores:\n{str(e)}")

    def cargar_productos_por_proveedor(self):
        """Cargar productos del proveedor seleccionado en la tabla."""
        proveedor_id = self.comboProveedores.currentData()
        try:
            conexion = Conexion.conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id, nombre_producto, descripcion, precio 
                FROM productos 
                WHERE proveedor_id = %s
            """, (proveedor_id,))
            productos = cursor.fetchall()

            self.tableWidget_2.setRowCount(0)
            for row_idx, producto in enumerate(productos):
                self.tableWidget_2.insertRow(row_idx)
                for col_idx, value in enumerate(producto):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget_2.setItem(row_idx, col_idx, item)

            conexion.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar productos:\n{str(e)}")

    def seleccionar_producto(self, row, col):
        """Seleccionar un producto de la tabla."""
        producto_id = self.tableWidget_2.item(row, 0).text()
        nombre = self.tableWidget_2.item(row, 1).text()
        descripcion = self.tableWidget_2.item(row, 2).text()
        precio = self.tableWidget_2.item(row, 3).text()

        self.txt_ClaveProducto.setText(producto_id)
        self.txt_Nombre.setText(nombre)
        self.txt_descripcion.setPlainText(descripcion)
        self.txt_precio.setText(precio)

    def agregar_producto_a_array(self):
        """Agregar el producto seleccionado al array y mostrarlo en la tabla inferior."""
        producto_id = self.txt_ClaveProducto.text()
        nombre = self.txt_Nombre.text()
        descripcion = self.txt_descripcion.toPlainText()
        precio = float(self.txt_precio.text())
        cantidad = self.spinCantidad.value()
        subtotal = precio * cantidad

        if not producto_id or cantidad <= 0:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un producto válido y una cantidad mayor a 0.")
            return

        self.productos_seleccionados.append({
            "producto_id": producto_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "precio": precio,
            "cantidad": cantidad,
            "subtotal": subtotal
        })

        # Actualizar la tabla de productos seleccionados
        self.tableWidget.setRowCount(len(self.productos_seleccionados))
        for row_idx, producto in enumerate(self.productos_seleccionados):
            self.tableWidget.setItem(row_idx, 0, QTableWidgetItem(producto["nombre"]))
            self.tableWidget.setItem(row_idx, 1, QTableWidgetItem(str(producto["cantidad"])))
            self.tableWidget.setItem(row_idx, 2, QTableWidgetItem(f"${producto['precio']:.2f}"))
            self.tableWidget.setItem(row_idx, 3, QTableWidgetItem(f"${producto['subtotal']:.2f}"))

        # Actualizar el total general
        total_general = sum([p["subtotal"] for p in self.productos_seleccionados])
        self.labelTotal.setText(f"TOTAL: $ {total_general:.2f}")

    def guardar_pedido(self):
        """Guardar el pedido y los productos seleccionados en la base de datos."""
        if not self.productos_seleccionados:
            QMessageBox.warning(self, "Advertencia", "No hay productos seleccionados para el pedido.")
            return

        try:
            conexion = Conexion.conectar_bd()
            cursor = conexion.cursor()

            # Insertar el pedido
            total = sum([p["subtotal"] for p in self.productos_seleccionados])
            cursor.execute("""
                INSERT INTO pedidos (usuario_id, total, estatus) 
                VALUES (%s, %s, %s)
            """, (self.usuario_id, total, 'pendiente'))
            pedido_id = cursor.lastrowid

            # Insertar los productos en carritos
            for producto in self.productos_seleccionados:
                cursor.execute("""
                    INSERT INTO carritos (usuario_id, producto_id, cantidad, pedido_id) 
                    VALUES (%s, %s, %s, %s)
                """, (self.usuario_id, producto["producto_id"], producto["cantidad"], pedido_id))

            conexion.commit()
            QMessageBox.information(self, "Éxito", "El pedido se guardó correctamente.")
            self.close()
            self.regresar_signal.emit()
            conexion.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar el pedido:\n{str(e)}")

    def cancelar_pedido(self):
        """Cancelar la creación del pedido."""
        self.close()
        self.regresar_signal.emit()
