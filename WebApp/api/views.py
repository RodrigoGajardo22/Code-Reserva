from rest_framework import viewsets
from servicios.models import Servicio, Cliente, Empleado, Coordinador, ReservaServicio
from .serializers import (
    ServicioSerializer, 
    ClienteSerializer, 
    EmpleadoSerializer, 
    CoordinadorSerializer,
    ReservaServicioSerializer
)
from drf_spectacular.renderers import OpenApiJsonRenderer
from drf_spectacular.views import SpectacularAPIView

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer

class CoordinadorViewSet(viewsets.ModelViewSet):
    queryset = Coordinador.objects.all()
    serializer_class = CoordinadorSerializer

class ReservaServicioViewSet(viewsets.ModelViewSet):
    queryset = ReservaServicio.objects.all()
    serializer_class = ReservaServicioSerializer

class SchemaDescargaView(SpectacularAPIView):
    renderer_classes = [OpenApiJsonRenderer]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Content-Disposition'] = 'attachment; filename="reserva-api-schema.json"'
        return response