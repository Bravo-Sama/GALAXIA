from django.contrib import admin

from .models import PropuestaIA


@admin.register(PropuestaIA)
class PropuestaIAAdmin(admin.ModelAdmin):
    list_display = ("id", "estado", "creado_en", "expira_en", "confirmada_en")
    list_filter = ("estado",)
    readonly_fields = ("id", "creado_en", "expira_en", "confirmada_en")
    search_fields = ("id", "texto_usuario")
