from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from usuarios.conectar_bd import conectar_bd
from Pedidos.Codigo.crearPedidos import VentanaPedidos
from usuarios.ProductosDisponiblesWindow import ProductosDisponiblesWindow
from usuarios.HistorialPedidosWindow import HistorialPedidosWindow


class UsuarioApp(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, usuario_id):
        super().__init__()
        self.setWindowTitle("Gestión de Pedidos")
        self.setGeometry(100, 100, 1200, 800)

        self.usuario_id = usuario_id
        self.nombre_usuario = self.get_username()

        # Configuración de fondo
        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet("background-color: #e6f7ff;")
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.layout = QVBoxLayout(self.central_widget)

        # Mensaje de bienvenida
        self.welcome_label = QLabel(f"¡Bienvenido, {self.nombre_usuario}!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #0275d8; margin-bottom: 20px;")
        self.layout.addWidget(self.welcome_label)

        # Título
        self.title_label = QLabel("Tus Pedidos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333;")
        self.layout.addWidget(self.title_label)

        # Tabla de pedidos
        self.table_pedidos = QTableWidget()
        self.table_pedidos.setColumnCount(4)
        self.table_pedidos.setHorizontalHeaderLabels(["ID", "Total", "Fecha", "Estatus"])
        self.table_pedidos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_pedidos.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border-radius: 8px;
                font-size: 16px;
            }
            QHeaderView::section {
                background-color: #0275d8;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 10px;
                text-align: center;
            }
        """)
        self.table_pedidos.itemSelectionChanged.connect(self.update_selected_pedido)
        self.layout.addWidget(self.table_pedidos)

        # Contenedor de botones de acción
        self.add_action_buttons()

        # Botones adicionales
        self.add_buttons()

        # Cargar pedidos
        self.load_pedidos()

        # Pedido seleccionado
        self.selected_pedido_id = None

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def get_username(self):
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT username FROM users WHERE id = %s"
                cursor.execute(query, (self.usuario_id,))
                result = cursor.fetchone()
                return result[0] if result else "Usuario"
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al obtener el usuario:\n{str(e)}")
            finally:
                cursor.close()
                conexion.close()
        return "Usuario"

    def load_pedidos(self):
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                SELECT id, total, fecha, estatus
                FROM pedidos
                WHERE usuario_id = %s
                AND estatus='pendiente'
                """
                cursor.execute(query, (self.usuario_id,))
                pedidos = cursor.fetchall()

                # Limpiar tabla antes de cargar
                self.table_pedidos.setRowCount(0)

                for row_idx, pedido in enumerate(pedidos):
                    self.table_pedidos.insertRow(row_idx)
                    for col_idx, value in enumerate(pedido):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table_pedidos.setItem(row_idx, col_idx, item)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar los pedidos:\n{str(e)}")
            finally:
                cursor.close()
                conexion.close()

    def update_selected_pedido(self):
        """Actualizar el ID del pedido seleccionado."""
        selected_items = self.table_pedidos.selectedItems()
        if selected_items:
            self.selected_pedido_id = int(selected_items[0].text())
        else:
            self.selected_pedido_id = None

    def add_action_buttons(self):
        """Agregar botones para acciones en pedidos seleccionados."""
        button_layout = QHBoxLayout()

        # Botón de ver detalles
        detail_button = QPushButton("Ver Detalles")
        detail_button.setStyleSheet("font-size: 14px; padding: 10px; background-color: #0275d8; color: white; border-radius: 5px;")
        detail_button.clicked.connect(self.show_order_details)
        button_layout.addWidget(detail_button)

        # Botón de cancelar pedido
        cancel_button = QPushButton("Cancelar Pedido")
        cancel_button.setStyleSheet("font-size: 14px; padding: 10px; background-color: #d9534f; color: white; border-radius: 5px;")
        cancel_button.clicked.connect(self.cancel_order)
        button_layout.addWidget(cancel_button)

        # Botón de marcar como completado
        complete_button = QPushButton("Marcar como Completado")
        complete_button.setStyleSheet("font-size: 14px; padding: 10px; background-color: #5cb85c; color: white; border-radius: 5px;")
        complete_button.clicked.connect(self.complete_order)
        button_layout.addWidget(complete_button)

        self.layout.addLayout(button_layout)

    def add_buttons(self):
        """Agregar botones de historial y productos disponibles."""
        button_layout = QHBoxLayout()

        # Botón de ver historial de pedidos
        history_button = QPushButton("Historial de Pedidos")
        history_button.setStyleSheet("font-size: 14px; padding: 10px; background-color: #0275d8; color: white; border-radius: 5px;")
        history_button.clicked.connect(self.open_history_window)
        button_layout.addWidget(history_button)

        # Botón de ver productos disponibles
        products_button = QPushButton("Productos Disponibles")
        products_button.setStyleSheet("font-size: 14px; padding: 10px; background-color: #5cb85c; color: white; border-radius: 5px;")
        products_button.clicked.connect(self.open_products_window)
        button_layout.addWidget(products_button)

        # Botón de realizar nuevo pedido
        new_order_button = QPushButton("Nuevo Pedido")
        new_order_button.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f0ad4e; color: white; border-radius: 5px;")
        new_order_button.clicked.connect(self.open_new_order_window)
        button_layout.addWidget(new_order_button)

        self.layout.addLayout(button_layout)

    def cancel_order(self):
        if not self.selected_pedido_id:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un pedido.")
            return

        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "UPDATE pedidos SET estatus = 'cancelado' WHERE id = %s"
                cursor.execute(query, (self.selected_pedido_id,))
                conexion.commit()
                QMessageBox.information(self, "Pedido Cancelado", f"El pedido {self.selected_pedido_id} ha sido cancelado.")
                self.load_pedidos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cancelar el pedido:\n{str(e)}")
            finally:
                cursor.close()
                conexion.close()

    def complete_order(self):
        if not self.selected_pedido_id:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un pedido.")
            return

        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "UPDATE pedidos SET estatus = 'completado' WHERE id = %s"
                cursor.execute(query, (self.selected_pedido_id,))
                conexion.commit()
                QMessageBox.information(self, "Pedido Completado", f"El pedido {self.selected_pedido_id} ha sido marcado como completado.")
                self.load_pedidos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al completar el pedido:\n{str(e)}")
            finally:
                cursor.close()
                conexion.close()

    def show_order_details(self):
        if not self.selected_pedido_id:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un pedido.")
            return

        try:
            self.details_window = DetallePedidoWindow(self.selected_pedido_id)
            self.details_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de detalles del pedido:\n{str(e)}")

    def open_new_order_window(self):
        try:
            self.new_order_window = VentanaPedidos(self.usuario_id)
            self.new_order_window.regresar_signal.connect(self.load_pedidos)
            self.new_order_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de nuevo pedido:\n{str(e)}")

    def open_products_window(self):
        try:
            self.products_window = ProductosDisponiblesWindow()
            self.products_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de productos disponibles:\n{str(e)}")

    def open_history_window(self):
        try:
            self.history_window = HistorialPedidosWindow(self.usuario_id)
            self.history_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de historial de pedidos:\n{str(e)}")


class DetallePedidoWindow(QMainWindow):
    def __init__(self, pedido_id):
        super().__init__()
        self.setWindowTitle(f"Detalles del Pedido {pedido_id}")
        self.setGeometry(200, 150, 800, 400)

        # Layout principal
        layout = QVBoxLayout()

        # Tabla de detalles
        self.table_detalles = QTableWidget()
        self.table_detalles.setColumnCount(3)
        self.table_detalles.setHorizontalHeaderLabels(["Producto", "Cantidad", "Subtotal"])
        self.table_detalles.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_detalles)

        # Cargar detalles del pedido
        self.load_detalles(pedido_id)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_detalles(self, pedido_id):
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                SELECT p.nombre_producto, c.cantidad, (c.cantidad * p.precio) AS subtotal
                FROM carritos c
                JOIN productos p ON c.producto_id = p.id
                WHERE c.pedido_id = %s
                """
                cursor.execute(query, (pedido_id,))
                detalles = cursor.fetchall()

                self.table_detalles.setRowCount(0)
                for row_idx, detalle in enumerate(detalles):
                    self.table_detalles.insertRow(row_idx)
                    for col_idx, value in enumerate(detalle):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table_detalles.setItem(row_idx, col_idx, item)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar los detalles del pedido:\n{str(e)}")
            finally:
                cursor.close()
                conexion.close()
