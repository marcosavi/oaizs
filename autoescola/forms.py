from django import forms 
from django.contrib.auth.hashers import make_password 
from .models import CustomUser, Autoescola 

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'cpf']  # Assuming these are the fields in your form

    def save(self, commit=True):
        user = super().save(commit=False)
        email_part = user.email[:3]
        cpf_part = user.cpf[:6]
        user.username = f"{email_part}{cpf_part}"
        password = f"{email_part}{cpf_part}"
        user.password = make_password(password)
        if commit:
            user.save()
        return user

class AutoescolaForm(forms.ModelForm):
    class Meta:
        model = Autoescola
        fields = '__all__'