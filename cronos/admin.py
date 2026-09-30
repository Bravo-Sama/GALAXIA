from django.contrib import admin

from .models import CuentaGoogle, Evento


@admin.register(CuentaGoogle)
class CuentaGoogleAdmin(admin.ModelAdmin):
    list_display = ("email", "tipo", "activa")
    list_filter = ("tipo", "activa")
    search_fields = ("email",)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "cuenta",
        "fecha_inicio",
        "fecha_fin",
        "modulo_origen",
    )
    list_filter = ("cuenta", "modulo_origen")
    search_fields = ("titulo", "descripcion")
