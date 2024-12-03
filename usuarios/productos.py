from usuarios.conectar_bd import conectar_bd

def cargar_productos():
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = "SELECT id, nombre_producto, precio FROM productos"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al cargar productos: {e}")
        finally:
            cursor.close()
            conexion.close()
    return []
