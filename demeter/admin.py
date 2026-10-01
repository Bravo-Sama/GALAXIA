from django.contrib import admin

from .models import (
    CategoriaAlimento,
    ItemDespensa,
    Producto,
    RegistroComida,
)


@admin.register(CategoriaAlimento)
class CategoriaAlimentoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "unidad", "stock_minimo")
    list_filter = ("categoria", "unidad")
    search_fields = ("nombre",)
    list_select_related = ("categoria",)


@admin.register(ItemDespensa)
class ItemDespensaAdmin(admin.ModelAdmin):
    list_display = (
        "producto",
        "cantidad",
        "fecha_vencimiento",
        "ultima_actualizacion",
    )
    list_filter = ("producto__categoria",)
    search_fields = ("producto__nombre",)
    list_select_related = ("producto", "producto__categoria")


@admin.register(RegistroComida)
class RegistroComidaAdmin(admin.ModelAdmin):
    list_display = ("tipo", "fecha", "gasto_asociado")
    list_filter = ("tipo", "gasto_asociado")
    search_fields = ("descripcion",)
