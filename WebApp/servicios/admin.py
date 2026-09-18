from django.contrib import admin
from .models import Cliente, Servicio, Coordinador, Empleado, ReservaServicio, SolicitudReserva


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'activo')
    search_fields = ('nombre', 'apellido', 'numero_documento')


@admin.register(Coordinador)
class CoordinadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'activo')
    search_fields = ('nombre', 'apellido', 'numero_documento')


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'numero_legajo', 'numero_documento', 'usuario', 'activo')
    search_fields = ('nombre', 'apellido', 'numero_legajo', 'numero_documento')
    readonly_fields = ('usuario',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.sincronizar_usuario()


@admin.register(ReservaServicio)
class ReservaServicioAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'cliente', 'fecha_reserva', 'empleado', 'coordinador', 'fecha_servicio')
    search_fields = ('servicio__nombre', 'cliente__nombre', 'cliente__apellido')


@admin.register(SolicitudReserva)
class SolicitudReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'numero_documento', 'servicio', 'fecha_servicio', 'fecha_registro', 'estado')
    list_filter = ('estado', 'servicio')
    search_fields = ('nombre', 'apellido', 'numero_documento', 'servicio__nombre')
