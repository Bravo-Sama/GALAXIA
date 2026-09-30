from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    class Tipo(models.TextChoices):
        INGRESO = "Ingreso", "Ingreso"
        GASTO_FIJO = "Gasto Fijo", "Gasto Fijo"
        GASTO_VARIABLE = "Gasto Variable", "Gasto Variable"

    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Transaccion(models.Model):
    class Tipo(models.TextChoices):
        INGRESO = "Ingreso", "Ingreso"
        GASTO = "Gasto", "Gasto"

    class ModuloOrigen(models.TextChoices):
        PLUTO = "Pluto", "Pluto"
        HEFESTO = "Hefesto", "Hefesto"
        DEMETER = "Demeter", "Demeter"
        CRONOS = "Cronos", "Cronos"
        ARES = "Ares", "Ares"

    monto = models.IntegerField()
    tipo = models.CharField(max_length=7, choices=Tipo.choices)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="transacciones",
    )
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(default=timezone.now)
    modulo_origen = models.CharField(
        max_length=7,
        choices=ModuloOrigen.choices,
        default=ModuloOrigen.PLUTO,
    )

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo}: ${self.monto:,} - {self.descripcion}"
