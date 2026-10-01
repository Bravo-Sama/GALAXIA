from django.db import models
from django.utils import timezone


class Vehiculo(models.Model):
    patente = models.CharField(max_length=10, primary_key=True)
    marca = models.CharField(max_length=100, default="Chevrolet")
    modelo = models.CharField(max_length=100, default="Corsa")
    año = models.IntegerField(default=2006)
    kilometraje_actual = models.IntegerField()

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["patente"]

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"


class CargaCombustible(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="cargas_combustible",
    )
    litros = models.DecimalField(max_digits=8, decimal_places=2)
    kilometraje = models.IntegerField()
    costo_total = models.IntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    transaccion_finanzas = models.OneToOneField(
        "pluto.Transaccion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carga_combustible",
    )

    class Meta:
        verbose_name = "Carga de combustible"
        verbose_name_plural = "Cargas de combustible"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.vehiculo.patente} - {self.litros} L - ${self.costo_total}"

class Mantenimiento(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="mantenimientos",
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    kilometraje = models.IntegerField()
    costo = models.IntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    transaccion_finanzas = models.OneToOneField(
        "pluto.Transaccion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mantenimiento",
    )

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.vehiculo.patente} - {self.titulo}"
