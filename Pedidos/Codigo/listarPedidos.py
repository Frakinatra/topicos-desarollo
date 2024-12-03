import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

# Ruta al archivo .ui
ui_path = "./Interfaces/FormConsultarPedidos.ui"

class VentanaPedidos(QMainWindow):
    def __init__(self):
        super().__init__()
        # Cargar el diseño de la ventana desde el archivo .ui
        uic.loadUi(ui_path, self)

        self.btn_buscar.clicked.connect(self.buscar_pedido)

    # Función para manejar el evento del botón "Buscar"
    def buscar_pedido(self):
        # Obtén el texto ingresado en el campo de clave del pedido
        clave_pedido = self.txtClavePedido.text()  # input_clave es el nombre del campo en el archivo .ui
        if clave_pedido:
            QMessageBox.information(self, "Buscar Pedido", f"Buscando el pedido con clave: {clave_pedido}")
        else:
            QMessageBox.warning(self, "Error", "Por favor, ingresa una clave de pedido.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPedidos()
    ventana.show()
    sys.exit(app.exec_())