import secrets
from uuid import UUID

from django.conf import settings
from django.db import DatabaseError, transaction
from django.http import HttpRequest
from django.utils import timezone
from ninja import NinjaAPI, Schema
from ninja.security import APIKeyHeader

from hefesto.models import Mantenimiento
from pluto.models import Transaccion

from .ejecutor import ejecutar_accion_ia, validar_accion_ia
from .ia_router import procesar_mensaje_ollama
from .models import PropuestaIA


class GalaxiaAPIKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request: HttpRequest, key: str):
        if key and secrets.compare_digest(key, settings.GALAXIA_API_KEY):
            return key
        return None


api = NinjaAPI(
    title="Galaxia API",
    version="1.0.0",
    auth=GalaxiaAPIKey(),
)


class TransaccionSchema(Schema):
    id: int
    monto: int
    tipo: str
    categoria: str
    descripcion: str
    fecha: str
    modulo_origen: str


class MantenimientoSchema(Schema):
    id: int
    vehiculo: str
    titulo: str
    descripcion: str
    kilometraje: int
    costo: int
    fecha: str


class ChatIn(Schema):
    texto: str


class ChatOut(Schema):
    estado: str
    respuesta: str
    propuesta_id: str | None = None


class ConfirmacionOut(Schema):
    estado: str
    respuesta: str


@api.get("/finanzas/transacciones", response=list[TransaccionSchema])
def listar_transacciones(request):
    transacciones = (
        Transaccion.objects.select_related("categoria")
        .order_by("-fecha")[:10]
    )
    return [
        {
            "id": transaccion.id,
            "monto": transaccion.monto,
            "tipo": transaccion.tipo,
            "categoria": transaccion.categoria.nombre,
            "descripcion": transaccion.descripcion,
            "fecha": transaccion.fecha.isoformat(),
            "modulo_origen": transaccion.modulo_origen,
        }
        for transaccion in transacciones
    ]


@api.get("/auto/mantenimientos", response=list[MantenimientoSchema])
def listar_mantenimientos(request):
    mantenimientos = Mantenimiento.objects.select_related("vehiculo").all()
    return [
        {
            "id": mantenimiento.id,
            "vehiculo": mantenimiento.vehiculo.patente,
            "titulo": mantenimiento.titulo,
            "descripcion": mantenimiento.descripcion,
            "kilometraje": mantenimiento.kilometraje,
            "costo": mantenimiento.costo,
            "fecha": mantenimiento.fecha.isoformat(),
        }
        for mantenimiento in mantenimientos
    ]


@api.post("/chat", response=ChatOut)
def chat_galaxia(request, payload: ChatIn):
    try:
        resultado_ia = procesar_mensaje_ollama(payload.texto)
        propuesta = validar_accion_ia(resultado_ia)
        registro = PropuestaIA.objects.create(
            texto_usuario=payload.texto,
            resultado_json=propuesta,
        )
        return {
            "estado": "pendiente",
            "respuesta": "Propuesta creada. Requiere confirmación explícita.",
            "propuesta_id": str(registro.pk),
        }
    except (RuntimeError, ValueError) as exc:
        return {"estado": "error", "respuesta": str(exc)}


@api.post(
    "/chat/propuestas/{propuesta_id}/confirmar",
    response=ConfirmacionOut,
)
def confirmar_propuesta(request, propuesta_id: UUID):
    with transaction.atomic():
        try:
            propuesta = PropuestaIA.objects.select_for_update().get(
                pk=propuesta_id,
            )
        except PropuestaIA.DoesNotExist:
            return {"estado": "error", "respuesta": "Propuesta no encontrada."}

        if propuesta.estado != PropuestaIA.Estado.PENDIENTE:
            return {
                "estado": "error",
                "respuesta": "La propuesta ya fue procesada.",
            }
        if propuesta.expira_en <= timezone.now():
            propuesta.estado = PropuestaIA.Estado.EXPIRADA
            propuesta.save(update_fields=["estado"])
            return {"estado": "error", "respuesta": "La propuesta expiró."}

        try:
            resultado = ejecutar_accion_ia(propuesta.resultado_json)
        except (RuntimeError, ValueError, DatabaseError) as exc:
            return {"estado": "error", "respuesta": str(exc)}
        if not resultado.startswith("Éxito:"):
            return {"estado": "error", "respuesta": resultado}

        propuesta.estado = PropuestaIA.Estado.CONFIRMADA
        propuesta.confirmada_en = timezone.now()
        propuesta.save(update_fields=["estado", "confirmada_en"])
        return {"estado": "éxito", "respuesta": resultado}
