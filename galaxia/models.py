import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


def propuesta_expira_en():
    return timezone.now() + timedelta(minutes=10)


class PropuestaIA(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        EXPIRADA = "expirada", "Expirada"
        RECHAZADA = "rechazada", "Rechazada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    texto_usuario = models.TextField()
    resultado_json = models.JSONField()
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField(default=propuesta_expira_en)
    confirmada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Propuesta de IA"
        verbose_name_plural = "Propuestas de IA"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["estado", "expira_en"]),
        ]

    def __str__(self):
        return f"{self.resultado_json.get('modulo', 'N/D')} - {self.estado}"
