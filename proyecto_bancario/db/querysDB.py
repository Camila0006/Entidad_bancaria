from proyecto_bancario.db.db import connection
from datetime import datetime, timedelta

def registro_admin():
    administrador = obtener_administrador(2409)
    if len(administrador) == 0:
        db = connection.cursor()
        query = "INSERT INTO cliente (cedula_cliente, nombre_cliente, apellido_cliente, telefono_cliente, direccion_cliente, codigo_ciudad) VALUES ('123','camila','mendez','1234','cra1236','434');"
        db.execute(query)
        query = "INSERT INTO adm_cuenta(codigo_adm,cedula_cliente,fecha_creacion_cuenta) VALUES ('2409','123','2024-10-16');"
        db.execute(query)
        connection.commit()
    return


def obtener_ciudades_por_nombre():
    db = connection.cursor()
    query = "SELECT nombre_ciudad FROM ciudad"
    db.execute(query)
    result = db.fetchall()

    return result

def obtener_ciudad_por_nombre(nombre_ciudad):
    db = connection.cursor()
    query = "SELECT * FROM ciudad WHERE nombre_ciudad = %s"
    db.execute(query, nombre_ciudad)
    result = db.fetchall()

    return result

def obtener_cedulas_clientes():
    db = connection.cursor()
    query = "SELECT cedula_cliente FROM cliente;"
    db.execute(query)
    result = db.fetchall()

    return result

def obtener_clientes_por_cedula(cedula):
    db = connection.cursor()
    query = "SELECT * FROM cliente WHERE cedula_cliente = %s;"
    db.execute(query, (cedula))
    result = db.fetchall()

    return result

def obtener_clientes_por_codigo_cuenta(codigo_cuenta):
    db = connection.cursor()
    query = "SELECT * FROM cliente WHERE codigo_cuenta = %s;"
    db.execute(query, (codigo_cuenta))
    result = db.fetchall()

    return result

def obtener_cuenta(codigo_cuenta):
    db = connection.cursor()
    query = "SELECT * FROM cuenta WHERE codigo_cuenta = %s"
    db.execute(query, codigo_cuenta)
    result = db.fetchall()

    return result


def obtener_administrador(codigo_admin):
    db = connection.cursor()
    query = "SELECT * FROM adm_cuenta WHERE codigo_adm = %s;"
    db.execute(query,(codigo_admin))
    result =db.fetchall()

    return result

def obtener_movimientos_por_fechas(cedula_cliente, fecha_desde, fecha_hasta):
    if fecha_desde == 0 and fecha_hasta == 0:
        fecha_hasta = datetime.now()
        fecha_desde = fecha_hasta - timedelta(days=3)

    db = connection.cursor()
    query = "SELECT * FROM movimiento WHERE cedula_cliente = %s AND fecha_movimiento BETWEEN %s AND %s;"
    db.execute(query, (cedula_cliente, fecha_desde, fecha_hasta))
    result = db.fetchall()

    return result

def listar_clientes():
    db = connection.cursor()
    query = "SELECT * FROM cliente;"
    db.execute(query)
    result = db.fetchall()

    return result

def registro_cliente(Cedula, Nombre, Apellido, Telefono, Direccion, ciudad, codigo_ciudad):
    db = connection.cursor()
    query = "SELECT * FROM ciudad WHERE codigo_ciudad = %s AND nombre_ciudad = %s;"
    db.execute(query, (str(codigo_ciudad), ciudad))
    result = db.fetchall()
    if len(result) == 0:
        query = "INSERT INTO ciudad (codigo_ciudad, nombre_ciudad) values (%s, %s);"
        result= db.execute(query, (codigo_ciudad, ciudad))

    query = "INSERT INTO cliente (cedula_cliente, nombre_cliente, apellido_cliente, telefono_cliente, direccion_cliente, codigo_ciudad) VALUES (%s, %s, %s, %s, %s, %s);"
    values = (Cedula, Nombre, Apellido, Telefono, Direccion, codigo_ciudad)
    result= db.execute(query, values)
    connection.commit()

    if result == 1:
        return True    
    
    return False

def actualizar_usuario (cedula,nombre,apellido,telefono,direccion,codigo_ciudad, ciudad):
    db = connection.cursor()

    query = "SELECT * FROM ciudad WHERE codigo_ciudad = %s AND nombre_ciudad = %s;"
    db.execute(query, (str(codigo_ciudad), ciudad))
    result = db.fetchall()
    if len(result) == 0:
        query = "INSERT INTO ciudad (codigo_ciudad, nombre_ciudad) values (%s, %s);"
        result= db.execute(query, (codigo_ciudad, ciudad))

    query = "UPDATE cliente SET nombre_cliente = %s, apellido_cliente = %s, telefono_cliente = %s,direccion_cliente = %s, codigo_ciudad=%s WHERE cedula_cliente = %s;" 
    values = (nombre,apellido,telefono,direccion,codigo_ciudad,cedula)
    result = db.execute(query,values)
    connection.commit()
    if result == 1:
        return True
        
    return False

def eliminar_cliente(cedula_cliente):
    db = connection.cursor()

    codigo_cuenta = obtener_clientes_por_cedula(cedula_cliente)[0][6]
    print("codigo_cuenta eliminar:", codigo_cuenta)
    query = "DELETE FROM cliente WHERE cedula_cliente = %s;"
    result = db.execute(query, cedula_cliente)
    connection.commit()
    if result == 1 and codigo_cuenta == None:
        return True
    else:
        print("Cliente elimiado correctamente")
        query = "DELETE FROM cuenta WHERE codigo_cuenta = %s;"
        result = db.execute(query, codigo_cuenta)
        connection.commit()
        print("cuenta elimiado correctamente")
        if result == 1:
            return True
    
    return False

def listar_cuentas():
    db = connection.cursor()
    query = "SELECT * FROM cuenta;"
    db.execute(query)
    result = db.fetchall()
    
    return result

def registro_cuenta(codigo_cuenta, cedula_cliente, nombre_cuenta, estado, saldo):
    db = connection.cursor()
    query = "INSERT INTO cuenta (codigo_cuenta, nombre_cuenta, estado, saldo) VALUES (%s, %s, %s, %s);"
    values = (codigo_cuenta, nombre_cuenta, estado, saldo)
    result= db.execute(query, values)
    connection.commit()

    if result == 1:
        query = "UPDATE cliente SET codigo_cuenta = %s WHERE cedula_cliente = %s;"
        result = db.execute(query, (codigo_cuenta, cedula_cliente))
        connection.commit()
        if result == 1:
            return True 
    return False

def actualizar_cuenta(codigo_cuenta, nombre_cuenta, estado):
    db = connection.cursor()
    query = "UPDATE cuenta SET nombre_cuenta = %s, estado = %s WHERE codigo_cuenta = %s;" 
    values = (nombre_cuenta, estado, codigo_cuenta)
    result = db.execute(query,values)
    connection.commit()
    if result == 1:
        return True
           
    return False

def eliminar_cuenta(codigo_cuenta, cedula_cliente):
    db = connection.cursor()

    query = "UPDATE cliente SET codigo_cuenta = Null WHERE cedula_cliente = %s AND codigo_cuenta = %s;" 
    values = (cedula_cliente, str(codigo_cuenta))
    result = db.execute(query,values)
    connection.commit()

    if result == 1:
        query = "DELETE FROM cuenta WHERE codigo_cuenta = %s;"
        result = db.execute(query, codigo_cuenta)
        connection.commit()
        if result == 1:
            return True
    
    return False

def movimiento_cuenta(tipo_movimiento, nuevo_saldo, saldo, cedula_cliente, codigo_cuenta):
    db = connection.cursor()

    fecha_movimiento = datetime.now()
    query = "INSERT INTO movimiento (cedula_cliente, codigo_cuenta, fecha_movimiento, tipo_movimiento, saldo) values (%s, %s, %s, %s, %s);"
    values = (cedula_cliente, codigo_cuenta, fecha_movimiento, tipo_movimiento, saldo)
    print("VALUES QUERY : ",values)
    result= db.execute(query, values)
    connection.commit()
    if result == 1:
        query = "UPDATE cuenta SET saldo = %s WHERE codigo_cuenta = %s;"
        values = (nuevo_saldo, codigo_cuenta)
        result= db.execute(query, values)
        connection.commit()
        return True
    
    return False
