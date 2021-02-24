from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('author/', views.about_author_page.as_view(), name='author'),
    path('tech/', views.about_tech_page.as_view(), name='tech')
]
