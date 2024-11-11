from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
import csv
import io
from proyecto_bancario.db.querysDB import (registro_admin,obtener_cuenta, 
                                           obtener_administrador,registro_cliente,actualizar_usuario
                                           ,listar_cuentas,registro_cuenta, actualizar_cuenta, eliminar_cuenta,
                                           movimiento_cuenta, obtener_ciudades,eliminar_cliente,listar_clientes,
                                           obtener_clientes_por_cedula,obtener_movimientos_por_fechas,obtener_clientes_por_codigo_cuenta,
                                           filtrar_clientes_por_cedula_o_nombre,filtrar_cuentas_por_estado,filtrar_cuentas_por_tipo)

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
            request.method = 'GET'
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
    global valida_reporte_por_codigo_cuenta
    valida_reporte_por_codigo_cuenta = ""
    context = {}
    administrador = obtener_administrador(2409)
    cliente_admin = obtener_clientes_por_cedula(administrador[0][1])
    context['administrador'] = {
        'nombre': cliente_admin[0][1],
        'apellido': cliente_admin[0][2]
    }

    if request.method == 'POST' and request.POST.get('cerrar_sesion'):
        valida_login_admin = False
        request.method = 'GET'
        return render(request, 'index.html', context)
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
    context = {
        'clientes': {}
    }
    if request.method == 'POST' and request.POST.get('boton_filtrar') == "true":
        if (valor := request.POST.get('filtro')) != None and valor != "":
            clientes = filtrar_clientes_por_cedula_o_nombre(valor)
            context['clientes'] = clientes
            request.method = 'GET'
            return render(request,'listar_clientes.html', context)
        else:
            context['message_error_filter'] = '¡Ups!, por favor ingrese un valor para filtrar, refresque e intente de nuevo!'
            return render(request,'listar_clientes.html', context)
    else:
        clientes = listar_clientes()
        context['clientes'] = clientes
        return render(request,'listar_clientes.html', context)


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
    context = {
        'cuentas': {}
    }
    filtro_estado = ""
    filtro_tipo = ""

    print("MEhotodo " , request.method)
    if request.method == 'POST' :
        #Validamos todo los filtros uno por uno
        if (reporte_por_codigo_cuenta := request.POST.get('reporte')) != None and reporte_por_codigo_cuenta != "":
            global valida_reporte_por_codigo_cuenta
            valida_reporte_por_codigo_cuenta = reporte_por_codigo_cuenta
            request.method = 'GET'
            return reporte_por_codigo_cuenta_view(request)

        print("accion boton buscar", request.POST.get('boton_filtrar'))
        if (boton_filtrar := request.POST.get('boton_filtrar')) != None and boton_filtrar == "true":
            print("obtenemos lo que viene para filtrar?", request.POST.get('filtro'))
            if (codigo_cuenta := request.POST.get('filtro')) != None and codigo_cuenta != "":
                cuenta = obtener_cuenta(codigo_cuenta)
                context['cuentas'] = cuenta
                request.method = 'GET'
                return render(request,'listar_cuentas.html', context)
            else:
                context['message_error_filter'] = '¡Ups!, por favor ingrese un valor para filtrar, refresque e intente de nuevo!'
                return render(request,'listar_cuentas.html', context)
        
        print("Que filtros estamos enviando crajo : Activa--", request.POST.get('filtro_activa'), " : Inactiva --", request.POST.get('filtro_inactiva'), " : Ahorros --",request.POST.get('filtro_ahorros'), " : Corriente --", request.POST.get('filtro_corriente'))
        if (filtro_activa := request.POST.get('filtro_activa')) != None and filtro_activa == "activa" :
            filtro_estado = filtro_activa
        if (filtro_inactiva := request.POST.get('filtro_inactiva')) != None and filtro_inactiva == "inactiva" :
            filtro_estado = filtro_inactiva
        if (filtro_ahorros := request.POST.get('filtro_ahorros')) != None and filtro_ahorros == "ahorros" :
            filtro_tipo = filtro_ahorros
        if (filtro_corriente := request.POST.get('filtro_corriente')) != None and filtro_corriente == "corriente" :
            filtro_tipo = filtro_corriente

        print("que vamos a filtrar de estados: ", filtro_estado)
        print("que vamos a filtrar de tipos: ", filtro_tipo)
        if filtro_estado != "" :
            cuentas = filtrar_cuentas_por_estado(filtro_estado)
            context['cuentas'] = cuentas
            request.method = 'GET'
            return render(request,'listar_cuentas.html', context)
        
        if filtro_tipo != "" :
            cuentas = filtrar_cuentas_por_tipo(filtro_tipo)
            context['cuentas'] = cuentas
            request.method = 'GET'
            return render(request,'listar_cuentas.html', context)
    else :
        cuentas = listar_cuentas() 
        context['cuentas'] = cuentas
        return render(request,'listar_cuentas.html', context)


def reporte_por_codigo_cuenta_view(request):
    context = {}
    print("CUENTA REPORTE", valida_reporte_por_codigo_cuenta)
    if valida_reporte_por_codigo_cuenta != "":
        context['cuenta'] = valida_reporte_por_codigo_cuenta
        context['reporte_cliente'] = obtener_clientes_por_codigo_cuenta(valida_reporte_por_codigo_cuenta)
        context['reporte_cuenta'] = obtener_cuenta(valida_reporte_por_codigo_cuenta)
        
        if request.method == 'POST' and request.POST.get('descarga_reporte'):
            print("Descargamos reporte", valida_reporte_por_codigo_cuenta)
            return generar_reporte(valida_reporte_por_codigo_cuenta)
        elif request.method == 'POST' and request.POST.get('volver'):
            print("Volvemos", valida_reporte_por_codigo_cuenta)
            request.method = 'GET'
            return administrador_view(request)
            
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


def generar_reporte(valida_reporte_por_codigo_cuenta):
    print("descarga_reporte_cedula", valida_reporte_por_codigo_cuenta)
    cliente = obtener_clientes_por_codigo_cuenta(valida_reporte_por_codigo_cuenta)
    cuenta = obtener_cuenta(valida_reporte_por_codigo_cuenta)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    if cliente:
        writer.writerow(['Cedula de cliente', 'Nombre', 'Apellido', 'Telefono', 'Direccion', 'Ciudad', 'Codigo de la cuenta asociada'])
        print("Datos que envio en reporte sobre cliente", cliente)
        writer.writerow([f'"{cliente[0][0]}"', cliente[0][1], cliente[0][2], cliente[0][3], cliente[0][4], f'"{cliente[0][5]}"', f'"{cliente[0][6]}"'])

    writer.writerow([])
    writer.writerow([])
    writer.writerow([])

    if cuenta:
        writer.writerow(['Codigo de cuenta', 'Tipo de cuenta', 'Estado de cuenta', 'Saldo total'])
        print("Datos que envio en reporte sobre cuenta del cliente", cuenta)
        writer.writerow([f'"{cuenta[0][0]}"', cuenta[0][1], cuenta[0][2], cuenta[0][3]])
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="reporte_cuenta_{valida_reporte_por_codigo_cuenta}.csv"'

    response.write(output.getvalue())

    return response

def generar_reporte_por_movimiento(cedula_cliente):
    movimientos = obtener_movimientos_por_fechas(cedula_cliente,0,0)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    for movimiento in movimientos:
        writer.writerow(['Fecha del movimiento','Tipo de movimiento','Saldo total'])
        writer.writerow([movimiento[3],movimiento[4],movimiento[5]])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_movimietos_de_cliente{cedula_cliente}.csv"'

    response.write(output.getvalue())

    return response
    