# GALAXIA

Sistema de gestión personal construido como un monolito modular con Django.

## Módulos

- **Pluto**: finanzas, categorías y transacciones.
- **Cronos**: cuentas de Google y eventos de calendario.
- **Hefesto**: vehículo, combustible y mantenimiento.
- **Deméter**: productos, despensa y registro de comidas.
- **Ares**: módulo reservado para ejercicio y estado físico.

## Tecnologías

- Python
- Django
- MySQL 8
- Docker Compose
- Django Ninja
- Ollama

## Requisitos

- Python 3.12 o superior
- Docker Desktop
- Git

## Instalación

Clona el repositorio y entra en la carpeta del proyecto:

```powershell
git clone https://github.com/Bravo-Sama/GALAXIA.git
Set-Location GALAXIA
```

Crea y activa un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
pip install django django-ninja requests mysqlclient
```

Define la contraseña de MySQL en un archivo `.env` en la raíz:

```env
MYSQL_ROOT_PASSWORD=tu_clave_segura
```

Usa [.env.example](./.env.example) como plantilla y define también una
contraseña distinta para `MYSQL_PASSWORD`, además de `DJANGO_SECRET_KEY` y
`GALAXIA_API_KEY`. El archivo `.env` está excluido de Git y no debe subirse al
repositorio.

## Base de datos

Levanta MySQL y phpMyAdmin:

```powershell
docker compose up -d
```

Servicios disponibles:

- MySQL: `127.0.0.1:3306`
- phpMyAdmin: <http://localhost:8080>

Aplica las migraciones:

```powershell
python manage.py migrate
```

La API requiere el encabezado:

```text
X-API-Key: tu_api_key
```

El endpoint `POST /api/chat` solo genera una propuesta. La operación debe
confirmarse mediante `POST /api/chat/propuestas/{id}/confirmar`.

Las propuestas expiran después de 10 minutos y solo pueden confirmarse una
vez. El endpoint de chat no modifica directamente la base de datos de negocio.

Opcionalmente, crea un usuario administrador:

```powershell
python manage.py createsuperuser
```

## Ejecutar el proyecto

```powershell
python manage.py runserver
```

Panel administrativo:

<http://127.0.0.1:8000/admin/>

## API

La API principal está disponible bajo `/api/`:

- `GET /api/finanzas/transacciones`
- `GET /api/auto/mantenimientos`
- `POST /api/chat`

Ejemplo para el endpoint de chat:

```json
{
  "texto": "Cargué 15 lucas de bencina"
}
```

El endpoint de chat utiliza Ollama localmente. Por defecto espera el servicio
en `http://localhost:11434/api/generate` y el modelo `llama3.2`.

Puedes personalizarlo mediante variables de entorno:

```env
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2
```

## Migraciones

Después de modificar modelos:

```powershell
python manage.py makemigrations
python manage.py migrate
```

## Seguridad

No subas contraseñas, tokens de Google, claves de Ollama ni archivos `.env`.
Usa variables de entorno para toda configuración sensible.
