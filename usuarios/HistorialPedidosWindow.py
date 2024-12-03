from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from usuarios.conectar_bd import conectar_bd


class HistorialPedidosWindow(QMainWindow):
    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id  # ID del usuario
        self.setWindowTitle("Historial de Pedidos")
        self.setGeometry(200, 150, 1000, 600)

        # Widget principal
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Título
        self.title_label = QLabel("Historial de Pedidos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333;")
        self.layout.addWidget(self.title_label)

        # Barra de filtros
        self.add_filter_bar()

        # Tabla de pedidos
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Total", "Fecha", "Estatus", "Acción"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setStyleSheet("""
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
        self.layout.addWidget(self.orders_table)

        # Cargar pedidos iniciales
        self.load_orders()

    def add_filter_bar(self):
        """Agregar barra de filtros para buscar pedidos."""
        filter_layout = QHBoxLayout()

        # Campo de texto para filtro
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrar por ID o Estatus")
        self.filter_input.setStyleSheet("padding: 5px; font-size: 16px;")
        filter_layout.addWidget(self.filter_input)

        # Botón de aplicar filtro
        filter_button = QPushButton("Aplicar Filtro")
        filter_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: #5cb85c; color: white; border-radius: 5px;")
        filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(filter_button)

        self.layout.addLayout(filter_layout)

    def load_orders(self, filtro=None):
        """Cargar pedidos desde la base de datos."""
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Consulta base
                query = """
                SELECT id, total, fecha, estatus
                FROM pedidos
                WHERE usuario_id = %s
                """

                # Agregar filtro si existe
                if filtro:
                    query += " AND (id LIKE %s OR estatus LIKE %s)"
                    filtro_valor = f"%{filtro}%"
                    cursor.execute(query, (self.usuario_id, filtro_valor, filtro_valor))
                else:
                    cursor.execute(query, (self.usuario_id,))

                pedidos = cursor.fetchall()

                # Limpiar tabla antes de cargar
                self.orders_table.setRowCount(0)

                for row_idx, pedido in enumerate(pedidos):
                    self.orders_table.insertRow(row_idx)
                    for col_idx, value in enumerate(pedido):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.orders_table.setItem(row_idx, col_idx, item)

                    # Botón de ver detalles
                    detail_button = QPushButton("Ver Detalles")
                    detail_button.setStyleSheet("""
                        font-size: 14px; 
                        padding: 8px; 
                        background-color: #0275d8; 
                        color: white; 
                        border-radius: 5px;
                    """)
                    detail_button.clicked.connect(lambda _, id=pedido[0]: self.show_order_details(id))
                    self.orders_table.setCellWidget(row_idx, 4, detail_button)

            except Exception as err:
                QMessageBox.critical(self, "Error", f"Error al cargar los pedidos: {err}")
            finally:
                cursor.close()
                conexion.close()

    def apply_filter(self):
        """Aplicar filtro basado en el texto ingresado."""
        filtro = self.filter_input.text().strip()
        self.load_orders(filtro=filtro if filtro else None)

    def show_order_details(self, pedido_id):
        """Abrir una nueva ventana para mostrar los detalles del pedido."""
        try:
            self.details_window = DetallePedidoWindow(pedido_id)
            self.details_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de detalles del pedido:\n{str(e)}")


class DetallePedidoWindow(QMainWindow):
    def __init__(self, pedido_id):
        super().__init__()
        self.setWindowTitle(f"Detalles del Pedido {pedido_id}")
        self.setGeometry(200, 200, 800, 600)

        # Crear layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Cargar productos del pedido
        self.load_details(pedido_id)

    def load_details(self, pedido_id):
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

                # Crear tabla
                table = QTableWidget(len(detalles), 3)
                table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Subtotal"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                for row, detalle in enumerate(detalles):
                    for col, value in enumerate(detalle):
                        item = QTableWidgetItem(str(value))
                        table.setItem(row, col, item)

                self.setCentralWidget(table)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar los detalles del pedido:\n{str(e)}")
            finally:
                cursor.close()
                conexion.close()
