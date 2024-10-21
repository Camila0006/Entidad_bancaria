from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import login_cliente_view,index_view,login_admin_view,administrador_view,registro_cliente_view,reporte_por_codigo_cuenta_view
from .views import actualizar_cliente_view,eliminar_cliente_view,valida_cliente_por_cedula_view,listar_clientes_view
from .views import listar_cuentas_view,registro_cuenta_view,validar_cuenta_por_codigo_view,actualizar_cuenta_view,eliminar_cuenta_view,cliente_view

urlpatterns = [
    path('', index_view, name='index'),
    path('login_admin/', login_admin_view, name='login_admin'),
    path('login_cliente/', login_cliente_view, name='login_cliente'),
    path('cliente/', cliente_view, name='cliente'),
    path('administrador/', administrador_view, name='administrador'),
    path('listar_clientes/', listar_clientes_view, name='listar_clientes'),
    path('listar_cuentas/', listar_cuentas_view, name='listar_cuentas'),
    path('registro_cliente/', registro_cliente_view, name='registro_cliente'),
    path('registro_cuenta/', registro_cuenta_view, name='registro_cuenta'),
    path('validar_cliente/', valida_cliente_por_cedula_view, name='validar_cliente'),
    path('validar_cuenta/', validar_cuenta_por_codigo_view, name='validar_cuenta'),
    path('actualizar_cliente/', actualizar_cliente_view, name='actualizar_cliente'),
    path('actualizar_cuenta/', actualizar_cuenta_view, name='actualizar_cuenta'),
    path('eliminar_cliente/', eliminar_cliente_view, name='eliminar_cliente'),
    path('eliminar_cuenta/', eliminar_cuenta_view, name='eliminar_cuenta'),
    path('reporte/', reporte_por_codigo_cuenta_view, name='reporte')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)