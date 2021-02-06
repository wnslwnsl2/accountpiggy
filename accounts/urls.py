from . import views
from django.urls import path
from django.contrib.auth.views import LoginView,LogoutView

app_name='accounts'
urlpatterns=[
    path('login/',views.login_page,name='login'),
    path('register/',views.register_page, name='register'),
    path('logout/',views.logout_page,name='logout')
]