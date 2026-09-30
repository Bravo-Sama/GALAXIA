from ninja import NinjaAPI, Schema

from hefesto.models import Mantenimiento
from pluto.models import Transaccion

from .ejecutor import ejecutar_accion_ia
from .ia_router import procesar_mensaje_ollama


api = NinjaAPI(title="Galaxia API", version="1.0.0")


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
        resultado = ejecutar_accion_ia(resultado_ia)
        return {"estado": "éxito", "respuesta": resultado}
    except (RuntimeError, ValueError) as exc:
        return {"estado": "error", "respuesta": str(exc)}
