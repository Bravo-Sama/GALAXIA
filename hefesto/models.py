from django.db import models, transaction
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

    def save(self, *args, **kwargs):
        if self.transaccion_finanzas_id is not None or self.costo_total <= 0:
            return super().save(*args, **kwargs)

        from pluto.models import Categoria, Transaccion

        with transaction.atomic():
            super().save(*args, **kwargs)
            categoria, _ = Categoria.objects.get_or_create(
                nombre="Combustible",
                defaults={
                    "tipo": Categoria.Tipo.GASTO_VARIABLE,
                    "descripcion": "Gastos de combustible del vehículo.",
                },
            )
            self.transaccion_finanzas = Transaccion.objects.create(
                monto=self.costo_total,
                tipo=Transaccion.Tipo.GASTO,
                categoria=categoria,
                descripcion=f"Carga de combustible de {self.vehiculo} ({self.litros} L)",
                fecha=self.fecha,
                modulo_origen=Transaccion.ModuloOrigen.HEFESTO,
            )
            super().save(update_fields=["transaccion_finanzas"])


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

    def save(self, *args, **kwargs):
        if self.transaccion_finanzas_id is not None or self.costo <= 0:
            return super().save(*args, **kwargs)

        from pluto.models import Categoria, Transaccion

        with transaction.atomic():
            super().save(*args, **kwargs)
            categoria, _ = Categoria.objects.get_or_create(
                nombre="Mantenimiento del vehículo",
                defaults={
                    "tipo": Categoria.Tipo.GASTO_VARIABLE,
                    "descripcion": "Gastos de mantenimiento del vehículo.",
                },
            )
            self.transaccion_finanzas = Transaccion.objects.create(
                monto=self.costo,
                tipo=Transaccion.Tipo.GASTO,
                categoria=categoria,
                descripcion=f"{self.titulo} - {self.vehiculo}",
                fecha=self.fecha,
                modulo_origen=Transaccion.ModuloOrigen.HEFESTO,
            )
            super().save(update_fields=["transaccion_finanzas"])
