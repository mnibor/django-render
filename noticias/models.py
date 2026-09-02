from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.urls import reverse


class Articulo(models.Model):
    """News article."""

    titulo = models.CharField(max_length=200)
    # ~150 words ≈ ~900 chars (average 6 chars per word). Use 1100 to be safe.
    bajada = models.TextField(
        validators=[MaxLengthValidator(1100)],
        help_text="Subtitulo / bajada - max 150 palabras aprox (1100 caracteres)",
    )
    desarrollo = models.TextField(help_text="Contenido largo del articulo")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articulos",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Articulo"
        verbose_name_plural = "Articulos"

    def __str__(self) -> str:
        return self.titulo

    def get_absolute_url(self):
        return reverse("noticias:detalle", kwargs={"pk": self.pk})
