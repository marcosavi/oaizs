from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect 
from .models import Autoescola, CustomUser
from django.contrib import messages
from autoescola.forms import CustomUserForm, AutoescolaForm
from django.views.generic.list import ListView 
from django.contrib.auth.mixins import LoginRequiredMixin 
import openai 
from openai import OpenAI
from django.conf import settings

openai.api_key = settings.OPENAI

# Create your views here.
def index(request):
    return render(request, "autoescola/index.html", {})

class login(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.groups.filter(name='Moderador').exists() or user.groups.filter(name='Aluno').exists():
                autoescola_slug = user.autoescola.slug
                return reverse_lazy('autoescola:autoescola_page', kwargs={'slug': autoescola_slug})
            elif user.is_superuser:
                return reverse_lazy('admin:index')
            elif not user.is_superuser:
                return reverse_lazy('autoescola:aluno')
        return reverse_lazy('inicial:index')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("inicial:index"))

def autoescola_page(request, slug):
    autoescola = Autoescola.objects.get(slug=slug)
    users = CustomUser.objects.filter(autoescola=autoescola)
    user_is_moderador = request.user.groups.filter(name='Moderador').exists()

    if request.method == 'POST':
        if 'delete_user_id' in request.POST:  # Check if the deletion form was submitted
            user_id = int(request.POST.get('delete_user_id'))
            if user_id == request.user.id:
                # Prevent users from deleting themselves
                messages.error(request, "Você não pode deletar sua própria conta.")
                return HttpResponseRedirect(reverse('autoescola:autoescola_page', kwargs={'slug': slug}))
            user_to_delete = get_object_or_404(CustomUser, id=user_id, autoescola=autoescola)
            user_to_delete.delete()
            messages.success(request, "Usuário deletado com sucesso.")
            return HttpResponseRedirect(reverse('autoescola:autoescola_page', kwargs={'slug': slug}))

        form = CustomUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.autoescola = autoescola
            new_user.save()
            return HttpResponseRedirect(reverse('autoescola:autoescola_page', kwargs={'slug': slug}))

    else:
        form = CustomUserForm()

    return render(request, "autoescola/autoescola_page.html", {
        'autoescola': autoescola,
        'user_is_moderador': user_is_moderador,
        'users': users,
        'form': form
    })

class AlunoListView(LoginRequiredMixin, ListView):
    model = Autoescola
    template_name = "autoescola/aluno.html"
    login_url = "autoescola:login"

# OpenAI - #1 - Melhorar qualidades, gerando beneficios
def improve_text(texts):
    improved_texts = []
    for text in texts:
        try:
            completion = OpenAI().chat.completions.create(
            model="gpt-4-turbo",
            messages = [
        {"role": "system", "content": "Você é um especialista em copywriting, escrevendo benficios chamativos e engajantes para autoescolas brasileiras. Os beneficios dever sempre finalizar com um ponto final."},
        {"role": "user", "content": f"Melhore o seguinte beneficio: {text}. Cada beneficio deve conter cerca de 80 caracteres. Se houver palavras para destacar, as entorne com '<b> e </b>'."},
        ],
        )
            improved_text = completion.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            improved_text = text
        improved_texts.append(improved_text)
    return improved_texts

# OpenAI - #2 - Gerar Headline
def generate_titulo(beneficios):
    completion = OpenAI().chat.completions.create(
            model="gpt-4-turbo",
            messages = [
                            {"role": "system", "content": "Você é um especialista em copywriting, escrevendo uma headline chamativa para um site de uma autoescola. Você se baseará nos beneficios dessa autoescola."},
                            {"role": "user", "content": f"Esses sao os beneficios para você se basear na hora de escrevar a sua headline para o site: {beneficios[0]}, {beneficios[1]}, {beneficios[2]}. Super importante: A headline deve conter no máximo 70 caracteres, nao deve haver aspas (nem separadores e pontos de exclamaçao), ser uma única sentença e ter emojis ao invés de ponto final"},
                        ])
    return completion.choices[0].message.content

# OpenAI - #3 - Gerar iframe com base no endereço
def generate_iframe_endereco(endereco):
    completion = OpenAI().chat.completions.create(
        model="gpt-4-turbo",
        messages = [
            {"role":"system", "content":"Eu vou te prover um endereço, que sempre será no Brasil, e você me retornará o 'embedded' code desse local (iframe), usando o Google Maps para eu adicionar em meu website (HTML). Eu apenas quero o código iframe. Nunca diga uma palavra além do código iframe."},
            {"role":"user", "content":f"Esse é o ondereço que você se baseará para gerar o código iframe: {endereco}"},
        ])
    return completion.choices[0].message.content 

# OpenAI - Gerar endereço formatado
def generate_formated_endereco(endereco):
     completion = OpenAI().chat.completions.create(
        model = "gpt-4-turbo",
        messages = [
            {"role":"system", "content":"Eu irei lhe fornecer um endereço e você irá simplesmente o formatar seguindo o seguinte padrao: 'Cidade (Sigla do Estado), País' "},
            {"role":"user", "content":f"Formate o seguinte endereço: {endereco}"},
        ])
     return completion.choices[0].message.content

# OpenAI - #4 - Gerar subtitulo com base nos beneficios
def generate_sub_titulo(beneficios):
    completion = OpenAI().chat.completions.create(
        model = "gpt-4-turbo",
        messages = [
            {"role": "system", "content": "Você é um especialista em copywriting, escrevendo uma headline chamativa para um site de uma autoescola. Você se baseará nos beneficios dessa autoescola. "},
            {"role": "user", "content": f"Esses sao os beneficios para você se basear na hora de escrevar a sua headline para o site: {beneficios[0]}, {beneficios[1]}, {beneficios[2]}. Eu apenas preciso da headline. Em hipotese alguma me forneça algo adicional. Além disso, nao use aspas e evite ':'."},
        ])
    return completion.choices[0].message.content

# OpenAI - #5 - Gerar imagem Geral
"""def generate_image_main(beneficios):
        response = OpenAI().images.generate(
            model="dall-e-2",
            prompt= f"Gere uma imagem que retrate esses três aspectos: {beneficios[0]}, {beneficios[1]}, {beneficios[2]}. Nao inclua texto nas imagens. A imagem deve ser baseada na realidade de uma autoescola brasileira.",
            size="256x256",
            quality="standard",
            n=1,
        )
        image_generate_1 = response.data[0].url
        return image_generate_1"""

# OpenAI - #6 - Gerar imagem 'Beneficio 1' 
"""def generate_image_1(improved_beneficio_1):
        response = OpenAI().images.generate(
            model="dall-e-2",
            prompt= f"Gere uma imagem baseada no que foi dito em {improved_beneficio_1}. Nao inclua texto nas imagens. A imagem deve ser baseada na realidade de uma autoescola brasileira.",
            size="256x256",
            quality="standard",
            n=1,
        )
        image_generate_1 = response.data[0].url
        return image_generate_1"""
    
# OpenAI - #6 - Gerar imagem 'Beneficio 2' 
"""def generate_image_2(improved_beneficio_2):
        response = OpenAI().images.generate(
            model="dall-e-2",
            prompt= f"Gere uma imagem baseada no que foi dito em {improved_beneficio_2}. Nao inclua texto nas imagens. A imagem deve ser baseada na realidade de uma autoescola brasileira.",
            size="256x256",
            quality="standard",
            n=1,
        )
        image_generate_2 = response.data[0].url
        return image_generate_2"""


# OpenAI - #7 - Gerar imagem 'Beneficio 3' 

"""def generate_image_3(improved_beneficio_3):
        response = OpenAI().images.generate(
            model="dall-e-2",
            prompt= f"Gere uma imagem baseada no que foi dito em {improved_beneficio_3}. Nao inclua texto nas imagens. A imagem deve ser baseada na realidade de uma autoescola brasileira.",
            size="256x256",
            quality="standard",
            n=1,
        )
        image_generate_3 = response.data[0].url
        return image_generate_3"""


def autoescola_form_view(request):
    if request.method == 'POST':
        form = AutoescolaForm(request.POST, request.FILES)
        if form.is_valid():
            autoescola = form.save(commit=False)

            #function: generate_formated_endereco
            endereco = autoescola.endereco
            formated_endereco = generate_formated_endereco(endereco)
            autoescola.endereco_formated = formated_endereco

            #function: generate_iframe_endereco
            generated_iframe = generate_iframe_endereco(endereco)
            autoescola.endereco_iframe = generated_iframe

            #function: improve_text
            beneficios = [autoescola.beneficio_1, autoescola.beneficio_2, autoescola.beneficio_3]
            improved_beneficios = improve_text(beneficios)
            autoescola.beneficio_1, autoescola.beneficio_2, autoescola.beneficio_3 = improved_beneficios

            #function: generate_sub_titulo and generate_titulo
            improved_beneficio_1 = improved_beneficios[0]
            improved_beneficio_2 = improved_beneficios[1]
            improved_beneficio_3 = improved_beneficios[2]
            #autoescola.image_1 = generate_image_main(beneficios)
            #autoescola.image_2 = generate_image_1(improved_beneficio_1)
            #autoescola.image_3 = generate_image_2(improved_beneficio_2)
            #autoescola.image_4 = generate_image_3(improved_beneficio_3)

            #function: generate_sub_titulo and generate_titulo
            autoescola.titulo = generate_titulo(improved_beneficios)
            autoescola.sub_titulo = generate_sub_titulo(improved_beneficios)
            autoescola.save()
            return redirect('autoescola:autoescola_page', slug=autoescola.slug)
        else:
            # Print form errors to debug
            print(form.errors)
    else:
        form = AutoescolaForm()
    return render(request, 'autoescola/add-autoescola.html', {'form': form})