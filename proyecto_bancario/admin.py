from django.contrib import admin
from proyecto_bancario.models import Cliente, Ciudad, Cuenta, Movimiento


# Register your models here.

admin.site.register(Cliente)
admin.site.register(Ciudad)
admin.site.register(Cuenta)
admin.site.register(Movimiento)
