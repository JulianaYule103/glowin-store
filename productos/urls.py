from django.urls import path
from . import views
from .views import crear_preferencia_pago

urlpatterns = [
    path("ia-chat/", views.ia_chat, name="ia_chat"),

    path('productos/', views.lista_productos, name='lista_productos'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),

    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('<int:producto_id>/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),

    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/<int:item_id>/sumar/', views.sumar_cantidad, name='sumar_cantidad'),
    path('carrito/<int:item_id>/restar/', views.restar_cantidad, name='restar_cantidad'),
    path('carrito/<int:item_id>/eliminar/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),

    path('checkout/', views.checkout_contacto, name='checkout'),
    path('checkout/envio/', views.checkout_envio, name='checkout_envio'),
    path('checkout/resumen/', views.checkout_resumen, name='checkout_resumen'),
    path('procesar-orden/', views.procesar_orden, name='procesar_orden'),
    path('orden-exitosa/', views.orden_exitosa, name='orden_exitosa'),
    path('confirmacion/', views.confirmacion_pedido, name='confirmacion_pedido'),

    path("crear-preferencia/", crear_preferencia_pago, name="crear_preferencia"),
    path("pago-exitoso/", views.pago_exitoso, name="pago_exitoso"),
    path("pago-fallido/", views.pago_fallido, name="pago_fallido"),
    path("pago-pendiente/", views.pago_pendiente, name="pago_pendiente"),

    path("buscar/", views.buscar, name="buscar"),
]
