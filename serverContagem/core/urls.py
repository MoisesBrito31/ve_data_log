from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import IndexView, LoginView, Logout, ErroView, SobreView
from .views import UsuarioView, UsuarioAdd, UsuarioDelete, UsuarioEdit


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('erro', ErroView.as_view(), name='erro'),
    path('index', IndexView.as_view(), name='index'),
    path('config', IndexView.as_view(), name='index'),
    path('sobre', SobreView.as_view(), name='sobre'),
    path('about', SobreView.as_view(), name='about'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),
    path('usuario', UsuarioView.as_view(), name='usuario'),
    path('usuario_add', UsuarioAdd.as_view(), name='usuario_add'),
    path('usuario_edit', UsuarioEdit.as_view(), name='usuario_edit'),
    path('usuario_delete', UsuarioDelete.as_view(), name='usuario_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
