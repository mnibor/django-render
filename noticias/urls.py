from django.urls import path

from .views import ArticuloDetailView, ArticuloListView

app_name = "noticias"

urlpatterns = [
    path("", ArticuloListView.as_view(), name="lista"),
    path("articulo/<int:pk>/", ArticuloDetailView.as_view(), name="detalle"),
]
