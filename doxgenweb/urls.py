from django.contrib import admin
from django.urls import path, include
from upload import views as upload_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', upload_views.home, name='home'),
    path('upload/', upload_views.upload_cpp_project, name='upload'),
    path('docs/<str:folder>/', upload_views.serve_docs, name='serve_docs'),
    path('dashboard/', upload_views.user_dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='upload/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('users/', include('users.urls')),
    path('github/', upload_views.import_from_github, name='github_import'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
