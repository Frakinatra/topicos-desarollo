from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from usuarios.conectar_bd import conectar_bd


class ProductosDisponiblesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productos Disponibles")
        self.setGeometry(200, 150, 1000, 600)  # Tamaño de la ventana

        # Widget principal
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Título
        self.title_label = QLabel("Productos Disponibles")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333;")
        self.layout.addWidget(self.title_label)

        # Barra de filtros
        self.add_filter_bar()

        # Tabla de productos
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["ID", "Producto", "Descripción", "Talla", "Precio", "Proveedor"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setStyleSheet("""
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
        self.layout.addWidget(self.products_table)

        # Cargar productos iniciales
        self.load_products()

    def add_filter_bar(self):
        """Agregar barra de filtros para buscar productos."""
        filter_layout = QHBoxLayout()

        # Campo de texto para filtro
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrar por proveedor o ID")
        self.filter_input.setStyleSheet("padding: 5px; font-size: 16px;")
        filter_layout.addWidget(self.filter_input)

        # Botón de aplicar filtro
        filter_button = QPushButton("Aplicar Filtro")
        filter_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: #5cb85c; color: white; border-radius: 5px;")
        filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(filter_button)

        self.layout.addLayout(filter_layout)

    def load_products(self, filtro=None):
        """Cargar productos desde la base de datos."""
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Consulta base
                query = """
                SELECT p.id, p.nombre_producto, p.descripcion, p.talla_disponible, p.precio, pr.nombre AS proveedor
                FROM productos p
                JOIN proveedores pr ON p.proveedor_id = pr.id
                """

                # Agregar filtro si existe
                if filtro:
                    query += " WHERE p.id = %s OR pr.nombre LIKE %s"
                    filtro_proveedor = f"%{filtro}%"
                    cursor.execute(query, (filtro, filtro_proveedor))
                else:
                    cursor.execute(query)

                productos = cursor.fetchall()

                # Limpiar tabla antes de cargar
                self.products_table.setRowCount(0)

                for row_idx, producto in enumerate(productos):
                    self.products_table.insertRow(row_idx)
                    for col_idx, value in enumerate(producto):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.products_table.setItem(row_idx, col_idx, item)

            except Exception as err:
                QMessageBox.critical(self, "Error", f"Error al cargar los productos: {err}")
            finally:
                cursor.close()
                conexion.close()

    def apply_filter(self):
        """Aplicar filtro basado en el texto ingresado."""
        filtro = self.filter_input.text().strip()
        self.load_products(filtro=filtro if filtro else None)
