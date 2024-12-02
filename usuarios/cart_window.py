from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QDialog, QLabel, QMessageBox
from PyQt5.QtCore import Qt
import mysql.connector
from usuarios.conectar_bd import conectar_bd


class CartWindow(QDialog):
    def __init__(self, usuario_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carrito de Compras")
        self.setGeometry(150, 150, 500, 500)
        
        self.usuario_id = usuario_id
        self.cart_items = []

        # Configuración de fondo
        self.setStyleSheet("background-color: #f5f5f5;")  # Fondo gris claro

        # Layout principal
        self.layout = QVBoxLayout(self)

        # Título
        self.title_label = QLabel("Mi Carrito de Compras")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 15px;")
        self.layout.addWidget(self.title_label)

        # Lista de productos en el carrito
        self.cart_list = QListWidget()
        self.cart_list.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
        """)
        self.layout.addWidget(self.cart_list)

        # Botones de acción
        self.actions_layout = QHBoxLayout()

        # Botón para eliminar seleccionado
        self.remove_button = QPushButton("Eliminar Seleccionado")
        self.remove_button.setStyleSheet("""
            font-size: 14px;
            background-color: #d9534f;
            color: white;
            border-radius: 5px;
            padding: 8px 12px;
        """)
        self.remove_button.clicked.connect(self.remove_selected_item)
        self.actions_layout.addWidget(self.remove_button)

        # Botón para vaciar carrito
        self.clear_button = QPushButton("Vaciar Carrito")
        self.clear_button.setStyleSheet("""
            font-size: 14px;
            background-color: #5cb85c;
            color: white;
            border-radius: 5px;
            padding: 8px 12px;
        """)
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
