from django.shortcuts import render # type: ignore

# Create your views here.
def index(request):
    return render(request, "politicas/index.html", {})