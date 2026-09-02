# Noticias Tech — Blog Django para Render

Blog simple de noticias tecnológicas. Demo didáctica de **deploy monolito Django en [Render](https://render.com)** con una sola URL (`/` es el blog, `/admin` es el admin, `/crear` es el formulario para redactores).

> **Objetivo de la demo:** explicar cómo subir un proyecto Django a Render y qué limitaciones tiene la plataforma. Por eso el proyecto es intencionalmente **sin imágenes**.

## Stack

- **Django 6.1** + Gunicorn + WhiteNoise + dj-database-url + psycopg2-binary + python-decouple
- **Python 3.12** (ver `.python-version` y `Containerfile`)
- **PostgreSQL 16** (en Render y en local con Podman)
- CSS propio sin frameworks — **Nunito** (cuerpo/desarrollo) + **Merriweather** (títulos/bajadas) vía Google Fonts

## Modelo

`Articulo`: `titulo` (CharField), `bajada` (TextField ~150 palabras / 1100 chars), `desarrollo` (TextField lorem ipsum 4 párrafos), `autor` (FK User), `fecha_creacion` (auto_now_add), `fecha_actualizacion` (auto_now). Ordenado por más reciente primero (`-fecha_creacion`), paginado 5 por página. **Sin imagen** a propósito (ver Limitaciones).

## Usuarios de demo

Creados por `python manage.py seed_data` (idempotente, se puede correr N veces):

| Usuario | Password | Rol | Permisos |
|---------|----------|-----|----------|
| `admin` | `admin123` | superuser | ve todo, crea como sí mismo |
| `carlos.perez` | `carlos123` | redactor (is_staff) | add/change/view_articulo |
| `natalia.gomez` | `natalia123` | redactora (is_staff) | add/change/view_articulo |

9 artículos de tecnología (títulos reales, bajadas relacionadas, desarrollo lorem ipsum) repartidos entre Carlos y Natalia con fechas escalonadas para probar ordenamiento y paginación (5 en página 1, 4 en página 2).

### Crear notas como redactor

- **Admin:** `http://localhost:8000/admin/` → loguearse como `carlos.perez` → Artículos → Add. El campo `autor` no aparece: se asigna automáticamente al usuario logueado. Los redactores solo ven sus propias notas; `admin` ve todas.
- **Frontend:** `http://localhost:8000/crear/` (requiere login, `LoginRequiredMixin`). Formulario con `titulo/bajada/desarrollo`; el `autor` es siempre `request.user`.

## Correr en local

### Opción A: Podman (recomendada — igual que Render)

Reproduce el entorno de producción sin instalar Postgres en tu PC.

```bash
# Requiere podman y podman-compose (o podman compose con plugin)
podman-compose up --build
# o: podman compose up --build
```

Abrir http://localhost:8000 — Admin en http://localhost:8000/admin/ — Crear en http://localhost:8000/crear/

El `compose.yaml` ya trae `DATABASE_URL`, `SECRET_KEY`, `DEBUG=true` y `ALLOWED_HOSTS` con `0.0.0.0`. Ejecuta automáticamente `migrate` + `seed_data`.

```bash
# Re-seed manual si hace falta
podman-compose exec web python manage.py seed_data

# Ver usuarios
podman-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; print(list(get_user_model().objects.values_list('username', flat=True)))"

# Bajar
podman-compose down
# con volumen (borra DB): podman-compose down -v
```

### Opción B: SQLite sin contenedores (rápido para probar)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

> El proyecto usa `DATABASE_URL` si existe, sino cae a `sqlite:///db.sqlite3`. `DEBUG` y `SECRET_KEY` salen de env vars (`python-decouple`). `ALLOWED_HOSTS` incluye `0.0.0.0` para `runserver 0.0.0.0:8000` dentro de contenedores.

## Deploy en Render (Blueprint)

1. Pushear este repo a GitHub (`main` es la rama de producción).
2. En [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint** → conectar el repo (`https://github.com/mnibor/django-render.git`).
3. Render detecta `render.yaml` y crea automáticamente **Web Service** (runtime python) + **PostgreSQL** (plan free).
4. El `buildCommand` (`./build.sh`) hace `pip install`, `collectstatic`, `migrate` y `seed_data`.
5. Al terminar, la URL queda tipo `https://django-render-xxxx.onrender.com` — el admin es `/admin`, crear es `/crear`.

Variables que setea `render.yaml`: `SECRET_KEY` (generada), `DATABASE_URL` (inyectada por Render desde la DB), `ALLOWED_HOSTS=.onrender.com`, `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`, `PYTHON_VERSION=3.12.0`. `DEBUG=false` en Render. `RENDER_EXTERNAL_HOSTNAME` se agrega automáticamente a `ALLOWED_HOSTS`.

**Mismo código para `main` y `dev`, solo cambian env vars** (12-Factor App). No hay código distinto por rama. Local lee `compose.yaml`/`.env`, Render inyecta `DATABASE_URL`.

## Estructura

```
config/            # settings, urls, wsgi, asgi
noticias/          # app: models, admin, views, urls, management/commands/seed_data
templates/         # base.html, noticias/lista.html, noticias/detalle.html, noticias/form.html
static/css/        # styles.css (Nunito + Merriweather)
compose.yaml       # Podman (postgres:16 + web, dockerfile: Containerfile)
Containerfile      # Python 3.12-slim para Podman/Render
render.yaml        # Blueprint Render (web + postgres)
build.sh           # buildCommand Render
Procfile           # alternativa startCommand (gunicorn)
.python-version    # 3.12.0
```

`docs/` está excluido vía `.gitignore` (documentación interna, no se sube a GitHub).

## Limitaciones de Render (por qué este proyecto es sin imágenes)

Esta sección es parte de la demo. Si explicas el proyecto en clase, menciona estos 5 puntos:

### 1. Filesystem efímero — sin `media/` persistente
Cada deploy, reinicio o escalado borra lo escrito en disco. Un `ImageField` que guarda en `/app/media/` funcionaría 5 minutos y luego daría 404. Por eso el modelo **no tiene imagen**. Si se necesitaran imágenes, hay que usar almacenamiento externo:
- **Cloudinary** (recomendado para demo): `django-cloudinary-storage`, gratis hasta 25 GB.
- **AWS S3** con `django-storages`: más configurable, más complejo.
- **Render Disk**: disco persistente pago ($0.25/GB), atado a una sola instancia, no escala y no está en free tier.

### 2. Sleep en plan Free (cold start)
Tras 15 min sin tráfico, Render suspende el servicio. El siguiente request tarda 30-50 s en despertar. Es normal en free tier; en plan pago (`Starter`+) no ocurre.

### 3. PostgreSQL Free expira a los 90 días
La DB free se borra automáticamente a los 90 días (Render avisa por email). Para producción se recomienda Neon, Supabase o Postgres pago de Render. Para la demo es suficiente.

### 4. Variables de entorno, no código por rama
No se hace `if RENDER: ...`. Se usa `dj-database-url` + `python-decouple`: mismo `settings.py` lee `DATABASE_URL` local (Podman) o inyectada por Render. `main` y `dev` son idénticas en código.

### 5. Estáticos requieren WhiteNoise + collectstatic
Render no tiene Nginx. `build.sh` debe correr `collectstatic --no-input` y `WhiteNoise` sirve `STATIC_ROOT=staticfiles` en producción.

## Comandos útiles

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data          # crea/actualiza usuarios + 9 artículos
python manage.py createsuperuser
python manage.py collectstatic --no-input
podman-compose up --build
podman-compose logs -f web
```

## Notas

- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` aceptan listas separadas por coma (via `Csv()`). `RENDER_EXTERNAL_HOSTNAME` se agrega automáticamente si existe.
- Idioma `es-ar`, timezone `America/Argentina/Buenos_Aires`.
- Paginación: 5 artículos por página, orden `-fecha_creacion`.
