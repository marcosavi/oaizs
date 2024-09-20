from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage 
from django.utils.text import slugify
from django_cpf_cnpj.fields import CPFField, CNPJField


# Create your models here.
class Autoescola(models.Model):
    #Totally AI generated 
    titulo = models.CharField("Título (opcional)", max_length=200, blank = True, null = True)
    sub_titulo = models.CharField("Sub-Título (opcional)", max_length=500, blank = True, null = True)
    #Partially AI generated
    beneficio_1 = models.CharField("Beneficio 1 (opcional)", max_length=200, blank = True, null = True)
    beneficio_2 = models.CharField("Beneficio 2 (opcional)", max_length=200, blank = True, null = True)
    beneficio_3 = models.CharField("Beneficio 3 (opcional)", max_length=200, blank = True, null = True)
    #Non-AI generated
    nome = models.CharField("Nome da autoescola (*)", max_length=64, blank = False, help_text = "Exemplo: X")
    cnpj = CNPJField(masked = True)
    endereco = models.CharField("Endereço (opcional)", max_length=200, blank = True, null = True)
    
    whatsapp = models.CharField("Whatsapp (opcional)", max_length = 50, blank = True, null = True)
    facebook = models.CharField("Facebook (opcional)", max_length = 50, blank = True, null = True)
    instagram = models.CharField("Instagram (opcional)", max_length = 50, blank = True, null = True)
    
    image_1 = models.TextField(blank = True, null = True)
    image_2 = models.TextField(blank = True, null = True)
    image_3 = models.TextField(blank = True, null = True)
    image_4 = models.TextField(blank = True, null = True)
    logo = models.ImageField(storage=FileSystemStorage)

    endereco_iframe = models.TextField(blank = True, null = True)
    endereco_formated = models.CharField(max_length = 70, blank = True, null = True)
    pergunta_frequente_1 = models.CharField("Pergunta frequente 1 (opcional)",  max_length = 300, blank = True, null = True)
    pergunta_frequente_2 = models.CharField("Pergunta frequente 2 (opcional)",  max_length = 300, blank = True, null = True)
    pergunta_frequente_3 = models.CharField("Pergunta frequente 3 (opcional)",  max_length = 300, blank = True, null = True)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.nome}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            original_slug = slugify(self.nome)
            queryset = Autoescola.objects.filter(slug__iexact=original_slug).count()
            count = 1
            slug = original_slug
            while(queryset):
                slug = f'{original_slug}-{count}'
                count += 1
                queryset = Autoescola.objects.filter(slug__iexact=slug).count()
            self.slug = slug
        super(Autoescola, self).save(*args, **kwargs)
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = 'images/placeholder.png'
        return url
    
class CustomUser(AbstractUser):
    autoescola = models.ForeignKey(Autoescola, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=100, unique = True)
    cpf = models.CharField(max_length = 11, unique = True)
    last_login_date = models.DateField(null=True, blank=True)
    login_streak = models.IntegerField(default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']