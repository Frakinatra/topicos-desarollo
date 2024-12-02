from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialog, QMessageBox
from usuarios.conectar_bd import conectar_bd


class ConfiguracionWindow(QDialog):
    def __init__(self, usuario_id, nombre_usuario, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Usuario")
        self.setGeometry(150, 150, 400, 400)
        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario

        # Layout principal
        self.layout = QVBoxLayout(self)

        # Campo para actualizar el correo
        self.email_label = QLabel("Correo Electrónico:")
        self.email_input = QLineEdit(self)
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)

        # Campo para actualizar la contraseña
        self.password_label = QLabel("Nueva Contraseña:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)  # Ocultar texto al escribir
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        # Sección para insertar datos en user_profiles
        self.profile_label = QLabel("Registrar Datos Adicionales (Opcional)")
        self.layout.addWidget(self.profile_label)

        self.nombre_label = QLabel("Nombre:")
        self.nombre_input = QLineEdit(self)
        self.layout.addWidget(self.nombre_label)
        self.layout.addWidget(self.nombre_input)

        self.apellido_label = QLabel("Apellido:")
        self.apellido_input = QLineEdit(self)
        self.layout.addWidget(self.apellido_label)
        self.layout.addWidget(self.apellido_input)

        self.profile_email_label = QLabel("Correo (Profile):")
        self.profile_email_input = QLineEdit(self)
        self.layout.addWidget(self.profile_email_label)
        self.layout.addWidget(self.profile_email_input)

        self.profile_password_label = QLabel("Contraseña (Profile):")
        self.profile_password_input = QLineEdit(self)
        self.profile_password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.profile_password_label)
        self.layout.addWidget(self.profile_password_input)

        # Botones
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.save_button.setStyleSheet("background-color: #5cb85c; color: white; padding: 5px; border-radius: 5px;")
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("background-color: #d9534f; color: white; padding: 5px; border-radius: 5px;")
        self.cancel_button.clicked.connect(self.close)
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.buttons_layout)

        # Cargar datos actuales
        self.load_current_data()

    def load_current_data(self):
        """Carga los datos actuales del usuario desde la base de datos."""
        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()

                # Obtener datos de la tabla `users`
                query_users = "SELECT email FROM users WHERE id = %s"
                cursor.execute(query_users, (self.usuario_id,))
                user_data = cursor.fetchone()
                if user_data:
                    self.email_input.setText(user_data[0])  # Establecer el correo actual

                # Obtener datos de la tabla `user_profiles`
                query_profiles = """
                SELECT nombre, apellido, correo FROM user_profiles WHERE user_id = %s
                """
                cursor.execute(query_profiles, (self.usuario_id,))
                profile_data = cursor.fetchone()
                if profile_data:
                    self.nombre_input.setText(profile_data[0])  # Nombre
                    self.apellido_input.setText(profile_data[1])  # Apellido
                    self.profile_email_input.setText(profile_data[2])  # Correo del perfil
            except Exception as err:
                QMessageBox.critical(self, "Error", f"Error al cargar los datos: {err}")
            finally:
                cursor.close()
                conexion.close()

    def save_changes(self):
        """Guarda los cambios realizados por el usuario."""
        nuevo_email = self.email_input.text().strip()
        nueva_password = self.password_input.text().strip()

        # Datos para user_profiles
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        profile_email = self.profile_email_input.text().strip()
        profile_password = self.profile_password_input.text().strip()

        conexion = conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()

                # Actualizar correo y contraseña en `users`
                if nuevo_email or nueva_password:
                    query_users = """
                    UPDATE users SET 
                        email = COALESCE(%s, email), 
                        password = COALESCE(%s, password) 
                    WHERE id = %s
                    """
                    cursor.execute(query_users, (nuevo_email or None, nueva_password or None, self.usuario_id))

                # Insertar o actualizar datos en `user_profiles`
                query_profiles_check = "SELECT * FROM user_profiles WHERE user_id = %s"
                cursor.execute(query_profiles_check, (self.usuario_id,))
                profile_exists = cursor.fetchone()

                if profile_exists:
                    # Actualizar datos existentes
                    query_profiles_update = """
                    UPDATE user_profiles 
                    SET 
                        nombre = COALESCE(%s, nombre), 
                        apellido = COALESCE(%s, apellido), 
                        correo = COALESCE(%s, correo), 
                        password = COALESCE(%s, password) 
                    WHERE user_id = %s
                    """
                    cursor.execute(query_profiles_update, (nombre or None, apellido or None, profile_email or None, profile_password or None, self.usuario_id))
                elif profile_email and nombre and apellido and profile_password:
                    # Insertar nuevos datos
                    query_profiles_insert = """
                    INSERT INTO user_profiles (user_id, nombre, apellido, correo, password)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query_profiles_insert, (self.usuario_id, nombre, apellido, profile_email, profile_password))

                conexion.commit()
                QMessageBox.information(self, "Éxito", "Información actualizada correctamente.")
                self.close()
            except Exception as err:
                QMessageBox.critical(self, "Error", f"Error al actualizar la información: {err}")
            finally:
                cursor.close()
                conexion.close()
