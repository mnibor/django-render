from django.views.generic import DetailView, ListView

from .models import Articulo


class ArticuloListView(ListView):
    model = Articulo
    template_name = "noticias/lista.html"
    context_object_name = "articulos"
    paginate_by = 5
    ordering = ["-fecha_creacion"]

    def get_queryset(self):
        return Articulo.objects.select_related("autor").order_by("-fecha_creacion")


class ArticuloDetailView(DetailView):
    model = Articulo
    template_name = "noticias/detalle.html"
    context_object_name = "articulo"

    def get_queryset(self):
        return Articulo.objects.select_related("autor")
