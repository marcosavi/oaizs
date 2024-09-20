from django.urls import path # type: ignore
from . import views

app_name = "autoescola"

urlpatterns = [
    path('acessar/', views.login.as_view(), name="login"),
    path('sair/', views.logout_view, name="logout"),
    path("<slug:slug>/", views.autoescola_page, name = "autoescola_page"),
    path("aluno/", views.AlunoListView.as_view(), name = "aluno"),
    path("", views.autoescola_form_view, name = "add-autoescola"),
]

