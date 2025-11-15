from django.contrib import admin
from .models import Producto, Categoria, Marca, Talla, Color, Tono
from django import forms
from django.utils.html import format_html

class TonoForm(forms.ModelForm):
    class Meta:
        model = Tono
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'})
        }


class TonoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color_display')
    fields = ('nombre', 'color')
    search_fields = ('nombre',)

    def color_display(self, obj):
        return format_html(
            '<div style="width:40px; height:20px; background-color:{}; border:1px solid #000;"></div>',
            obj.color
        )
    color_display.short_description = "Color"

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria')
    filter_horizontal = ('tallas', 'colores', 'tonos') 

admin.site.register(Tono, TonoAdmin)
admin.site.register(Marca)
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Talla)
admin.site.register(Color)