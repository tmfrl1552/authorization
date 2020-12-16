from django.conf.urls import url
from django.urls import path, include


from . import views


from django.conf import settings
from django.conf.urls.static import static

app_name = 'myauth_home'

urlpatterns = [
    url(r'^$', views.UserLoginView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
]

