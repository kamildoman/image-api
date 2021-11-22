
from django.urls import path
from .views import *





urlpatterns = [
    path('', ImageViewSet.as_view(), name='upload'),
    path('login/', login_user, name="login"),
    path('logout/', user_logout, name="logout"),
    path('fetch/', fetch_link, name = "fetch"),
    path('temp/<str:path>', temporary_image, name="temporary_image"),
    path('media/<str:path>', media_access, name="media_access"),
] 