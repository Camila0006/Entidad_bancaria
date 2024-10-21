from django.db import models

class Ciudad(models.Model):
    codigo_ciudad = models.CharField(max_length=10, primary_key=True)
    nombre_ciudad = models.CharField(max_length=25)

    def __str__(self):
        return self.codigo_ciudad, self.nombre_ciudad
    class Meta:
        db_table = "ciudad"

class Cliente(models.Model):
    cedula_cliente = models.CharField(max_length=12, primary_key=True)
    nombre_cliente = models.CharField(max_length=25)
    apellido_cliente = models.CharField(max_length=25)
    telefono_cliente = models.CharField(max_length=15)
    direccion_cliente = models.CharField(max_length=50)
    codigo_ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)

    def __str__(self):
        return self.cedula_cliente, self.nombre_cliente, self.apellido_cliente, self.telefono_cliente, self.direccion_cliente, self.codigo_ciudad
    class Meta:
        db_table = "cliente"

class Cuenta(models.Model):
    codigo_cuenta = models.CharField(max_length=10, primary_key=True)
    nombre_cuenta = models.CharField(max_length=25)
    estado = models.CharField(max_length=1)

    def __str__(self):
        return self.codigo_cuenta, self.nombre_cuenta, self.estado
    class Meta:
        db_table = "cuenta"

class Movimiento(models.Model):
    id = models.IntegerField(primary_key=True)
    cedula_cliente = models.CharField(max_length=12)
    codigo_cuenta = models.CharField(max_length=10)
    fecha_movimiento = models.DateField()
    tipo_movimiento = models.CharField(max_length=1)
    saldo = models.FloatField()

    def __str__(self):
        return f"Movimiento {self.id}"
    class Meta:
        db_table = "movimiento"

class AdmCuenta(models.Model):
    codigo_adm = models.CharField(max_length=10, primary_key=True)
    cedula_cliente = models.CharField(max_length=12)
    codigo_cuenta = models.CharField(max_length=10)
    fecha_creacion_cita = models.DateField()

    def __str__(self):
        return f"AdmCuenta {self.codigo_adm}"
    class Meta:
        db_table = "adm_cuenta"
