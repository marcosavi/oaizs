from django.contrib import admin #type: ignore
from .models import Autoescola, CustomUser
from django.contrib.auth.admin import UserAdmin #type: ignore
from django import forms #type: ignore
 
# Register your models here.
class AutoescolaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ['nome']}
    fieldsets = (
        ('Dados da Autoescola', {'fields': ('nome', 'cnpj')}),
        ('Redes sociais', {'fields': ('whatsapp', 'facebook', 'instagram')}),
        ('Sobre a autoescola', {'fields': ('titulo', 'sub_titulo')}),
        ('Beneficios', {'fields': ('beneficio_1', 'beneficio_2', 'beneficio_3')}),
        ('Imagens', {'fields': ('logo', 'image_1', 'image_2', 'image_3', 'image_4')}),
        ('Depoimentos', {'fields': ('pergunta_frequente_1', 'pergunta_frequente_2', 'pergunta_frequente_3')}),
        ('Website SEO', {'fields': ('slug',)}),
    )
    

class MyUserAdmin(UserAdmin):
     model = CustomUser
     add_fieldsets  = (
        ("Cadastro", {'fields': ('username', 'email', 'cpf', 'password1', 'password2')}),
        ("Autoescola", {'fields': ('autoescola',)}),
        ("Permissoes", {'fields': ('groups',)}),
    )

admin.site.register(Autoescola, AutoescolaAdmin)
admin.site.register(CustomUser, MyUserAdmin)