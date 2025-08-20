from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('cadastro/sucesso/', views.cadastro_success, name='cadastro_success'), # NOVA LINHA
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('produtos/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('produtos/editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('produtos/excluir/<int:pk>/', views.excluir_produto, name='excluir_produto'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/adicionar/', views.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),

]