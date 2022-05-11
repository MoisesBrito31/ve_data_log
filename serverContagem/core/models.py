from django.db import models
from random import randint as randon
from stdimage import StdImageField

CHAVE = (
    'G','0','4','f','H','I','a','6','3','o','h','f','M','k','n','P','Q','R','S','T',
    'e','W','z','Y','Z','a','c','c','d','e','f','g','s','P','j','k','l','z','n','o',
    'p','q','V','s','t','u','3','x','5','z','0','1','2','3','4','5','6','7','8','9',
    'y','e','r','s','3','4','w','n','0','z','0','h','T','3','4','i','1','j','x','B',
    'p','q','r','s','t','u','w','x','y','z','0','1','2','3','4','5','6','7','8','9',
)

class Token():
    token = 'abcdefghij'
    __base =(
        'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','W','X','Y','Z',
        'a','c','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','w','x','y','z',
        '0','1','2','3','4','5','6','7','8','9',
    )

    def __init__(self, qtd=100):
        self.GeraToken(qtd)

    def GeraToken(self, qtd):
        ret = str('')
        for x in range(qtd):
            ret = str.format('{}{}', ret, self.__base[randon(0,59)])
        self.token = ret


class Base(models.Model):
    criado = models.DateTimeField('Criado',auto_now_add=True)
    modificado = models.DateTimeField('Modificado', auto_now=True)
    ativo = models.BooleanField('Ativo?',default=True)
    class Meta:
        abstract = True


class Cargo(Base):
    cargo = models.CharField('Cargo', max_length=100)
    nivel = models.IntegerField('Nivel de Acesso')

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
    
    def __str__(self):
        return self.cargo


class Usuario(Base):
    nome = models.CharField('nome', max_length=100)
    email = models.EmailField('E-Mail', max_length=100, unique=True)
    nivel = models.ForeignKey('core.Cargo', verbose_name='Cargo', on_delete=models.CASCADE)
    senha = models.CharField('Senha', max_length=10, )
    token = models.CharField('token', max_length=255, default='', blank=True)
    img = StdImageField(
                            'Imagem', upload_to='usuarios', 
                            variations={'thumb':{'width' : 100,'height':100}},
                            blank=True
                        )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome

    def loggin(self):
        tk = Token().token
        self.token = tk

    def logout(self):
        tk = Token().token
        self.token = tk

    




