from django.urls import path # type: ignore
from . import views

app_name = "inicial"

urlpatterns = [
    path("", views.index, name = "index"),
]