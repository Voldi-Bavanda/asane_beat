from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from music.models import Beat, Artist, Song  # Notez 'music' au lieu de 'asane'

def index(request):
    featured_beats = Beat.objects.filter(is_available=True, featured=True).order_by('-upload_date')[:4]
    featured_artists = Artist.objects.filter(featured=True).order_by('-likes')[:4]
    
    return render(request, 'index.html', {
        'featured_beats': featured_beats,
        'featured_artists': featured_artists
    })

def beats_disponibles(request):
    search_query = request.GET.get('search', '')
    sort = request.GET.get('sort', '-upload_date')
    
    beats = Beat.objects.filter(is_available=True)
    
    if search_query:
        beats = beats.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    beats = beats.order_by(sort)
    
    # Pagination - 9 beats par page
    page = request.GET.get('page', 1)
    paginator = Paginator(beats, 9)
    
    try:
        beats = paginator.page(page)
    except PageNotAnInteger:
        beats = paginator.page(1)
    except EmptyPage:
        beats = paginator.page(paginator.num_pages)
    
    return render(request, 'beats_disponibles.html', {
        'beats': beats,
        'search_query': search_query,
        'sort': sort
    })

def nos_stars(request):
    search_query = request.GET.get('search', '')
    
    artists = Artist.objects.all()
    
    if search_query:
        artists = artists.filter(
            Q(name__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    artists = artists.order_by('-likes')
    featured_artists = Artist.objects.filter(featured=True).order_by('-likes')[:3]
    
    # Pagination - 12 artistes par page
    page = request.GET.get('page', 1)
    paginator = Paginator(artists, 12)
    
    try:
        artists = paginator.page(page)
    except PageNotAnInteger:
        artists = paginator.page(1)
    except EmptyPage:
        artists = paginator.page(paginator.num_pages)
    
    return render(request, 'nos_stars.html', {
        'artists': artists,
        'featured_artists': featured_artists,
        'search_query': search_query
    })

# @login_required  ← Supprimer cette ligne
def like_artist(request, artist_id):
    if request.method == 'POST':
        artist = get_object_or_404(Artist, id=artist_id)

        if request.user.is_authenticated:
            # Utilisateur connecté : logique normale
            if request.user in artist.users_who_liked.all():
                messages.warning(request, "Vous avez déjà liké cet artiste!")
            else:
                artist.likes += 1
                artist.users_who_liked.add(request.user)
                artist.save()
                messages.success(request, f"Vous avez liké {artist.name}!")
        else:
            # Utilisateur anonyme : utiliser la session
            session_key = f"liked_artist_{artist_id}"
            if request.session.get(session_key, False):
                messages.warning(request, "Vous avez déjà liké cet artiste!")
            else:
                artist.likes += 1
                artist.save()
                request.session[session_key] = True
                messages.success(request, f"Vous avez liké {artist.name}!")

    return redirect('nos_stars')


@login_required
def acheter_beat(request, beat_id):
    beat = get_object_or_404(Beat, id=beat_id)
    
    if not beat.is_available:
        messages.error(request, "Ce beat n'est plus disponible!")
        return redirect('beats_disponibles')
    
    if request.user in beat.users_who_bought.all():
        messages.warning(request, "Vous avez déjà acheté ce beat!")
    else:
        # Logique de paiement à implémenter ici
        beat.users_who_bought.add(request.user)
        messages.success(request, f"Vous avez acheté le beat {beat.title}!")
    
    return redirect('beats_disponibles')

def nous_soutenir(request):
    return render(request, 'nous_soutenir.html')

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    songs = artist.songs.all().order_by('-release_date')
    
    # Vérifie si l'utilisateur a déjà liké cet artiste
    user_has_liked = request.user.is_authenticated and artist.users_who_liked.filter(id=request.user.id).exists()
    
    return render(request, 'artist_detail.html', {
        'artist': artist,
        'songs': songs,
        'user_has_liked': user_has_liked
    })

def beat_detail(request, beat_id):
    beat = get_object_or_404(Beat, id=beat_id)
    similar_beats = Beat.objects.filter(
        is_available=True,
        author=beat.author
    ).exclude(
        id=beat_id
    ).order_by('-upload_date')[:4]
    
    # Vérifie si l'utilisateur a déjà acheté ce beat
    user_has_bought = request.user.is_authenticated and beat.users_who_bought.filter(id=request.user.id).exists()
    
    return render(request, 'music/beat_detail.html', {
        'beat': beat,
        'similar_beats': similar_beats,
        'user_has_bought': user_has_bought
    })


def toggle_like_artist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    
    if request.user in artist.users_who_liked.all():
        artist.users_who_liked.remove(request.user)
        artist.likes -= 1
        artist.save()
        messages.success(request, f"Vous avez retiré votre like de {artist.name}!")
    else:
        artist.users_who_liked.add(request.user)
        artist.likes += 1
        artist.save()
        messages.success(request, f"Vous avez liké {artist.name}!")
    
    return redirect('artist_detail', artist_id=artist_id)



def contact_view(request):
    return render(request, 'contact.html')
