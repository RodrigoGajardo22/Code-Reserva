from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'servicios', views.ServicioViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'empleados', views.EmpleadoViewSet)
router.register(r'coordinadores', views.CoordinadorViewSet)
router.register(r'reservas', views.ReservaServicioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]