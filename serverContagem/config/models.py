from django.db import models
from stdimage import StdImageField
from core.models import Base

class Camera(Base):
    nome = models.CharField('nome',max_length=50)
    porta_img = models.IntegerField('Porta de Imagem', default=32200)
    porta_dados = models.IntegerField('Porta de Dados', default=32100)
    ip = models.CharField('ip',max_length=15,unique=True)
    status = models.CharField('status',max_length=15)
    aprovado = models.IntegerField('Aprovações',default=0)
    reprovado = models.IntegerField('Reprovações',default=0)
    garrafas = models.IntegerField('Total de Garrafas',default=0)
    faltantes = models.IntegerField('Garrafas Faltantes',default=0)
    img = models.CharField('Ultima Imagem',max_length=200,default='')
    lastValue = models.IntegerField('última contagem',default=0)

    class Meta:
        verbose_name = 'Câmera'
        verbose_name_plural = 'Câmeras'

    def __str__(self):
        return self.nome

class Imagem(Base):
    camera=models.ForeignKey(Camera,on_delete=models.CASCADE)
    data = models.DateTimeField('Hora')
    img = models.CharField('Ultima Imagem',max_length=200)
    garrafas = models.IntegerField('Garrafas Presentes',default=0)

    class Meta:
        verbose_name = 'Imagem'
        verbose_name_plural = 'Imagens'

    def __str__(self):
        return f'{self.camera.nome}-{self.pk}'
