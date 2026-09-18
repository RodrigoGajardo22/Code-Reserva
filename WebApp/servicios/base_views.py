from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect


class BajaLogicaView(LoginRequiredMixin, View):
    model = None
    success_url = None
    login_url = 'ingresar'

    def post(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        obj.dar_baja()
        self._sincronizar_usuario(obj)
        return redirect(self.success_url)

    def _sincronizar_usuario(self, obj):
        usuario = getattr(obj, 'usuario', None)
        if usuario is not None:
            usuario.is_active = obj.activo
            usuario.save()


class RestaurarView(LoginRequiredMixin, View):
    model = None
    success_url = None
    login_url = 'ingresar'

    def post(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        obj.activar()
        self._sincronizar_usuario(obj)
        return redirect(self.success_url)

    def _sincronizar_usuario(self, obj):
        usuario = getattr(obj, 'usuario', None)
        if usuario is not None:
            usuario.is_active = obj.activo
            usuario.save()
