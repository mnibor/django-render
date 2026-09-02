from django.contrib import admin

from .models import Articulo


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "fecha_creacion", "fecha_actualizacion")
    list_filter = ("autor", "fecha_creacion")
    search_fields = ("titulo", "bajada")
    date_hierarchy = "fecha_creacion"
    ordering = ("-fecha_creacion",)
    exclude = ("autor",)

    def save_model(self, request, obj, form, change):
        # El autor siempre es el usuario logueado que crea la nota
        if not change or not obj.autor_id:
            obj.autor = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Superusers ven todo, redactores solo sus notas
        if request.user.is_superuser:
            return qs
        return qs.filter(autor=request.user)
