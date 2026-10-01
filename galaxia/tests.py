from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from demeter.models import RegistroComida

from .models import PropuestaIA


@override_settings(GALAXIA_API_KEY="test-api-key")
class ChatSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_chat_requires_api_key(self):
        response = self.client.post(
            "/api/chat",
            data={"texto": "anota un gasto"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    @patch("galaxia.api.procesar_mensaje_ollama")
    def test_chat_creates_pending_proposal(self, process_message):
        process_message.return_value = {
            "modulo": "Finanzas",
            "accion": "Gasto",
            "datos": {"monto": 15000, "descripcion": "Bencina"},
        }
        response = self.client.post(
            "/api/chat",
            data={"texto": "gasté 15 lucas en bencina"},
            content_type="application/json",
            headers={"X-API-Key": "test-api-key"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["estado"], "pendiente")
        self.assertEqual(PropuestaIA.objects.count(), 1)

    @patch("galaxia.api.procesar_mensaje_ollama")
    def test_food_proposal_is_only_executed_after_confirmation(
        self,
        process_message,
    ):
        process_message.return_value = {
            "modulo": "Comida",
            "accion": "Registrar comida",
            "datos": {
                "tipo": "Once",
                "descripcion": "Dos panes con queso y un té",
            },
        }
        response = self.client.post(
            "/api/chat",
            data={"texto": "Comí dos panes con queso y un té para la once"},
            content_type="application/json",
            headers={"X-API-Key": "test-api-key"},
        )

        propuesta_id = response.json()["propuesta_id"]
        self.assertEqual(RegistroComida.objects.count(), 0)

        confirmation = self.client.post(
            f"/api/chat/propuestas/{propuesta_id}/confirmar",
            content_type="application/json",
            headers={"X-API-Key": "test-api-key"},
        )

        self.assertEqual(confirmation.status_code, 200)
        self.assertEqual(confirmation.json()["estado"], "éxito")
        self.assertEqual(RegistroComida.objects.count(), 1)
        self.assertEqual(RegistroComida.objects.get().tipo, "Once")
