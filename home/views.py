from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Produto, Empresa
from .forms import ProdutoForm, UsuarioForm

# --- DECORATOR ATUALIZADO ---
def usuario_required(view_func):
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            messages.error(request, 'Você precisa estar logado para acessar esta página.')
            return redirect('login')
        try:
            # Armazenamos o usuário e a empresa na requisição para fácil acesso
            request.current_usuario = Usuario.objects.get(pk=usuario_id)
            request.current_empresa = request.current_usuario.empresa
        except Usuario.DoesNotExist:
            messages.error(request, 'Sessão inválida. Por favor, faça login novamente.')
            if 'usuario_id' in request.session:
                del request.session['usuario_id']
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.current_usuario.is_admin:
            messages.error(request, 'Você não tem permissão de administrador para acessar esta página.')
            return redirect('lista_produtos')
        return view_func(request, *args, **kwargs)
    return usuario_required(wrapper) # Usamos o usuario_required como base

def home(request):
    return render(request, 'home.html')

# --- VIEW DE CADASTRO ATUALIZADA ---
def cadastro(request):
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa')
        nome_admin = request.POST.get('nome_admin')
        email = request.POST.get('email')
        login = request.POST.get('login')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'cadastro.html')

        if Empresa.objects.filter(nome=nome_empresa).exists():
            messages.error(request, 'Já existe uma empresa com este nome.')
        elif Usuario.objects.filter(login=login).exists():
            messages.error(request, 'Este login já está em uso.')
        elif Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está em uso.')
        else:
            nova_empresa = Empresa.objects.create(nome=nome_empresa)
            
            admin = Usuario.objects.create(
                nome=nome_admin,
                email=email,
                login=login,
                # A SENHA AGORA É CRIPTOGRAFADA
                senha=make_password(senha),
                empresa=nova_empresa,
                is_admin=True
            )
            
            request.session['usuario_id'] = admin.id
            messages.success(request, f'Empresa "{nome_empresa}" cadastrada com sucesso!')
            return redirect('cadastro_success')
            
    return render(request, 'cadastro.html')


def cadastro_success(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        # Se não houver sessão, redireciona para o login
        return redirect('login')

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        # Se o usuário da sessão não existe mais, limpa a sessão
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        return redirect('login')
            
    context = {
        'usuario': usuario,
        'empresa': usuario.empresa
    }
    return render(request, 'cadastro_success.html', context)


def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('login')
        senha_input = request.POST.get('senha')

        try:
            usuario = Usuario.objects.get(login=login_input)
            # A verificação de senha agora usa check_password
            if check_password(senha_input, usuario.senha):
                request.session['usuario_id'] = usuario.id
                messages.success(request, f'Login realizado com sucesso! Bem-vindo, {usuario.nome}.')
                return redirect('lista_produtos')
            else:
                messages.error(request, 'Senha incorreta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Login não encontrado.')
    return render(request, 'login.html')

def logout_view(request):
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    messages.info(request, 'Você foi desconectado.')
    return redirect('home')

# --- VIEWS DE PRODUTO ATUALIZADAS ---

@usuario_required
def lista_produtos(request):
    # Filtra os produtos pela empresa do usuário logado
    produtos = Produto.objects.filter(empresa=request.current_empresa)
    context = {
        'produtos': produtos,
        'usuario': request.current_usuario # Passa o usuário para o template
    }
    return render(request, 'lista_produtos.html', context)

@usuario_required
def adicionar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            # Associa o produto à empresa do usuário logado
            produto.empresa = request.current_empresa
            produto.save()
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('lista_produtos')
        else:
            messages.error(request, 'Ocorreu um erro ao adicionar o produto. Verifique os dados.')
    else:
        form = ProdutoForm()
    
    context = {
        'form': form
    }
    return render(request, 'adicionar_produto.html', context)

@usuario_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    # Verifica se o produto pertence à empresa do usuário
    if produto.empresa != request.current_empresa:
        messages.error(request, 'Você não tem permissão para editar este produto.')
        return redirect('lista_produtos')
        
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('lista_produtos')
        else:
            messages.error(request, 'Ocorreu um erro ao atualizar o produto. Verifique os dados.')
    else:
        form = ProdutoForm(instance=produto)
    
    context = {
        'form': form,
        'produto': produto
    }
    return render(request, 'editar_produto.html', context)

@usuario_required
def excluir_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    # Verifica se o produto pertence à empresa do usuário
    if produto.empresa != request.current_empresa:
        messages.error(request, 'Você não tem permissão para excluir este produto.')
        return redirect('lista_produtos')

    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso!')
        return redirect('lista_produtos')
    
    return render(request, 'confirmar_exclusao.html', {'produto': produto})

@admin_required
def lista_usuarios(request):
    usuarios = Usuario.objects.filter(empresa=request.current_empresa)
    
    # Encontra o admin principal para passar ao template
    primeiro_admin = Usuario.objects.filter(empresa=request.current_empresa, is_admin=True).order_by('id').first()

    context = {
        'usuarios': usuarios,
        'usuario': request.current_usuario,
        'primeiro_admin': primeiro_admin # Passa o objeto do admin principal
    }
    return render(request, 'lista_usuarios.html', context)

@admin_required
def adicionar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, user=request.current_usuario)
        if form.is_valid(): # A validação 'clean' será chamada aqui
            login = form.cleaned_data.get('login')
            email = form.cleaned_data.get('email')
            if Usuario.objects.filter(login=login).exists():
                messages.error(request, 'Este login já está em uso.')
            elif Usuario.objects.filter(email=email).exists():
                messages.error(request, 'Este email já está em uso.')
            else:
                novo_usuario = form.save(commit=False)
                novo_usuario.empresa = request.current_empresa
                
                senha = form.cleaned_data.get('senha')
                novo_usuario.senha = make_password(senha)
                
                novo_usuario.save()
                
                messages.success(request, f'Usuário "{novo_usuario.nome}" adicionado com sucesso!')
                return redirect('lista_usuarios')
    else:
        form = UsuarioForm(user=request.current_usuario)

    context = {
        'form': form
    }
    return render(request, 'adicionar_usuario.html', context)


@admin_required
def editar_usuario(request, pk):
    usuario_a_editar = get_object_or_404(Usuario, pk=pk, empresa=request.current_empresa)
    primeiro_admin = Usuario.objects.filter(empresa=request.current_empresa, is_admin=True).order_by('id').first()

    if usuario_a_editar == primeiro_admin:
        messages.error(request, 'Você não pode editar o perfil do administrador principal da empresa.')
        return redirect('lista_usuarios')
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario_a_editar, user=request.current_usuario)
        if form.is_valid():
            usuario_editado = form.save(commit=False)
            nova_senha = form.cleaned_data.get('senha')
            if nova_senha:
                usuario_editado.senha = make_password(nova_senha)
            else:
                usuario_editado.senha = usuario_a_editar.senha
            
            # Se o usuário não for o admin principal, o campo 'is_admin' não estará no form.
            # Desta forma, o valor de is_admin do usuário não será alterado, o que está correto.
            usuario_editado.save()
            messages.success(request, f'Usuário "{usuario_a_editar.nome}" atualizado com sucesso!')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario_a_editar, user=request.current_usuario)
        form.initial['senha'] = '' 

    context = {
        'form': form,
        'usuario_a_editar': usuario_a_editar
    }
    return render(request, 'editar_usuario.html', context)


@admin_required
def excluir_usuario(request, pk):
    usuario_a_excluir = get_object_or_404(Usuario, pk=pk, empresa=request.current_empresa)

    # --- NOVA VERIFICAÇÃO ---
    primeiro_admin = Usuario.objects.filter(empresa=request.current_empresa, is_admin=True).order_by('id').first()
    
    # Bloqueia a exclusão se o alvo for o primeiro admin
    if usuario_a_excluir == primeiro_admin:
        messages.error(request, 'O administrador principal da empresa не pode ser excluído.')
        return redirect('lista_usuarios')
    # -------------------------

    if usuario_a_excluir == request.current_usuario:
        messages.error(request, 'Você não pode excluir sua própria conta de administrador.')
        return redirect('lista_usuarios')

    if request.method == 'POST':
        nome_usuario = usuario_a_excluir.nome
        usuario_a_excluir.delete()
        messages.success(request, f'Usuário "{nome_usuario}" foi excluído com sucesso!')
        return redirect('lista_usuarios')

    context = {
        'usuario_a_excluir': usuario_a_excluir
    }
    return render(request, 'confirmar_exclusao_usuario.html', context)