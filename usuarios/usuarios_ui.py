from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QMessageBox, QScrollArea
from PyQt5.QtCore import Qt
from usuarios.cart_window import CartWindow
from usuarios.productos import cargar_productos
from usuarios.conectar_bd import conectar_bd
from usuarios.configuracion_window import ConfiguracionWindow  # Nueva ventana para configuración


class UsuarioApp(QMainWindow):
    def __init__(self, usuario_id):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.setGeometry(100, 100, 800, 600)

        self.usuario_id = usuario_id  # ID del usuario logueado
        self.nombre_usuario = self.get_username()  # Obtener el username desde la base de datos
        self.products = []  # Lista para almacenar productos desde la BD

        # Configuración de fondo
        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet("background-color: #e6f7ff;")  # Fondo azul suave
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.layout = QVBoxLayout(self.central_widget)

        # Mensaje de bienvenida
        self.welcome_label = QLabel(f"¡Bienvenido, {self.nombre_usuario}!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #0275d8; margin-bottom: 20px;")
        self.layout.addWidget(self.welcome_label)

        # Título
        self.title_label = QLabel("Productos Disponibles")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333;")
        self.layout.addWidget(self.title_label)

        # Scroll para la tabla de productos
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        # Tabla de productos
        self.products_layout = QVBoxLayout()
        self.scroll_layout.addLayout(self.products_layout)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Botón de ver carrito
        self.cart_button = QPushButton("Ver Carrito")
        self.cart_button.setStyleSheet("""
            font-size: 16px; 
            padding: 10px; 
            background-color: #5cb85c; 
            color: white; 
            border-radius: 5px; 
            margin-top: 10px;
        """)
        self.cart_button.clicked.connect(self.open_cart_window)
        self.layout.addWidget(self.cart_button, alignment=Qt.AlignRight)

        # Cargar productos desde la base de datos
        self.load_products_from_db()

    def get_username(self):
        """Obtiene el nombre de usuario desde la base de datos."""
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT username FROM users WHERE id = %s"
                cursor.execute(query, (self.usuario_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]  # Retorna el username
                else:
                    QMessageBox.warning(self, "Error", "Usuario no encontrado.")
                    self.close()
            except Exception as err:
                QMessageBox.critical(self, "Error", f"Error al obtener el username: {err}")
                self.close()
            finally:
                cursor.close()
                conexion.close()
        return "Usuario"

    def load_products_from_db(self):
        """Cargar productos desde la base de datos."""
        self.products = cargar_productos()
        for product in self.products:
            self.add_product_widget(product)

    def add_product_widget(self, product):
        product_id, product_name, product_price = product

        # Contenedor del producto
        product_widget = QWidget()
        product_widget.setStyleSheet("""
            background-color: white; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 15px; 
            margin: 5px 0;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        """)
        product_layout = QHBoxLayout(product_widget)

        # Nombre del producto
        name_label = QLabel(product_name)
        name_label.setStyleSheet("font-size: 16px; color: #333;")
        product_layout.addWidget(name_label)

        # Precio del producto
        price_label = QLabel(f"${product_price:.2f}")
        price_label.setStyleSheet("font-size: 16px; color: #555; margin-left: 20px;")
        product_layout.addWidget(price_label)

        # Botón de añadir al carrito
        add_button = QPushButton("Añadir")
        add_button.setStyleSheet("""
            font-size: 14px; 
            background-color: #0275d8; 
            color: white; 
            border-radius: 5px; 
            padding: 5px 10px;
        """)
        add_button.clicked.connect(lambda: self.add_to_cart(product))
        product_layout.addWidget(add_button)

        self.products_layout.addWidget(product_widget)

    def add_to_cart(self, product):
        product_id, product_name, product_price = product
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()

                # Verificar si el producto ya está en el carrito
                query_check = """
                SELECT cantidad FROM carritos WHERE usuario_id = %s AND producto_id = %s
                """
                cursor.execute(query_check, (self.usuario_id, product_id))
                result = cursor.fetchone()

                if result:
                    # Si ya está en el carrito, actualizar la cantidad
                    nueva_cantidad = result[0] + 1  # Incrementar cantidad en 1
                    query_update = """
                    UPDATE carritos SET cantidad = %s WHERE usuario_id = %s AND producto_id = %s
                    """
                    cursor.execute(query_update, (nueva_cantidad, self.usuario_id, product_id))
                    conexion.commit()
                    QMessageBox.information(self, "Carrito", f"{product_name} actualizado en el carrito. Cantidad: {nueva_cantidad}")
                else:
                    # Si no está en el carrito, insertar un nuevo registro
                    query_insert = """
                    INSERT INTO carritos (usuario_id, producto_id, cantidad)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(query_insert, (self.usuario_id, product_id, 1))  # Cantidad inicial 1
                    conexion.commit()
                    QMessageBox.information(self, "Carrito", f"{product_name} añadido al carrito.")
            except Exception as err:
                QMessageBox.critical(self, "Error", f"Error al añadir al carrito: {err}")
            finally:
                cursor.close()
                conexion.close()

    def open_cart_window(self):
        cart_window = CartWindow(self.usuario_id, self)
        cart_window.exec_()

    def open_config_window(self):
        config_window = ConfiguracionWindow(self.usuario_id, self.nombre_usuario, self)
        config_window.exec_()
