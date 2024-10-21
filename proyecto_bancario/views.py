from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
import csv
import io
from django.contrib.auth.decorators import login_required
from proyecto_bancario.db.querysDB import registro_admin
from proyecto_bancario.db.querysDB import obtener_cuenta, obtener_administrador,registro_cliente,actualizar_usuario, obtener_ciudad_por_nombre
from proyecto_bancario.db.querysDB import listar_cuentas,registro_cuenta, actualizar_cuenta, eliminar_cuenta, movimiento_cuenta, obtener_ciudades_por_nombre
from proyecto_bancario.db.querysDB import eliminar_cliente,listar_clientes,obtener_clientes_por_cedula,obtener_movimientos_por_fechas,obtener_clientes_por_codigo_cuenta

valida_cliente_por_cedula = ""
valida_cuenta_por_codigo = ""
valida_reporte_por_codigo_cuenta = ""

def index_view(request):
    registro_admin()
    return render (request, 'index.html')


def login_cliente_view(request):
    context = {}
    cuenta = None
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        cuenta_asociada = request.POST.get('cuenta')
        resultado_cliente = obtener_clientes_por_cedula(str(cedula))
        if len(resultado_cliente) == 0:
            context['error_message'] = 'Ups, La cedula del cliente ingresado no existe'
        if len(resultado_cliente) != 0:
            cuenta = resultado_cliente[0][6]
            if cuenta == None:
                context['warning_message'] = 'Ups, la cedula del cliente existe, pero no tiene una cuenta asociada'
        if len(resultado_cliente) != 0 and cuenta != None and cuenta_asociada == cuenta:
            global valida_cliente_por_cedula
            valida_cliente_por_cedula = cedula
            return render(request, 'cliente.html')
        elif cuenta_asociada != cuenta:
            context ['warning_message'] = 'Ups, El codigo de la cuenta es incorrecto '

        
    return render(request, 'login_cliente.html', context)


def login_admin_view(request):
    context = {}
    if request.method == 'POST':
        codigo_admin = request.POST.get('codigo_administrador')
        result_cuenta_admin = obtener_administrador(str(codigo_admin))
        if len(result_cuenta_admin) != 0 :
            return render(request,'administrador.html')
        elif len(result_cuenta_admin) == 0:
            context['error_message'] = 'El codigo del administrador ingresado no existe.'
        
    return render(request, 'login_admin.html', context)


# @login_required
def administrador_view(request):
    return render(request,'administrador.html')


# @login_required
def cliente_view(request):
    context = {}
    if valida_cliente_por_cedula == "":
        return render(request, 'login_cliente.html')
    else:
        context['movimientos'] = obtener_movimientos_por_fechas(valida_cliente_por_cedula, 0, 0)
        estado_cuenta = obtener_cuenta(obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][6])[0][2]
        if estado_cuenta == 'Inactiva':
            context['message_state'] = 'Ups, parece que tu cuenta esta inactiva, por lo tanto no podras hacer movimientos'
        context['saldo'] = int(obtener_cuenta(obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][6])[0][3])

        if request.method == 'POST':
            fecha_desde = request.POST.get('fecha_desde')
            fecha_hasta = request.POST.get('fecha_hasta')

            if fecha_hasta == "":
                fecha_hasta = datetime.now()
            if fecha_desde != "":
                context['movimientos'] = obtener_movimientos_por_fechas(valida_cliente_por_cedula, fecha_desde, fecha_hasta)

            if estado_cuenta == 'Activa' and fecha_desde == None:
                tipo_movimiento = request.POST.get('tipo_movimiento')
                cantidad = request.POST.get('cantidad')
                cantidad = int(cantidad)

                cliente = obtener_clientes_por_cedula(valida_cliente_por_cedula)
                codigo_cuenta = cliente[0][6]

                cuenta = obtener_cuenta(codigo_cuenta)
                saldo = int(cuenta[0][3])
                nuevo_saldo = 0

                if tipo_movimiento in ["Envio", "Retiro"]:
                    if saldo - cantidad < 15000:
                         context['message_warning_saldo'] = 'Saldo insuficiente. Recuerda que la cuenta debe permanecer con un monton minimo de 15000 COP'
                    else:
                        nuevo_saldo = saldo - cantidad
                        movimiento_exitoso = movimiento_cuenta(tipo_movimiento, str(nuevo_saldo),str(cantidad), valida_cliente_por_cedula, str(codigo_cuenta))
                        if movimiento_exitoso:
                            context['message_success_move'] = '¡Movimiento exitoso!'
                elif tipo_movimiento == "Abono":
                    nuevo_saldo = saldo + cantidad
                    movimiento_exitoso = movimiento_cuenta(tipo_movimiento, str(nuevo_saldo), str(cantidad), valida_cliente_por_cedula, str(codigo_cuenta))
                    if movimiento_exitoso:
                        context['message_success_move'] = '¡Abono exitoso!'
                        render(request, 'cliente.html', context)
                else:
                    context['message_warning'] = 'Tipo de movimiento no válido.'

            reporte_cliente = request.POST.get('reporte_cliente')
            if reporte_cliente == "true":
                return generar_reporte_por_movimiento(valida_cliente_por_cedula)
        
    return render(request, 'cliente.html', context)


def listar_clientes_view(request):
    clientes = listar_clientes()
    return render(request,'listar_clientes.html',{'clientes': clientes})


def registro_cliente_view(request):
    context = {}
    context['ciudades'] = obtener_ciudades_por_nombre()
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')

        if len(obtener_clientes_por_cedula(cedula)) != 0:
            context['message_error_duplicated'] = '¡Error, el cliente que intenta registrar ya existe!' 
            return render(request, 'registro_cliente.html', context)

        codigo_ciudad = obtener_ciudad_por_nombre(ciudad)[0][0]
        result_cedula_cliente = registro_cliente(str(cedula),nombre,apellido,str(telefono),direccion,ciudad, str(codigo_ciudad))
        if result_cedula_cliente ==True:
            return render(request,'registro_cuenta.html')

        
    return render(request,'registro_cliente.html', context)


def valida_cliente_por_cedula_view(request):
    context = {}
    if request.method == 'POST':
        cedula = request.POST.get('cedula_cliente')
        existe_ciente = obtener_clientes_por_cedula(cedula)
        global valida_cliente_por_cedula
        valida_cliente_por_cedula = cedula
        if len(existe_ciente) == 0:
            context['message_error_cuenta'] = '¡Ups, parece que la cuenta no existe!'
        if len(existe_ciente) != 0:
            request.method = 'GET'
            return actualizar_cliente_view(request)
      
    return render(request,'validar_cliente.html', context)
   

def actualizar_cliente_view(request):
    context = {}
    context['ciudades'] = obtener_ciudades_por_nombre()

    if valida_cliente_por_cedula == "":
        return render(request, 'validar_cliente.html')
    else:
        context['nombre_existente'] = obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][1]
        context['apellido_existente'] = obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][2]
        context['telefono_existente'] = obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][3]
        context['direccion_existente'] = obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][4]
        
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            ciudad = request.POST.get('ciudad')

            codigo_ciudad = obtener_ciudad_por_nombre(ciudad)[0][0]        
            result_cedula_cliente = actualizar_usuario(valida_cliente_por_cedula,nombre,apellido,str(telefono),direccion,str(codigo_ciudad),ciudad)

            if result_cedula_cliente == True:
                context['message_success_update'] = '¡Actualizacion exitosa!'
                return render(request,'actualizar_cliente.html')

    return render(request,'actualizar_cliente.html', context)


def eliminar_cliente_view(request):
    context = {}
    global valida_cliente_por_cedula
    if request.method == 'POST':
        cedula = request.POST.get('cedula_cliente')
        valida = request.POST.get('valida')
        if valida == None:
            context['message_sure_delete'] = '¡Esta seguro de eliminar el cliente!'
            valida_cliente_por_cedula = cedula
        if valida == "SI":
            eliminacion_correcta = eliminar_cliente(valida_cliente_por_cedula)
            if eliminacion_correcta == True:
                context['message_success_delete'] = '¡Cliente eliminado exitosamente!'
                return render(request, 'eliminar_cliente.html', context)
        
    return render(request,'eliminar_cliente.html', context)


def listar_cuentas_view(request):
    cuentas = listar_cuentas()
    if request.method == 'POST':
        reporte_por_codigo_cuenta = request.POST.get('reporte')
        global valida_reporte_por_codigo_cuenta
        valida_reporte_por_codigo_cuenta = reporte_por_codigo_cuenta
        request.method = 'GET'
        return reporte_por_codigo_cuenta_view(request)
    return render(request,'listar_cuentas.html',{'cuentas': cuentas})


def reporte_por_codigo_cuenta_view(request):
    context = {}
    print("CUENTA REPORTE", valida_reporte_por_codigo_cuenta)
    if valida_reporte_por_codigo_cuenta != "":
        context['cuenta'] = valida_reporte_por_codigo_cuenta
        context['reporte_cliente'] = obtener_clientes_por_codigo_cuenta(valida_reporte_por_codigo_cuenta)
        context['reporte_cuenta'] = obtener_cuenta(valida_reporte_por_codigo_cuenta)

        if request.method == 'POST':
            return generar_reporte()
    else:
        return listar_cuentas_view(request)

    return render(request, 'reporte.html', context)


def registro_cuenta_view(request):
    context = {}
    if request.method == 'POST':
        codigo_cuenta = request.POST.get('codigo_cuenta')
        cedula_cliente = request.POST.get('cedula_cliente')
        nombre_cuenta = request.POST.get('nombre_cuenta')
        estado = request.POST.get('estado')
        saldo = request.POST.get('saldo')

        get_cliente_por_cedula = obtener_clientes_por_cedula(cedula_cliente)
        if len(obtener_cuenta(codigo_cuenta)) != 0:
            context['message_error_duplicated'] = '!Error, la cuenta que intenta crear ya existe!'
            return render(request, 'registro_cliente.html', context)
        if len(get_cliente_por_cedula) == 0:
            context['message_error_assign_cliente'] = '¡Error, el cliente ingresado no existe!'
            return render(request, 'registro_cuenta.html', context)
        if len(get_cliente_por_cedula) != 0:
            if get_cliente_por_cedula[0][6] != None :
                context['message_error_assign_cliente'] = '¡Error, la cuenta no se puede asignar, porque el cliente ya tiene una cuenta asociada!'
                return render(request, 'registro_cuenta.html', context)
        
        insert = registro_cuenta(str(codigo_cuenta),str(cedula_cliente),nombre_cuenta,estado,saldo)
        if insert ==True:
            context['message_succes_registro'] = '¡Cuenta creada exitosamente!'
            return render(request,'registro_cuenta.html', context)
    return render(request, 'registro_cuenta.html')


def validar_cuenta_por_codigo_view(request):
    context = {}
    if request.method == 'POST':
        codigo_cuenta = request.POST.get('codigo_cuenta')
        global valida_cuenta_por_codigo
        valida_cuenta_por_codigo = str(codigo_cuenta)
        existe_cuenta = obtener_cuenta(str(codigo_cuenta))
        if len(existe_cuenta) == 0:
            context['message_error_cuenta'] = '¡Ups, parece que la cuenta no existe!'
        elif len(existe_cuenta) != 0:
            request.method = 'GET'
            return actualizar_cuenta_view(request)
    return render(request, 'validar_cuenta.html', context)


def actualizar_cuenta_view(request):
    context = {}
    if request.method == 'POST':
        nombre_cuenta = request.POST.get('nombre_cuenta')
        estado = request.POST.get('estado')

        actualizacion_exitosa = actualizar_cuenta(valida_cuenta_por_codigo, nombre_cuenta, estado)
        if actualizacion_exitosa:
            context['message_success_update'] = '¡Actualizacion exitosa!'
            return render(request, 'actualizar_cuenta.html', context)

    return render(request, 'actualizar_cuenta.html', context)


def eliminar_cuenta_view(request):
    context = {}
    global valida_cliente_por_cedula
    global valida_cuenta_por_codigo
    if request.method == 'POST':
        valida = request.POST.get('valida')
        codigo_cuenta = request.POST.get('codigo_cuenta')
        cedula_cliente = request.POST.get('cedula_cliente')
        if valida == None:
            context['message_sure_delete'] = '¡Esta seguro de eliminar el cliente!'
            valida_cuenta_por_codigo = codigo_cuenta
            valida_cliente_por_cedula = cedula_cliente
        if valida == "SI":
            eliminacion_exitosa = eliminar_cuenta(valida_cuenta_por_codigo, valida_cliente_por_cedula)
            if eliminacion_exitosa:
                context['message_success_delete'] = '¡Cuenta eliminada exitosamente!'
                return render(request, 'eliminar_cuenta.html', context)
        
    return render(request, 'eliminar_cuenta.html', context)


def generar_reporte():
    cliente = obtener_clientes_por_codigo_cuenta(valida_reporte_por_codigo_cuenta)
    cuenta = obtener_cuenta(valida_reporte_por_codigo_cuenta)
    output = io.StringIO()

    writer = csv.writer(output)
    writer.writerow(['Cedula de cliente', 'Nombre', 'Apellido', 'Telefono', 'Direccion', 'Ciudad', 'Codigo de la cuenta asociada'])
    writer.writerow([cliente[0][0], cliente[0][1], cliente[0][2], cliente[0][3], cliente[0][4], cliente[0][5], cliente[0][6]])

    writer.writerow(['Codigo de cuenta', 'Tipo de cuenta', 'Estado de cuenta', 'Saldo total'])
    writer.writerow([cuenta[0][0], cuenta[0][1], cuenta[0][2], cuenta[0][3]])
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_cuenta_{valida_reporte_por_codigo_cuenta}.csv"'

    response.write(output.getvalue())

    return response

def generar_reporte_por_movimiento(cedula_cliente):
    movimientos = obtener_movimientos_por_fechas(cedula_cliente,0,0)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Fecha del movimiento','Tipo de movimiento','Saldo total'])
    for movimiento in movimientos:
        writer.writerow([movimiento[3],movimiento[4],movimiento[5]])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_movimietos_de_cliente{cedula_cliente}.csv"'

    response.write(output.getvalue())

    return response
    
