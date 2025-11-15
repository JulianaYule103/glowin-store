from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import urllib.parse
from .models import Producto, Carrito, CarritoItem, Orden, OrdenItem, Order, OrderItem, Categoria, Tono




# ✅ Productos por categoría

def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categoria': categoria,
    })


# ✅ Detalle del producto
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    context = {
        "producto": producto,
        "tallas": producto.tallas.all(),
        "colores": producto.colores.all(),
    }
    return render(request, "productos/detalle_producto.html", context)


# ✅ Listar productos
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista_productos.html', {'productos': productos})


# ✅ Agregar producto al carrito
@login_required
def agregar_al_carrito(request, producto_id):
    # SOLO aceptar método POST (evita errores y tonos vacíos)
    if request.method != "POST":
        return redirect('detalle_producto', producto_id=producto_id)

    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    # Cantidad enviada desde el formulario
    cantidad = int(request.POST.get("cantidad", 1))

    # Tono seleccionado
    tono_id = request.POST.get("tono")
    tono = None
    if tono_id and tono_id != "":
        tono = Tono.objects.filter(id=tono_id).first()

    # Buscar item con mismo producto y mismo tono
    item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        tono=tono,
        defaults={'cantidad': cantidad}
    )

    if not created:
        item.cantidad += cantidad
        item.save()

    return redirect('ver_carrito')

# ✅ Ver carrito
@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()

    total = sum(item.cantidad * item.producto.precio for item in items)

    return render(request, 'productos/carrito.html', {
        'items': items,
        'total': total
    })


# ✅ Aumentar cantidad
@login_required
def sumar_cantidad(request, item_id):
    item = CarritoItem.objects.get(id=item_id, carrito__usuario=request.user)
    item.cantidad += 1
    item.save()
    return redirect('ver_carrito')


# ✅ Restar cantidad
@login_required
def restar_cantidad(request, item_id):
    item = CarritoItem.objects.get(id=item_id, carrito__usuario=request.user)

    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()

    return redirect('ver_carrito')


# ✅ Eliminar producto
@login_required
def eliminar_item_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')


# ✅ Vaciar carrito
@login_required
def vaciar_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    carrito.items.all().delete()
    return redirect('ver_carrito')


@login_required
def procesar_orden(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = CarritoItem.objects.filter(carrito=carrito)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        direccion = request.POST.get("direccion")
        telefono = request.POST.get("telefono")

        total = sum(item.cantidad * item.producto.precio for item in items)

        orden = Orden.objects.create(
            usuario=request.user,
            nombre=nombre,
            email=email,
            direccion=direccion,
            telefono=telefono,
            total=total
        )

        for item in items:
            OrdenItem.objects.create(
                orden=orden,
                producto=item.producto.nombre,
                cantidad=item.cantidad,
                precio=item.producto.precio,
                subtotal=item.cantidad * item.producto.precio
            )

        carrito.items.all().delete()

        return redirect("orden_exitosa")

    return redirect("checkout")


# ✅ Checkout nuevo con WhatsApp
@login_required
def checkout(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = CarritoItem.objects.filter(carrito=carrito)

    total = 0
    for item in items:
        item.subtotal = item.cantidad * item.producto.precio
        total += item.subtotal

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        email = request.POST.get("email")
        direccion = request.POST.get("direccion")
        ciudad = request.POST.get("ciudad")
        departamento = request.POST.get("departamento")
        telefono = request.POST.get("telefono")
        metodo_pago = request.POST.get("metodo_pago")

        order = Order.objects.create(
            usuario=request.user,
            nombre=nombre,
            apellido=apellido,
            email=email,
            direccion=direccion,
            ciudad=ciudad,
            departamento=departamento,
            telefono=telefono,
            metodo_pago=metodo_pago,
            total=total
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                producto=item.producto.nombre,
                cantidad=item.cantidad,
                subtotal=item.subtotal
            )

        carrito.items.all().delete()

        mensaje = f"""
✨ NUEVO PEDIDO en Glowin ✨

👤 Cliente: {nombre} {apellido}
📧 Email: {email}
📞 Tel: {telefono}
📍 Dirección: {direccion}, {ciudad}, {departamento}

🛍️ Productos:
"""
        for item in items:
            mensaje += f"- {item.producto.nombre} x {item.cantidad} = ${int(item.subtotal):,}\n"

        mensaje += f"\n💰 Total: ${int(total):,}\n🚚 Método: {metodo_pago}"
        mensaje = urllib.parse.quote(mensaje)

        whatsapp_url = f"https://wa.me/573134606253?text={mensaje}"  # cambia tu número
        return redirect(whatsapp_url)

    return render(request, "productos/checkout.html", {
        "items": items,
        "total": total,
        "usuario": request.user
    })


# ✅ Página después de pagar (opcional)
def orden_exitosa(request):
    return render(request, "productos/orden_exitosa.html")

def confirmacion_pedido(request):
    return render(request, "productos/confirmacion.html")

