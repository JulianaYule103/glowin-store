from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import urllib.parse
import mercadopago
import os

from .models import (
    Producto,
    Carrito,
    CarritoItem,
    Orden,
    OrdenItem,
    Order,
    OrderItem,
    Categoria,
    Tono,
)
from .chatbot_ai import chatbot_respuesta


# ============================
#   MERCADO PAGO CALLBACKS
# ============================

def pago_exitoso(request):
    return render(request, "productos/pago_exitoso.html")


def pago_fallido(request):
    return render(request, "productos/pago_fallido.html")


def pago_pendiente(request):
    return render(request, "productos/pago_pendiente.html")


# ============================
#   CREAR PREFERENCIA MERCADO PAGO
# ============================

@csrf_exempt
def crear_preferencia_pago(request):
    print("====== ENTRÓ A crear_preferencia_pago ======")
    print("Método:", request.method)

    if request.method != "POST":
        print("❌ ERROR: método no permitido")
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        # Carrito
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        items = CarritoItem.objects.filter(carrito=carrito)

        print("Items en carrito:", items.count())

        if not items.exists():
            print("❌ Carrito vacío")
            return JsonResponse({"error": "Carrito vacío"}, status=400)

        # Token de MP
        access_token = settings.MP_ACCESS_TOKEN
        print("MP_ACCESS_TOKEN:", access_token)

        if not access_token:
            print("❌ ERROR: MP_ACCESS_TOKEN faltante")
            return JsonResponse({"error": "MP_ACCESS_TOKEN faltante"}, status=500)

        sdk = mercadopago.SDK(access_token)

        # Items para MP
        productos_mp = []
        for item in items:
            print(f"Agregando producto MP → {item.producto.nombre} x{item.cantidad}")
            productos_mp.append({
                "title": item.producto.nombre,
                "quantity": int(item.cantidad),
                "unit_price": int(item.producto.precio),
                "currency_id": "COP",
            })

        # Envío desde la sesión
        checkout = request.session.get("checkout", {})
        envio = checkout.get("envio", {})
        costo_envio = int(envio.get("costo", 0) or 0)

        print("Costo envío:", costo_envio)

        if costo_envio > 0:
            productos_mp.append({
                "title": "Envío",
                "quantity": 1,
                "unit_price": costo_envio,
                "currency_id": "COP",
            })

        # ============================
        #   CONFIG PREFERENCE SEGÚN ENTORNO
        # ============================

        full_url = request.build_absolute_uri()
        server_name = request.META.get("SERVER_NAME")

        print("FULL URL:", full_url)
        print("SERVER_NAME:", server_name)

        if (
    "127.0.0.1" in full_url
    or "localhost" in full_url
    or server_name.startswith("DESKTOP")
    or server_name.startswith("LAPTOP")
):
            # ⭐ MODO LOCAL: NO usar auto_return (MP lo rechaza en http)
            preference_data = {
                "items": productos_mp,
                "back_urls": {
                    "success": "https://www.mercadopago.com.co/",
                    "failure": "https://www.mercadopago.com.co/",
                    "pending": "https://www.mercadopago.com.co/",
                },
            }
        else:
            # ⭐ PRODUCCIÓN (cuando tengas dominio con HTTPS)
            preference_data = {
                "items": productos_mp,
                "back_urls": {
                    "success": request.build_absolute_uri(reverse("pago_exitoso")),
                    "failure": request.build_absolute_uri(reverse("pago_fallido")),
                    "pending": request.build_absolute_uri(reverse("pago_pendiente")),
                },
                "auto_return": "approved",
            }

        print("Creando preferencia en MP...")
        preference = sdk.preference().create(preference_data)
        print("Respuesta completa MP:", preference)

        if "response" not in preference or "id" not in preference["response"]:
            print("❌ ERROR: Mercado Pago no devolvió ID")
            return JsonResponse({"error": "Mercado Pago no devolvió ID"}, status=500)

        print("✔ preference_id:", preference["response"]["id"])

        return JsonResponse({
            "preference_id": preference["response"]["id"]
        })

    except Exception as e:
        import traceback
        print("======== ERROR REAL =========")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


# ============================
#   CHATBOT IA
# ============================

@csrf_exempt
def ia_chat(request):
    if request.method != "POST":
        return JsonResponse({"tipo": "error", "mensaje": "Solo POST"})

    try:
        user_msg = request.POST.get("mensaje", "")

        res = chatbot_respuesta(user_msg)

        if not isinstance(res, dict):
            return JsonResponse({
                "tipo": "texto",
                "mensaje": "Lo siento 💗, hubo un error interno."
            })

        return JsonResponse({
            "tipo": res.get("tipo", "texto"),
            "mensaje": res.get("mensaje", ""),
            "nombre": res.get("nombre", ""),
            "descripcion": res.get("descripcion", ""),
            "imagen": res.get("imagen", ""),
            "url": res.get("url", "")
        })

    except Exception as e:
        return JsonResponse({
            "tipo": "error",
            "mensaje": f"Error del servidor: {str(e)}"
        })


# ============================
#   LOGOUT
# ============================

def logout_view(request):
    logout(request)
    return redirect('home')


# ============================
#   LISTADO / BÚSQUEDA / DETALLE
# ============================

def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categoria': categoria,
    })


def buscar(request):
    query = request.GET.get("q", "").strip()

    resultados = []
    if query:
        resultados = Producto.objects.filter(nombre__icontains=query)

    return render(request, "productos/busqueda.html", {
        "query": query,
        "resultados": resultados
    })


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    context = {
        "producto": producto,
        "tallas": producto.tallas.all(),
        "colores": producto.colores.all(),
    }
    return render(request, "productos/detalle_producto.html", context)


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista_productos.html', {'productos': productos})


# ============================
#   CARRITO
# ============================

@login_required
def agregar_al_carrito(request, producto_id):

    if request.method != "POST":
        return redirect('detalle_producto', producto_id=producto_id)

    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    cantidad = int(request.POST.get("cantidad", 1))

    tono_id = request.POST.get("tono")
    tono = Tono.objects.filter(id=tono_id).first() if tono_id else None

    item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        tono=tono,
        defaults={'cantidad': cantidad}
    )

    if not created:
        item.cantidad += cantidad
        item.save()

    return redirect('detalle_producto', producto_id=producto_id)


@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()

    total = 0
    for item in items:
        item.subtotal = item.cantidad * item.producto.precio
        total += item.subtotal

    return render(request, 'productos/carrito.html', {
        'items': items,
        'total': total
    })


@login_required
def sumar_cantidad(request, item_id):
    item = CarritoItem.objects.get(id=item_id, carrito__usuario=request.user)
    item.cantidad += 1
    item.save()
    return redirect('ver_carrito')


@login_required
def restar_cantidad(request, item_id):
    item = CarritoItem.objects.get(id=item_id, carrito__usuario=request.user)

    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()

    return redirect('ver_carrito')


@login_required
def eliminar_item_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')


@login_required
def vaciar_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    carrito.items.all().delete()
    return redirect('ver_carrito')


# ============================
#   PROCESAR ORDEN (NO MP)
# ============================

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


# ============================
#   CHECKOUT PASO 1, 2, 3
# ============================

# 💸 Config de envío
ENVIO_ESTANDAR = 8000
ENVIO_RAPIDO = 12000
ENVIO_GRATIS_MINIMO = 120000


def _get_carrito_y_total(usuario):
    """Pequeña ayuda: devuelve carrito, items y total de productos."""
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    items = CarritoItem.objects.filter(carrito=carrito)

    total = 0
    for item in items:
        item.subtotal = item.cantidad * item.producto.precio
        total += item.subtotal

    return carrito, list(items), total


@login_required
def checkout_contacto(request):
    """
    PASO 1 – Datos de contacto
    """
    carrito, items, total = _get_carrito_y_total(request.user)

    if not items:
        return redirect('ver_carrito')

    checkout = request.session.get("checkout", {})
    datos_contacto = checkout.get("contacto", {})

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        email = request.POST.get("email", "").strip()

        checkout["contacto"] = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
        }
        request.session["checkout"] = checkout

        return redirect('checkout_envio')

    return render(request, "productos/checkout_contacto.html", {
        "items": items,
        "total": total,
        "contacto": datos_contacto,
    })


@login_required
def checkout_envio(request):
    """
    PASO 2 – Dirección y método de envío
    """
    carrito, items, total = _get_carrito_y_total(request.user)
    if not items:
        return redirect('ver_carrito')

    checkout = request.session.get("checkout", {})
    datos_envio = checkout.get("envio", {})

    envio_gratis = total >= ENVIO_GRATIS_MINIMO

    if request.method == "POST":
        direccion = request.POST.get("direccion", "").strip()
        ciudad = request.POST.get("ciudad", "").strip()
        departamento = request.POST.get("departamento", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        metodo_envio = request.POST.get("metodo_envio", "estandar")

        if envio_gratis:
            metodo_envio = "gratis"
            costo_envio = 0
        else:
            if metodo_envio == "rapido":
                costo_envio = ENVIO_RAPIDO
            else:
                metodo_envio = "estandar"
                costo_envio = ENVIO_ESTANDAR

        checkout["envio"] = {
            "direccion": direccion,
            "ciudad": ciudad,
            "departamento": departamento,
            "telefono": telefono,
            "metodo": metodo_envio,
            "costo": costo_envio,
        }
        request.session["checkout"] = checkout

        return redirect('checkout_resumen')

    return render(request, "productos/checkout_envio.html", {
        "items": items,
        "total": total,
        "envio": datos_envio,
        "envio_gratis": envio_gratis,
        "ENVIO_ESTANDAR": ENVIO_ESTANDAR,
        "ENVIO_RAPIDO": ENVIO_RAPIDO,
        "ENVIO_GRATIS_MINIMO": ENVIO_GRATIS_MINIMO,
    })


@login_required
def checkout_resumen(request):
    """
    PASO 3 – Resumen + pago
    """
    carrito, items, total_productos = _get_carrito_y_total(request.user)
    if not items:
        return redirect('ver_carrito')

    checkout = request.session.get("checkout", {})
    contacto = checkout.get("contacto", {})
    envio = checkout.get("envio", {})

    costo_envio = int(envio.get("costo", 0) or 0)
    total_final = total_productos + costo_envio

    return render(request, "productos/checkout_resumen.html", {
        "items": items,
        "total_productos": total_productos,
        "contacto": contacto,
        "envio": envio,
        "costo_envio": costo_envio,
        "total_final": total_final,
        "MP_PUBLIC_KEY": os.getenv("MP_PUBLIC_KEY"),
    })


# ============================
#   PÁGINAS DE ÉXITO
# ============================

def orden_exitosa(request):
    return render(request, "productos/orden_exitosa.html")


def confirmacion_pedido(request):
    return render(request, "productos/confirmacion.html")
