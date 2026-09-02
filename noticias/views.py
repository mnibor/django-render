from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView

from .models import Articulo


class ArticuloCreateView(LoginRequiredMixin, CreateView):
    model = Articulo
    fields = ["titulo", "bajada", "desarrollo"]
    template_name = "noticias/form.html"

    def form_valid(self, form):
        # El autor es siempre el usuario autenticado
        form.instance.autor = self.request.user
        return super().form_valid(form)


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
