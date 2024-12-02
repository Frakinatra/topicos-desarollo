# Actualización del código para manejar la persistencia del carrito en la base de datos.
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QDialog, QWidget, QMessageBox
from PyQt5.QtCore import Qt

class UsuarioApp(QMainWindow):
    def __init__(self, usuario_id=1):  # Se espera recibir el usuario_id después del login
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.setGeometry(100, 100, 800, 600)
        
        self.products = []  # Lista para almacenar productos desde la BD
        self.usuario_id = usuario_id  # ID del usuario logueado
        
        # Layout principal
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Título
        self.title_label = QLabel("Lista de Productos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(self.title_label)
        
        # Contenedor de productos
        self.products_layout = QVBoxLayout()
        self.layout.addLayout(self.products_layout)
        
        # Botón de ver carrito
        self.cart_button = QPushButton("Ver Carrito")
        self.cart_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #5cb85c; color: white;")
        self.cart_button.clicked.connect(self.open_cart_window)
        self.layout.addWidget(self.cart_button, alignment=Qt.AlignRight)
        
        # Cargar productos desde la base de datos
        self.load_products_from_db()
    
    def connect_db(self):
        """Conexión a la base de datos."""
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="login_db"
            )
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de conexión", f"Error al conectar a la base de datos: {err}")
            return None
    
    def load_products_from_db(self):
        """Cargar productos desde la base de datos."""
        conexion = self.connect_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT id, nombre_producto, precio FROM productos"
                cursor.execute(query)
                self.products = cursor.fetchall()
                
                # Añadir productos a la interfaz
                for product in self.products:
                    self.add_product_widget(product)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al consultar productos: {err}")
            finally:
                cursor.close()
                conexion.close()
    
    def add_product_widget(self, product):
        product_id, product_name, product_price = product
        product_widget = QWidget()
        product_layout = QHBoxLayout(product_widget)
        
        # Nombre del producto
        name_label = QLabel(product_name)
        name_label.setStyleSheet("font-size: 18px;")
        product_layout.addWidget(name_label)
        
        # Precio del producto
        price_label = QLabel(f"${product_price:.2f}")
        price_label.setStyleSheet("font-size: 16px;")
        product_layout.addWidget(price_label)
        
        # Botón de añadir al carrito
        add_button = QPushButton("Añadir al carrito")
        add_button.setStyleSheet("font-size: 14px; background-color: #0275d8; color: white;")
        add_button.clicked.connect(lambda: self.add_to_cart(product))
        product_layout.addWidget(add_button)
        
        self.products_layout.addWidget(product_widget)
    
    def add_to_cart(self, product):
        product_id, product_name, product_price = product
        conexion = self.connect_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Insertar en la tabla carritos
                query = """
                INSERT INTO carritos (usuario_id, producto_id, cantidad)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (self.usuario_id, product_id, 1))  # Cantidad fija a 1 por ahora
                conexion.commit()
                QMessageBox.information(self, "Carrito", f"{product_name} añadido al carrito.")
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al añadir al carrito: {err}")
            finally:
                cursor.close()
                conexion.close()
    
    def open_cart_window(self):
        cart_window = CartWindow(self.usuario_id, self)
        cart_window.exec_()


class CartWindow(QDialog):
    def __init__(self, usuario_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carrito de Compras")
        self.setGeometry(150, 150, 400, 400)
        
        self.usuario_id = usuario_id
        self.cart_items = []
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        
        # Lista de productos en el carrito
        self.cart_list = QListWidget()
        self.layout.addWidget(self.cart_list)
        
        # Botones de acción
        self.actions_layout = QHBoxLayout()
        
        # Botón para eliminar seleccionado
        self.remove_button = QPushButton("Eliminar Seleccionado")
        self.remove_button.clicked.connect(self.remove_selected_item)
        self.actions_layout.addWidget(self.remove_button)
        
        # Botón para vaciar carrito
        self.clear_button = QPushButton("Vaciar Carrito")
        self.clear_button.clicked.connect(self.clear_cart)
        self.actions_layout.addWidget(self.clear_button)
        
        self.layout.addLayout(self.actions_layout)
        
        # Cargar productos del carrito desde la base de datos
        self.load_cart_from_db()
    
    def connect_db(self):
        """Conexión a la base de datos."""
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="login_db"
            )
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de conexión", f"Error al conectar a la base de datos: {err}")
            return None
    
    def load_cart_from_db(self):
        """Cargar productos del carrito desde la base de datos."""
        conexion = self.connect_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                SELECT p.id, p.nombre_producto, p.precio, c.cantidad
                FROM carritos c
                JOIN productos p ON c.producto_id = p.id
                WHERE c.usuario_id = %s
                """
                cursor.execute(query, (self.usuario_id,))
                self.cart_items = cursor.fetchall()
                self.update_cart_list()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al cargar el carrito: {err}")
            finally:
                cursor.close()
                conexion.close()
    
    def update_cart_list(self):
        self.cart_list.clear()
        for product_id, product_name, product_price, cantidad in self.cart_items:
            self.cart_list.addItem(f"{product_name} - ${product_price:.2f} x {cantidad}")
    
    def remove_selected_item(self):
        selected_item = self.cart_list.currentRow()
        if selected_item >= 0:
            product_id = self.cart_items[selected_item][0]
            conexion = self.connect_db()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    query = "DELETE FROM carritos WHERE usuario_id = %s AND producto_id = %s LIMIT 1"
                    cursor.execute(query, (self.usuario_id, product_id))
                    conexion.commit()
                    self.cart_items.pop(selected_item)
                    self.update_cart_list()
                    QMessageBox.information(self, "Carrito", "Producto eliminado del carrito.")
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Error", f"Error al eliminar el producto: {err}")
                finally:
                    cursor.close()
                    conexion.close()
    
    def clear_cart(self):
        conexion = self.connect_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "DELETE FROM carritos WHERE usuario_id = %s"
                cursor.execute(query, (self.usuario_id,))
                conexion.commit()
                self.cart_items.clear()
                self.update_cart_list()
                QMessageBox.information(self, "Carrito", "Carrito vaciado.")
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Error al vaciar el carrito: {err}")
            finally:
                cursor.close()
                conexion.close()


# Código ajustado para guardar y cargar el carrito desde la base de datos.
# Puedes integrarlo directamente en tu proyecto y probarlo en tu entorno local.
# app = QApplication([])
# main_window = UsuarioApp(usuario_id=1)
# main_window.show()
# app.exec_()
