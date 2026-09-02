from django.contrib import admin

from .models import Articulo


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "fecha_creacion", "fecha_actualizacion")
    list_filter = ("autor", "fecha_creacion")
    search_fields = ("titulo", "bajada")
    date_hierarchy = "fecha_creacion"
    ordering = ("-fecha_creacion",)
