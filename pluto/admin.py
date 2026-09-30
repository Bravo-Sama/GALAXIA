from django.contrib import admin

from .models import Categoria, Transaccion


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo")
    list_filter = ("tipo",)


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = (
        "descripcion",
        "monto",
        "tipo",
        "categoria",
        "fecha",
        "modulo_origen",
    )
    list_filter = ("tipo", "modulo_origen", "categoria")
    search_fields = ("descripcion",)
