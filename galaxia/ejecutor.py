from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.utils import timezone
from django.utils.dateparse import parse_datetime


def ejecutar_accion_ia(resultado_json):
    if not isinstance(resultado_json, dict):
        return "Fracaso: el resultado de la IA debe ser un objeto JSON."

    modulo = resultado_json.get("modulo")
    accion = resultado_json.get("accion")
    datos = resultado_json.get("datos", {})

    if not isinstance(accion, str) or not accion:
        return "Fracaso: falta una acción válida."
    if not isinstance(datos, dict):
        return "Fracaso: los datos de la acción deben ser un objeto JSON."

    try:
        match modulo:
            case "Auto":
                from hefesto.models import CargaCombustible, Vehiculo

                monto = datos.get("monto")
                kilometraje = datos.get("kilometraje")
                if monto is None or kilometraje is None:
                    return "Fracaso: Auto requiere monto y kilometraje."

                patente = datos.get("patente")
                if patente:
                    vehiculo = Vehiculo.objects.get(patente=patente)
                else:
                    vehiculo = Vehiculo.objects.order_by("patente").first()

                if vehiculo is None:
                    return "Fracaso: no existe un vehículo configurado."

                litros = datos.get("litros", 0)
                try:
                    litros = Decimal(str(litros))
                except (InvalidOperation, ValueError) as exc:
                    raise ValueError("litros debe ser un número válido.") from exc

                carga = CargaCombustible.objects.create(
                    vehiculo=vehiculo,
                    litros=litros,
                    kilometraje=int(kilometraje),
                    costo_total=int(monto),
                )
                return f"Éxito: carga de combustible creada (ID {carga.pk})."

            case "Calendario":
                from cronos.models import CuentaGoogle, Evento

                titulo = datos.get("titulo", "Nuevo Evento")
                fecha_inicio_str = datos.get("fecha_inicio")
                if not fecha_inicio_str:
                    raise ValueError(
                        "Se requiere una fecha y hora de inicio para agendar "
                        "un evento."
                    )

                fecha_inicio = parse_datetime(str(fecha_inicio_str))
                if fecha_inicio is None:
                    raise ValueError(
                        f"Formato de fecha inválido ({fecha_inicio_str}). "
                        "Use formato ISO 8601."
                    )
                if timezone.is_naive(fecha_inicio):
                    fecha_inicio = timezone.make_aware(fecha_inicio)

                fecha_fin_str = datos.get("fecha_fin")
                if fecha_fin_str:
                    fecha_fin = parse_datetime(str(fecha_fin_str))
                    if fecha_fin is None:
                        raise ValueError(
                            f"Formato de fecha inválido ({fecha_fin_str}). "
                            "Use formato ISO 8601."
                        )
                    if timezone.is_naive(fecha_fin):
                        fecha_fin = timezone.make_aware(fecha_fin)
                else:
                    fecha_fin = fecha_inicio + timedelta(hours=1)

                if fecha_fin <= fecha_inicio:
                    raise ValueError(
                        "La fecha de fin debe ser posterior a la fecha de inicio."
                    )

                tipo_cuenta = str(
                    datos.get("tipo_cuenta", "Personal")
                ).capitalize()
                cuenta = CuentaGoogle.objects.filter(
                    tipo=tipo_cuenta,
                    activa=True,
                ).first()
                if cuenta is None:
                    cuenta = CuentaGoogle.objects.filter(activa=True).first()
                if cuenta is None:
                    raise ValueError(
                        "No hay cuentas de Google activas configuradas en la "
                        "base de datos."
                    )

                evento = Evento.objects.create(
                    cuenta=cuenta,
                    titulo=str(titulo),
                    descripcion=str(datos.get("descripcion", "")),
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    modulo_origen="IA_Router",
                )
                return (
                    f"Éxito: evento '{evento.titulo}' agendado para el "
                    f"{fecha_inicio.strftime('%d/%m/%Y a las %H:%M')} "
                    f"en tu calendario {cuenta.tipo}."
                )

            case "Finanzas":
                from pluto.models import Categoria, Transaccion

                monto = datos.get("monto")
                if monto is None:
                    raise ValueError(
                        "Se requiere un monto explícito para registrar una "
                        "transacción."
                    )
                try:
                    monto = int(monto)
                except (TypeError, ValueError) as exc:
                    raise ValueError("El monto debe ser un número entero.") from exc
                if monto <= 0:
                    raise ValueError("El monto debe ser mayor que cero.")

                accion_ia = str(accion).lower()
                es_ingreso = "ingreso" in accion_ia or "sueldo" in accion_ia
                tipo_transaccion = (
                    Transaccion.Tipo.INGRESO
                    if es_ingreso
                    else Transaccion.Tipo.GASTO
                )
                tipo_categoria = (
                    Categoria.Tipo.INGRESO
                    if es_ingreso
                    else Categoria.Tipo.GASTO_VARIABLE
                )
                categoria_nombre = str(
                    datos.get("categoria", "General")
                ).strip().capitalize()
                if not categoria_nombre:
                    categoria_nombre = "General"
                categoria, _ = Categoria.objects.get_or_create(
                    nombre=categoria_nombre,
                    defaults={"tipo": tipo_categoria},
                )

                transaccion = Transaccion.objects.create(
                    descripcion=str(datos.get("descripcion", "Sin descripción")),
                    monto=monto,
                    tipo=tipo_transaccion,
                    categoria=categoria,
                    modulo_origen=Transaccion.ModuloOrigen.PLUTO,
                )
                return (
                    f"Éxito: {tipo_transaccion.lower()} de ${monto} registrado "
                    f"bajo la categoría '{categoria.nombre}' "
                    f"(ID {transaccion.pk})."
                )

            case _:
                return f"Fracaso: módulo no soportado: {modulo!r}."
    except (TypeError, ValueError) as exc:
        return f"Fracaso: datos inválidos para {modulo}: {exc}"
    except ObjectDoesNotExist as exc:
        return f"Fracaso: no se encontró el registro requerido: {exc}"
    except DatabaseError as exc:
        return f"Fracaso al ejecutar la acción de {modulo}: {exc}"
