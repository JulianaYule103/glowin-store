from django.shortcuts import render, redirect
from django.contrib.auth import logout
from productos.models import Producto, Categoria  # 👈 asegúrate de tener esto

def home(request):
    destacados = Producto.objects.all()[:4]
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'index.html', {
        'destacados': destacados,
        'categorias': categorias,
    })

def logout_view(request):
    logout(request)
    return redirect('home')


