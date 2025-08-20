"""
URL configuration for projeto_koiti project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home import views as home_views # Importe as views da app home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')), # Mantenha esta linha para as URLs de login/cadastro
    path('produtos/', home_views.lista_produtos, name='lista_produtos_root'), # Nova linha para a lista de produtos
    path('', home_views.home, name='landing_page'), 
]

