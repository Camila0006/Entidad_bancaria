from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
import csv
import io
from proyecto_bancario.db.querysDB import registro_admin
from proyecto_bancario.db.querysDB import obtener_cuenta, obtener_administrador,registro_cliente,actualizar_usuario
from proyecto_bancario.db.querysDB import listar_cuentas,registro_cuenta, actualizar_cuenta, eliminar_cuenta, movimiento_cuenta, obtener_ciudades
from proyecto_bancario.db.querysDB import eliminar_cliente,listar_clientes,obtener_clientes_por_cedula,obtener_movimientos_por_fechas,obtener_clientes_por_codigo_cuenta

global valida_login_admin
global valida_login_cliente
valida_login_admin = False
valida_login_cliente = False

valida_cliente_por_cedula = ""
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
            # global valida_login_cliente
            # valida_login_cliente = True
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
            # global valida_login_admin
            # valida_login_admin = True
            return render(request,'administrador.html')
        else:
            context['error_message'] = 'El codigo del administrador ingresado no existe.'
        
    return render(request, 'login_admin.html', context)


def administrador_view(request):
    #Validamos que se haya logeado el admin
    # if valida_login_admin is False:
    #     return render(request, 'login_admin.html')
    # else:
    context = {}
    administrador = obtener_administrador(2409)
    cliente_admin = obtener_clientes_por_cedula(administrador[0][1])
    context['administrador'] = {
        'nombre': cliente_admin[0][1],
        'apellido': cliente_admin[0][2]
    }

    # if request.POST.get('cerrar_sesion'):
    #     valida_login_admin = False
    #     return render(request, 'index.html', context)
    return render(request,'administrador.html', context)


def cliente_view(request):
    context = {}
    #Validamos que se haya logeado el cliente
    # if valida_login_cliente is False:
    #     return render(request, 'login_cliente.html', context)
    # else:
    context['movimientos'] = obtener_movimientos_por_fechas(valida_cliente_por_cedula, 0, 0)
    estado_cuenta = obtener_cuenta(obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][6])[0][2]
    if estado_cuenta == 'Inactiva':
        context['message_state'] = 'Ups, parece que tu cuenta esta inactiva, por lo tanto no podras hacer movimientos'
    context['saldo'] = int(obtener_cuenta(obtener_clientes_por_cedula(valida_cliente_por_cedula)[0][6])[0][3])

    if request.method == 'POST':
        # if request.POST.get('cerrar_sesion'):
        #     valida_login_cliente = False
        #     return render(request, 'index.html', request)
        
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
    context = {
        'ciudades': obtener_ciudades()
    }
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

        result_cedula_cliente = registro_cliente(str(cedula),nombre,apellido,str(telefono),direccion, str(ciudad))
        if result_cedula_cliente ==True:
            context['message_succes_registro'] = '¡El cliente ha sido registrado exitosamente!' 
            return render(request,'registro_cuenta.html', context)

        
    return render(request,'registro_cliente.html', context)


def actualizar_cliente_view(request):
    context = {
        'ciudades': obtener_ciudades(),
        'cliente': {}
    }

    # Validación de cédula
    if (valida_cedula_cliente := request.POST.get('valida_cedula')) is not None:
        request.session['cedula_cliente_actualizar'] = valida_cedula_cliente
        cliente_existente = obtener_clientes_por_cedula(valida_cedula_cliente)
        
        if cliente_existente:
            context['cliente'] = {
                'nombre': cliente_existente[0][1],
                'apellido': cliente_existente[0][2],
                'telefono': cliente_existente[0][3],
                'direccion': cliente_existente[0][4],
                'ciudad': cliente_existente[0][5]
            }
        else:
            context['message_error_client'] = 'Ups, el cliente ingresado no existe!'
        
        return render(request, 'actualizar_cliente.html', context)

    # Actualización de datos
    if request.method == 'POST' and 'nombre' in request.POST:
        cedula = request.session.get('cedula_cliente_actualizar')  # Obtiene la cédula de la sesión
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')

        if cedula:
            result_cedula_cliente = actualizar_usuario(cedula, nombre, apellido, str(telefono), direccion, str(ciudad))

            if result_cedula_cliente:
                context['message_success_update'] = '¡Actualización exitosa!'
            else:
                context['message_error_client'] = 'Error al actualizar el cliente.'
    
    return render(request, 'actualizar_cliente.html', context)



def eliminar_cliente_view(request):
    context = {
        'ciudades': obtener_ciudades(),
        'cliente': {}
    }

    if (valida_cedula_cliente := request.POST.get('valida_cedula')) != None:
        request.session['cedula_cliente_eliminar'] = valida_cedula_cliente
        cliente_existente = obtener_clientes_por_cedula(valida_cedula_cliente)
        
        if cliente_existente:
            context['cliente'] = {
                'nombre': cliente_existente[0][1],
                'apellido': cliente_existente[0][2],
                'telefono': cliente_existente[0][3],
                'direccion': cliente_existente[0][4],
                'ciudad': cliente_existente[0][5]
            }
        else:
            context['message_error_client'] = 'Ups, el cliente ingresado no existe!'
        return render(request,'eliminar_cliente.html', context)

    if request.POST.get('eliminar_cliente') == 'eliminar':
        print("va a eliminar", request.session['cedula_cliente_eliminar'])
        context['message_sure_delete'] = '¿Está seguro de eliminar el cliente?'
    
    if request.method == 'POST':
        if (cedula_cliente := request.session.get('cedula_cliente_eliminar')) != None and request.POST.get('valida') == "SI":
            eliminacion_exitosa = eliminar_cliente(cedula_cliente)
            if eliminacion_exitosa:
                context['message_success_delete'] = 'Cliente eliminado exitosamente!'
                return render(request, 'eliminar_cuenta.html', context)
      

    return render(request, 'eliminar_cliente.html', context)



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

def actualizar_cuenta_view(request):
    context = {
        'tipo_cuentas': {'Ahorros','Corriente'},
        'estados': {'Activa','Inactiva'},
        'cuenta': {}
    }

    if (valida_cuenta := request.POST.get('valida_cuenta')) != None:
        request.session['codigo_cuenta_actualizar'] = valida_cuenta
        cuenta_existente = obtener_cuenta(valida_cuenta)
        if cuenta_existente:
            context['cuenta'] = {
                'codigo': cuenta_existente[0][0],
                'nombre': cuenta_existente[0][1],
                'estado': cuenta_existente[0][2],
            }
        else:
            context['message_error_client'] = 'Ups, la cuenta ingresada no existe!'
        return render(request,'actualizar_cuenta.html', context)
    
    if request.method == 'POST':
        codigo = request.session.get('codigo_cuenta_actualizar')
        nombre = request.POST.get('nombre_cuenta')
        estado = request.POST.get('estado_cuenta')
      
        result_cuenta_actualizada = actualizar_cuenta(nombre, estado, codigo)

        if result_cuenta_actualizada == True:
            request.session.pop('codigo_cuenta_actualizar', None)
            context['message_success_update'] = 'Cuenta actualizada exitosamente!'

    return render(request,'actualizar_cuenta.html', context)

def eliminar_cuenta_view(request):
    context = {
        'cuenta': {}
    }

    if (valida_cuenta := request.POST.get('valida_cuenta')) != None:
        request.session['codigo_cuenta_eliminar'] = valida_cuenta
        cuenta_existente = obtener_cuenta(valida_cuenta)
        if cuenta_existente:
            context['cuenta'] = {
                'codigo': cuenta_existente[0][0],
                'nombre': cuenta_existente[0][1],
                'estado': cuenta_existente[0][2],
            }
        else:
            context['message_error_client'] = 'Ups, la cuenta ingresada no existe!'
        
        return render(request,'eliminar_cuenta.html', context)
    
    if request.POST.get('eliminar_cuenta') == 'eliminar':
        context['message_sure_delete'] = '¡Esta seguro de eliminar el cliente!'

    if request.method == 'POST':
        if (codigo_cuenta := request.session.get('codigo_cuenta_eliminar')) != None and request.POST.get('valida') == "SI":
            eliminacion_exitosa = eliminar_cuenta(codigo_cuenta)
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
    
