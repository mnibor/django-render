from django.urls import path

from .views import ArticuloCreateView, ArticuloDetailView, ArticuloListView

app_name = "noticias"

urlpatterns = [
    path("", ArticuloListView.as_view(), name="lista"),
    path("crear/", ArticuloCreateView.as_view(), name="crear"),
    path("articulo/<int:pk>/", ArticuloDetailView.as_view(), name="detalle"),
]
