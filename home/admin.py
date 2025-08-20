from django.contrib import admin
from .models import Usuario, Produto, Empresa # Importe o modelo Produto

# Registre o modelo Usuario (se já não estiver registrado)
admin.site.register(Usuario)

# --- Registre o Novo Modelo Produto ---
admin.site.register(Produto)

# Registre os modelos para o painel de administração
admin.site.register(Empresa)