from django import forms

from .models import Servicio, Cliente, ReservaServicio, Coordinador, Empleado, SolicitudReserva


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'activo','telefono','email', 'numero_documento']
        widgets = {
            'telefono': forms.TelInput()
        }
        
class ReservaForm(forms.ModelForm):
    
    class Meta:
        model = ReservaServicio # hacemos mencion el modelo que vamos a utilizar para el formulario
        fields = ['cliente','servicio','empleado','coordinador','fecha_servicio'] #Elegimos los campos del modelo que queremos ver en el formulario
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'coordinador': forms.Select(attrs={'class': 'form-select'}),
            'fecha_servicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)
        self.fields['servicio'].queryset = Servicio.objects.filter(activo=True)
        self.fields['empleado'].queryset = Empleado.objects.filter(activo=True)
        self.fields['coordinador'].queryset = Coordinador.objects.filter(activo=True)

        self.fields['cliente'].empty_label = 'Selecciona el cliente que hace la reserva'
        self.fields['servicio'].empty_label = 'Selecciona el servicio que se va a prestar'
        self.fields['empleado'].empty_label = 'Selecciona el empleado a cargo'
        self.fields['coordinador'].empty_label = 'Selecciona al coordinador que te ayudará'

class CoordinadorForm(forms.ModelForm):
    class Meta:
        model = Coordinador
        fields = ['nombre', 'apellido', 'activo', 'numero_documento']

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'activo', 'numero_legajo', 'numero_documento']


class SolicitudReservaForm(forms.ModelForm):
    class Meta:
        model = SolicitudReserva
        fields = ['servicio', 'nombre', 'apellido', 'numero_documento', 'telefono', 'email', 'fecha_servicio']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'numero_documento': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'DNI'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'fecha_servicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servicio'].queryset = Servicio.objects.filter(activo=True)
        self.fields['servicio'].empty_label = 'Selecciona el servicio que te interesa'
        for nombre, campo in self.fields.items():
            if nombre != 'servicio':
                campo.required = True
        self.fields['fecha_servicio'].required = False
        self.fields['telefono'].required = False
        self.fields['email'].required = False


class AtenderSolicitudForm(forms.Form):
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True),
        label='Empleado a cargo',
        empty_label='Selecciona el empleado a cargo',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    coordinador = forms.ModelChoiceField(
        queryset=Coordinador.objects.filter(activo=True),
        label='Coordinador',
        empty_label='Selecciona al coordinador',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    fecha_servicio = forms.DateField(
        label='Fecha del servicio',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )