from django.contrib import admin
from .models import Usuario, Cargo


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado', 'modificado', 'ativo')

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('cargo','nivel' , 'criado', 'modificado', 'ativo')
