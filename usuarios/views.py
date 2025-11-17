from django.shortcuts import render, redirect
from django.contrib.auth import logout
from productos.models import Producto, Categoria

def home(request):

    categorias = Categoria.objects.all()

    # 💗 Todos los productos destacados marcados desde admin
    destacados = Producto.objects.filter(destacado=True)

    return render(request, "index.html", {
        "categorias": categorias,
        "destacados": destacados,
    })


def logout_view(request):
    logout(request)
    return redirect('home')
