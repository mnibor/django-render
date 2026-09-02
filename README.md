# Noticias Tech — Blog Django para Render

Blog simple de noticias tecnologicas. Demo de deploy monolito en [Render](https://render.com) (una sola URL, `/admin` es el admin de Django).

## Stack

- Django 4.2 + Gunicorn + WhiteNoise + dj-database-url + psycopg2-binary
- PostgreSQL 16 (Render y local con Podman)
- CSS propio sin frameworks — Nunito (cuerpo) + Merriweather (titulos/bajadas) via Google Fonts

## Modelo

`Articulo`: `titulo`, `bajada` (subtitulo ~150 palabras), `desarrollo` (lorem ipsum 4 parrafos), `autor` (FK User), `fecha_creacion`, `fecha_actualizacion`. Ordenado por mas reciente primero. Sin imagen.

## Usuarios de demo

Creados por `python manage.py seed_data` (idempotente):

| Usuario | Password | Rol |
|---------|----------|-----|
| `admin` | `admin123` | superuser |
| `carlos.perez` | `carlos123` | redactor |
| `natalia.gomez` | `natalia123` | redactora |

9 articulos repartidos entre Carlos y Natalia con fechas escalonadas para probar paginacion y ordenamiento (5 por pagina).

## Correr en local

### Opcion A: Podman (recomendada — igual que Render)

```bash
# Requiere podman y podman-compose (o podman compose con plugin)
cp .env.example .env   # opcional, compose.yaml ya trae defaults

podman-compose up --build
# o: podman compose up --build

# En otra terminal, si queres re-seedear:
podman-compose exec web python manage.py seed_data
```

Abrir http://localhost:8000 — Admin en http://localhost:8000/admin/

Para bajar:

```bash
podman-compose down
# con volumen: podman-compose down -v
```

### Opcion B: SQLite sin Docker (rapido para probar)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

> El proyecto usa `DATABASE_URL` si existe, sino cae a `sqlite:///db.sqlite3`. `DEBUG` y `SECRET_KEY` salen de env vars (`python-decouple`).

## Deploy en Render (Blueprint)

1. Pushear este repo a GitHub.
2. En [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint** → conectar el repo.
3. Render detecta `render.yaml` y crea el **Web Service** + **PostgreSQL** (plan free).
4. El `buildCommand` (`./build.sh`) hace `collectstatic`, `migrate` y `seed_data`.
5. Al terminar, la URL queda tipo `https://django-render-xxxx.onrender.com` — el admin es `/admin`.

Variables que setea `render.yaml`: `SECRET_KEY` (generada), `DATABASE_URL` (inyectada por Render), `ALLOWED_HOSTS=.onrender.com`, `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`. `DEBUG=false` en Render.

Mismo codigo para `main` y `dev`, solo cambian env vars.

## Estructura

```
config/            # settings, urls, wsgi
noticias/          # app: models, admin, views, urls, management/commands/seed_data
templates/         # base.html, noticias/lista.html, noticias/detalle.html
static/css/        # styles.css
compose.yaml       # Podman (postgres:16 + web)
Dockerfile         # para Render / local
render.yaml        # Blueprint Render
build.sh           # buildCommand Render
Procfile           # alternativa startCommand
```

## Comandos utiles

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

## Notas

- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` aceptan listas separadas por coma (via `python-decouple` Csv). Render inyecta `RENDER_EXTERNAL_HOSTNAME` automaticamente si existe.
- WhiteNoise sirve estaticos en produccion (`STATIC_ROOT=staticfiles`).
- Idioma `es-ar`, timezone `America/Argentina/Buenos_Aires`.
