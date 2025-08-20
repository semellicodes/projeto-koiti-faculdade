from django.db import models

class Empresa(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

class Usuario(models.Model):
    nome = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    login = models.CharField(max_length=20, unique=True)
    senha = models.CharField(max_length=128)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios')
    is_admin = models.BooleanField(default=False, help_text="Indica se o usuário é administrador da empresa.")

    def __str__(self):
        return f"{self.nome} ({self.empresa.nome})"

class Produto(models.Model):
    nome = models.CharField(max_length=200, help_text="Nome do produto.")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição detalhada do produto.")
    quantidade = models.IntegerField(default=0, help_text="Quantidade atual em estoque.")
    preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Preço unitário do produto.")
    data_entrada = models.DateTimeField(auto_now_add=True, help_text="Data em que o produto foi registrado.")
    ultima_atualizacao = models.DateTimeField(auto_now=True, help_text="Última vez que as informações do produto foram atualizadas.")
    # O produto agora pertence a uma empresa, não a um usuário
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos')

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return self.nome