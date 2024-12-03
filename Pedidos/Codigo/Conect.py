import mysql.connector

class Conexion():

    def conectar_bd():

        try:
            conexion = mysql.connector.connect(
                host="localhost",       # Cambia si tu servidor MySQL está en otro host
                user="root",            # Usuario de la base de datos
                password="",            # Contraseña del usuario
                database="login_db"     # Nombre de la base de datos
            )
            return conexion
        except mysql.connector.Error as err:
            print(f"Error de conexión: {err}")
            return None


