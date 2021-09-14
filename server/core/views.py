import datetime
from django.views.generic import View
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.conf import settings
from .models import Usuario
from .form import UsuarioForm


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow(
    ) + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)


def UserPermission(request, nivel_min=5):
    try:
        usu = str(request.COOKIES['userID'])
        user = Usuario.objects.get(token=usu)
        if user.nivel.nivel > nivel_min:
            return False
        else:
            return True
    except:
        return False


def logado(alvo, request, context={}, titulo='', msg='ok', dados='', nivel_min=5):
    try:
        usu = str(request.COOKIES['userID'])
        user = Usuario.objects.get(token=usu)
        context['user'] = user
        context['titulo'] = titulo
        context['msg'] = msg
        context['dados'] = dados
        if user.nivel.nivel > nivel_min:
            context['titulo'] = 'erro'
            context['msg'] = 'Você não tem Autorização para acessar essa pagina. Faça login com um Usuário com mais Privilégios'
            return render(request, 'erro.html', context)
        else:
            return render(request, alvo, context)
    except Exception as e:
        print(str(e))
        redir = alvo.split('.')[0]
        redir = redir.split('/')[0]
        response = redirect('/login')
        set_cookie(response, 'redirect', redir)
        return response


class IndexView(View):
    def get(self, request):
        return logado('index.html', self.request, titulo='Home page')


class SobreView(View):
    def get(self, request):
        return logado('about.html', self.request, titulo='Sobre')


class UsuarioView(View):
    def get(self, request):
        return logado('usuario/view.html', request, titulo='Usuários', dados=Usuario.objects.all(), nivel_min=2)


class UsuarioAdd(View):
    def get(self, request):
        return logado('usuario/add.html', request, titulo='Cadastro de Usuario', dados=UsuarioForm(), nivel_min=1)

    def post(self, request):
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return logado('usuario/add.html', request,
                          titulo='Cadastro de Usuario',
                          dados=UsuarioForm(),
                          msg='gravado',
                          )
        else:
            return logado('usuario/add.html', request,
                          titulo='Cadastro de Usuario',
                          dados=UsuarioForm(),
                          msg='falha',
                          )


class UsuarioEdit(View):
    def get(self, request):
        chave = int(request.GET['id'])
        toke = request.COOKIES['userID']
        user = Usuario.objects.get(id=chave)
        userAtual = Usuario.objects.get(token=toke)
        nivel = 1
        if user.id == userAtual.id:
            nivel = 2
        form = UsuarioForm(instance=user)
        return logado('usuario/edit.html',
                      request, titulo='Editor de Usuario',
                      dados=form, nivel_min=nivel,
                      context={'id': chave}
                      )

    def post(self, request):
        index = request.POST['id']
        user = Usuario.objects.get(id=index) or None
        form = UsuarioForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return logado('usuario/edit.html', request,
                          titulo='Editor de Usuário',
                          dados=form,
                          msg='gravado',
                          )
        else:
            return logado('usuario/edit.html', request,
                          titulo='Editor de Usuário',
                          dados=form,
                          msg='falha',
                          )


class UsuarioDelete(View):
    context = {}

    def get(self, request):
        try:
            if UserPermission(request, nivel_min=1):
                chave = int(request.GET['id'])
                user = Usuario.objects.get(id=chave)
                user.delete()
                return HttpResponseRedirect('usuario')
            else:
                self.context['msg'] = 'Você não tem Autorização para acessar essa pagina'
                return render(request, 'erro.html', self.context)
        except:
            self.context['msg'] = 'Um erro inesperado ocorreu'
            return render(request, 'erro.html', self.context)


class LoginView(View):
    context = {
        'titulo': 'Login',
        'user': '',
        'msg': 'ok',
        'dados': '',
    }

    def get(self, request):
        self.context['msg'] = 'ok'
        return render(request, 'login.html', self.context)

    def post(self, request):
        try:
            us = request.POST['email']
            sh = request.POST['senha']
            try:
                alvo = request.COOKIES['redirect']
            except:
                alvo = '/'
            use = Usuario.objects.get(email=us, senha=sh)
            use.loggin()
            use.save()
            response = redirect('/'+alvo)
            set_cookie(response, 'userID', use.token)
            return response
        except:
            self.context['msg'] = 'falha'
            return render(request, 'login.html', self.context)


class Logout(View):
    context = {
        'titulo': 'Login',
        'user': '',
        'msg': 'ok',
        'dados': '',
    }

    def get(self, request):
        user = Usuario.objects.get(token=request.COOKIES['userID'])
        user.logout()
        user.save()
        self.context['msg'] = 'ok'
        return render(request, 'login.html', self.context)


class ErroView(View):
    def get(self, request):
        try:
            mensagem = request.GET['msg']
        except:
            mensagem = "Falha desconhecida"
        return render(request, 'erro.html', context={'msg': mensagem})


