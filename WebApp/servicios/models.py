from django.db import models
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
# Create your models here.

class Persona (models.Model):

    nombre =models.CharField(max_length=100)
    apellido =models.CharField(max_length=100)
    numero_documento =models.IntegerField(unique=True)

    activo = models.BooleanField(default=True)

    def dar_baja(self):
        self.activo = False
        self.save()

    def activar(self):
        self.activo = True
        self.save()

    def __str__(self):
        estado = 'Activo' if self.activo else 'Inactivo'
        return f"{self.nombre} {self.apellido} ({self.numero_documento})"
    
    class Meta:
        abstract = True

class Servicio (models.Model):
    
    nombre =models.CharField(max_length=100)
    descripcion= models.TextField(max_length=400)
    precio = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        estado = 'Activo' if self.activo else 'Inactivo'
        return f"{self.nombre} ({estado})"
    
    def dar_baja(self):
        self.activo = False
        self.save()

    def activar(self):
        self.activo = True
        self.save()


class Cliente (Persona):

    telefono = models.IntegerField(null=True)
    email = models.EmailField(max_length=254, null=True)

class Coordinador (Persona):

    fecha_alta =models.DateField(auto_now=True)
    

class Empleado (Persona):

    numero_legajo =models.IntegerField(unique=True)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='empleado',
    )

    def sincronizar_usuario(self):
        '''Crea o actualiza el auth.User del empleado.
        Usuario de acceso = numero_legajo, contraseña = DNI (fija).
        También copia nombre y apellido al usuario.'''
        if self.usuario is None:
            self.usuario = User(
                username=str(self.numero_legajo),
                first_name=self.nombre,
                last_name=self.apellido,
                is_active=self.activo,
                is_staff=False,
            )
            self.usuario.set_password(str(self.numero_documento))
            self.usuario.save()
            self.save(update_fields=['usuario'])
        else:
            usuario = self.usuario
            usuario.username = str(self.numero_legajo)
            usuario.first_name = self.nombre
            usuario.last_name = self.apellido
            usuario.is_active = self.activo
            usuario.set_password(str(self.numero_documento))
            usuario.save()
        return self.usuario

class ReservaServicio(models.Model):
    
    cliente = models.ForeignKey(Cliente, on_delete= models.CASCADE, related_name="Reserva_Clientes" )
    servicio = models.ForeignKey(Servicio, on_delete= models.CASCADE, related_name="Reserva_Servicio" )
    empleado = models.ForeignKey(Empleado, on_delete= models.CASCADE, related_name="Reserva_Empleado" )
    coordinador = models.ForeignKey(Coordinador, on_delete= models.CASCADE, related_name="Reserva_Coordinador" )
    fecha_reserva = models.DateTimeField(auto_now_add= True)
    fecha_servicio = models.DateField()
    
    def clean(self):# clean()  es una funcion que tiene el modelo de Django para realizar VALIDACIONES PERSONALISADAS
        
        '''Cada vez que intentes guardar una ReservaServicio, Django va a verificar automáticamente:
        
            * Que el servicio esté activo.
            * Que no exista otra reserva para ese servicio en esa fecha.'''
        
        # Validamos que el servicio este activo

        if not Servicio.activo:
            raise ValidationError ("El servicio no esta activo")
        
        # Validamos que no exista otra reserva en la misma fecha
        
        if ReservaServicio.objects.filter(servicio = self.servicio, fecha_servicio= self.fecha_servicio).exists():
            raise ValidationError("El servicio esta reservado en esa fecha")
        
        return super().clean()


class SolicitudReserva(models.Model):

    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_ACEPTADA = 'aceptada'
    ESTADO_RECHAZADA = 'rechazada'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_ACEPTADA, 'Aceptada'),
        (ESTADO_RECHAZADA, 'Rechazada'),
    ]

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="Solicitud_Servicio")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    numero_documento = models.IntegerField()
    telefono = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    fecha_servicio = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    reserva = models.ForeignKey(
        ReservaServicio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Solicitud_Reserva",
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.servicio} ({self.get_estado_display()})"