from django.db import models


class CuentaGoogle(models.Model):
    class Tipo(models.TextChoices):
        PERSONAL = "Personal", "Personal"
        ACADEMICA = "Académica", "Académica"
        TRABAJO = "Trabajo", "Trabajo"

    email = models.EmailField(unique=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    refresh_token = models.CharField(max_length=255)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cuenta de Google"
        verbose_name_plural = "Cuentas de Google"
        ordering = ["email"]

    def __str__(self):
        return f"{self.email} ({self.tipo})"


class Evento(models.Model):
    cuenta = models.ForeignKey(
        CuentaGoogle,
        on_delete=models.CASCADE,
        related_name="eventos",
    )
    google_event_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    modulo_origen = models.CharField(
        max_length=50,
        default="Cronos",
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["fecha_inicio"]

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio:%Y-%m-%d %H:%M})"
