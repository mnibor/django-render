from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from noticias.models import Articulo

User = get_user_model()

LOREM_PARAGRAPHS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Curabitur pretium tincidunt lacus, nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida.",
    "Sed auctor neque eu tellus rhoncus ut eleifend nibh porttitor. Ut in nulla enim. Phasellus molestie magna non est bibendum non venenatis nisl tempor. Suspendisse dictum feugiat nisl ut dapibus. Mauris iaculis porttitor posuere. Praesent id metus massa, ut blandit odio.",
    "Proin quis tortor orci. Etiam at risus et justo dignissim congue. Donec congue lacinia dui, a porttitor lectus condimentum laoreet. Nunc eu ullamcorper orci. Quisque eget odio ac lectus vestibulum faucibus eget in metus. In pellentesque faucibus vestibulum.",
]

ARTICULOS_DATA = [
    {
        "titulo": "OpenAI lanza GPT-5 con razonamiento multimodal avanzado",
        "bajada": "La nueva generacion del modelo promete mejoras drasticas en razonamiento logico, comprension de video y generacion de codigo, marcando un salto respecto a su predecesor y redefiniendo las expectativas del sector.",
    },
    {
        "titulo": "Argentina regula el uso de inteligencia artificial en el sector publico",
        "bajada": "El Gobierno presento un marco normativo que establece principios de transparencia, equidad y supervision humana para la implementacion de sistemas de IA en organismos estatales y servicios al ciudadano.",
    },
    {
        "titulo": "La computacion cuantica alcanza un nuevo hito con 1000 qubits estables",
        "bajada": "Investigadores de IBM y Google anunciaron avances que acercan la supremacia cuantica practica, con procesadores capaces de mantener coherencia durante tiempos record y corregir errores de forma automatica.",
    },
    {
        "titulo": "Ciberseguridad: detectan una vulnerabilidad critica en routers hogarenos",
        "bajada": "Expertos alertan sobre un fallo que afecta a millones de dispositivos a nivel global y recomiendan actualizar el firmware de inmediato para evitar accesos no autorizados a redes domesticas.",
    },
    {
        "titulo": "El mercado de vehiculos electricos crece un 40% en Latinoamerica",
        "bajada": "Impulsado por incentivos fiscales y la baja de precios de baterias, la adopcion de autos electricos se acelera en Brasil, Mexico y Argentina, superando las proyecciones de la industria automotriz.",
    },
    {
        "titulo": "GitHub Copilot supera los 20 millones de usuarios activos",
        "bajada": "La herramienta de autocompletado con IA se consolida como asistente indispensable para desarrolladores, con estudios que muestran un aumento de productividad de hasta el 55% en tareas cotidianas.",
    },
    {
        "titulo": "Europa aprueba la Ley de Chips para reducir dependencia de Asia",
        "bajada": "Con una inversion de 43.000 millones de euros, la Union Europea busca duplicar su cuota en la produccion mundial de semiconductores y garantizar el suministro de componentes estrategicos.",
    },
    {
        "titulo": "Realidad aumentada: Apple Vision Pro llega a Argentina a fin de ano",
        "bajada": "El visor de computacion espacial de Apple desembarcara con un ecosistema de apps locales y un precio que ya genera debate entre entusiastas y analistas del mercado tecnologico.",
    },
    {
        "titulo": "Python destrona a JavaScript como lenguaje mas popular segun Stack Overflow",
        "bajada": "Por primera vez en una decada, Python lidera el ranking de lenguajes mas usados y queridos por los desarrolladores, impulsado por su dominio en ciencia de datos e inteligencia artificial.",
    },
]


def build_desarrollo() -> str:
    return "\n\n".join(LOREM_PARAGRAPHS[:4])


class Command(BaseCommand):
    help = "Crea usuarios (admin, carlos.perez, natalia.gomez) y 9 articulos de demo"

    def handle(self, *args, **options):
        # Users
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Superuser admin / admin123 creado"))
        else:
            # ensure password / flags
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("Superuser admin actualizado (admin123)")

        carlos, c_created = User.objects.get_or_create(
            username="carlos.perez",
            defaults={
                "email": "carlos.perez@example.com",
                "first_name": "Carlos",
                "last_name": "Perez",
                "is_staff": True,
            },
        )
        if c_created:
            carlos.set_password("carlos123")
            carlos.first_name = "Carlos"
            carlos.last_name = "Perez"
            carlos.is_staff = True
            carlos.save()

        natalia, n_created = User.objects.get_or_create(
            username="natalia.gomez",
            defaults={
                "email": "natalia.gomez@example.com",
                "first_name": "Natalia",
                "last_name": "Gomez",
                "is_staff": True,
            },
        )
        if n_created:
            natalia.set_password("natalia123")
            natalia.first_name = "Natalia"
            natalia.last_name = "Gomez"
            natalia.is_staff = True
            natalia.save()

        for u in (carlos, natalia):
            if not u.has_usable_password() or c_created or n_created:
                # already set above; ensure
                pass

        # Fix passwords and staff if existing users had different ones (idempotent)
        if not c_created:
            carlos.set_password("carlos123")
            carlos.is_staff = True
            carlos.save()
        if not n_created:
            natalia.set_password("natalia123")
            natalia.is_staff = True
            natalia.save()

        # Permisos: redactores pueden crear/ver/cambiar articulos
        from django.contrib.auth.models import Permission

        perms = Permission.objects.filter(codename__in=["add_articulo", "change_articulo", "view_articulo"])
        for user in (carlos, natalia):
            user.user_permissions.add(*perms)

        self.stdout.write(f"Redactores: carlos.perez/carlos123, natalia.gomez/natalia123 (is_staff + permisos articulo)")

        # Articles: avoid duplicates by title
        autores = [carlos, natalia]
        now = timezone.now()
        desarrollo = build_desarrollo()

        created_count = 0
        for i, data in enumerate(ARTICULOS_DATA):
            if Articulo.objects.filter(titulo=data["titulo"]).exists():
                continue
            autor = autores[i % 2]
            # Staggered dates: most recent first = i=0 is newest
            fecha = now - timedelta(days=i, hours=i * 2)
            art = Articulo(
                titulo=data["titulo"],
                bajada=data["bajada"],
                desarrollo=desarrollo,
                autor=autor,
            )
            art.save()
            # Override auto_now_add to get staggered ordering
            Articulo.objects.filter(pk=art.pk).update(fecha_creacion=fecha, fecha_actualizacion=fecha)
            created_count += 1

        total = Articulo.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Articulos creados en esta corrida: {created_count} (total: {total})"))
