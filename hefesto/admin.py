from django.contrib import admin

from .models import CargaCombustible, Mantenimiento, Vehiculo


admin.site.register(Vehiculo)


@admin.register(CargaCombustible)
class CargaCombustibleAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "fecha", "litros", "costo_total", "kilometraje")
    list_filter = ("vehiculo",)


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "vehiculo", "fecha", "costo", "kilometraje")
    list_filter = ("vehiculo",)
    search_fields = ("titulo", "descripcion")
