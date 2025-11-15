from django.urls import path
from . import views

urlpatterns = [
    # ✅ Listado de productos
    path('', views.lista_productos, name='lista_productos'),

    # ✅ Productos por categoría
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),


    # ✅ Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/<int:item_id>/sumar/', views.sumar_cantidad, name='sumar_cantidad'),
    path('carrito/<int:item_id>/restar/', views.restar_cantidad, name='restar_cantidad'),
    path('carrito/<int:item_id>/eliminar/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),

    # ✅ Agregar al carrito
    path('<int:producto_id>/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),

    # ✅ Detalle del producto
    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # ✅ Checkout
    path('checkout/', views.checkout, name='checkout'),

    # ✅ Crear orden antes de ir a WhatsApp (por si lo usas luego)
    path('procesar-orden/', views.procesar_orden, name='procesar_orden'),

    # ✅ Confirmación
    path("confirmacion/", views.confirmacion_pedido, name="confirmacion_pedido"),

    # ✅ Página de orden exitosa
    path('orden-exitosa/', views.orden_exitosa, name='orden_exitosa'),
]
