
from django import forms
from .models import Cliente
from .models import Ciudad
from .models import Cuenta
from .models import Movimiento
from .models import AdmCuenta

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class CiudadForm(forms.ModelForm):
    class Meta:
        model = Ciudad
        fields = '__all__'
class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = '__all__'

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = '__all__'

class AdmCuentaForm(forms.ModelForm):
    class Meta:
        model = AdmCuenta
        fields = '__all__'


