from django import forms
from .models import Produto, Usuario

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'quantidade', 'preco']
        labels = {
            'nome': 'Nome do Produto',
            'descricao': 'Descrição',
            'quantidade': 'Quantidade',
            'preco': 'Preço Unitário',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'preco': forms.NumberInput(attrs={'step': '0.01'}),
        }

# Este é o único formulário de que precisamos para criar e editar usuários
class UsuarioForm(forms.ModelForm):
    # Tornamos a senha obrigatória na criação, mas não na edição.
    # A lógica para isso será controlada na view.
    senha = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Deixe em branco para não alterar.")
    
    # Novo campo para confirmação
    confirmar_senha = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirmar Senha")

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'login', 'senha', 'is_admin']
        labels = {
            'is_admin': 'Conceder permissões de Administrador?'
        }

    def __init__(self, *args, **kwargs):
        user_logado = kwargs.pop('user', None)
        # Identifica se o formulário está a ser usado para criar ou editar
        self.is_creating = kwargs.get('instance') is None
        super(UsuarioForm, self).__init__(*args, **kwargs)

        # Se estivermos a criar um novo usuário, a senha é obrigatória
        if self.is_creating:
            self.fields['senha'].required = True
            self.fields['confirmar_senha'].required = True

        if user_logado:
            primeiro_admin = Usuario.objects.filter(empresa=user_logado.empresa, is_admin=True).order_by('id').first()
            if user_logado != primeiro_admin:
                if 'is_admin' in self.fields:
                    del self.fields['is_admin']

    # Método para validar se as senhas coincidem
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        # Se ambos os campos de senha foram preenchidos, eles devem ser iguais
        if senha and confirmar_senha and senha != confirmar_senha:
            self.add_error('confirmar_senha', "As senhas não coincidem.")
        
        return cleaned_data