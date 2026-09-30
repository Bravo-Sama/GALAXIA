from django.db import models
from django.utils import timezone


class CategoriaAlimento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría de alimento"
        verbose_name_plural = "Categorías de alimentos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class UnidadMedida(models.TextChoices):
        KILOGRAMO = "KG", "Kilogramos"
        GRAMO = "GR", "Gramos"
        LITRO = "L", "Litros"
        MILILITRO = "ML", "Mililitros"
        UNIDAD = "UN", "Unidades"

    nombre = models.CharField(max_length=200, unique=True)
    categoria = models.ForeignKey(
        CategoriaAlimento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
    )
    unidad = models.CharField(
        max_length=2,
        choices=UnidadMedida.choices,
        default=UnidadMedida.UNIDAD,
    )
    stock_minimo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Punto de reabastecimiento para alertas.",
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.unidad})"


class ItemDespensa(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="inventario",
    )
    cantidad = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    fecha_vencimiento = models.DateField(null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ítem en despensa"
        verbose_name_plural = "Ítems en despensa"
        ordering = ["fecha_vencimiento", "producto__nombre"]

    def __str__(self):
        return f"{self.producto.nombre}: {self.cantidad} {self.producto.unidad}"


class RegistroComida(models.Model):
    class TipoComida(models.TextChoices):
        DESAYUNO = "Desayuno", "Desayuno"
        ALMUERZO = "Almuerzo", "Almuerzo"
        ONCE = "Once", "Once"
        CENA = "Cena", "Cena"
        SNACK = "Snack", "Snack"

    tipo = models.CharField(
        max_length=20,
        choices=TipoComida.choices,
        default=TipoComida.ALMUERZO,
    )
    descripcion = models.TextField(
        help_text="Ej: Dos panes con queso, un café y una manzana.",
    )
    fecha = models.DateTimeField(default=timezone.now)
    gasto_asociado = models.BooleanField(
        default=False,
        help_text="¿Generó un gasto en Pluto?",
    )

    class Meta:
        verbose_name = "Registro de comida"
        verbose_name_plural = "Registros de comidas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} - {self.fecha:%d/%m/%Y}"
