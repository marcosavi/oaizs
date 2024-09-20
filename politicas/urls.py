from django.urls import path # type: ignore
from . import views

app_name = "politicas"

urlpatterns = [
    path("", views.index, name = "index"),
]