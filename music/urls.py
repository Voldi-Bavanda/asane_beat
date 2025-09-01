from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('beats/', views.beats_disponibles, name='beats_disponibles'),
    path('dons/', views.nous_soutenir, name='nous_soutenir'),
    path('stars/', views.nos_stars, name='nos_stars'),
    path('like-artist/<int:artist_id>/', views.like_artist, name='like_artist'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('beat/<int:beat_id>/', views.beat_detail, name='beat_detail'),
     path('contact/', views.contact_view, name='contact'),
]