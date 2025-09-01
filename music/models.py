from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os

class Beat(models.Model):
    title = models.CharField(max_length=100, verbose_name="Titre")
    author = models.CharField(max_length=100, verbose_name="Auteur")
    audio_file = models.FileField(
        upload_to='beats/',
        verbose_name="Fichier audio",
        help_text="Format MP3 recommandé"
    )
    featured = models.BooleanField(default=False, verbose_name="En vedette")
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name="Prix"
    )
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    users_who_bought = models.ManyToManyField(
        User,
        blank=True,
        related_name='purchased_beats',
        verbose_name="Acheté par"
    )

    class Meta:
        ordering = ['-upload_date']
        verbose_name = "Beat"
        verbose_name_plural = "Beats"

    def __str__(self):
        return f"{self.title} by {self.author}"

    def delete(self, *args, **kwargs):
        """Supprime le fichier audio lors de la suppression du beat"""
        if self.audio_file:
            if os.path.isfile(self.audio_file.path):
                os.remove(self.audio_file.path)
        super().delete(*args, **kwargs)


class Artist(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    bio = models.TextField(verbose_name="Biographie")
    profile_picture = models.ImageField(
        upload_to='artists/',
        verbose_name="Photo de profil",
        help_text="Format carré recommandé"
    )
    social_media_link = models.URLField(blank=True, verbose_name="Lien réseaux sociaux")
    likes = models.PositiveIntegerField(default=0, verbose_name="Likes")
    featured = models.BooleanField(default=False, verbose_name="En vedette")
    users_who_liked = models.ManyToManyField(
        User,
        blank=True,
        related_name='liked_artists',
        verbose_name="Utilisateurs ayant liké"
    )

    class Meta:
        ordering = ['-likes']
        verbose_name = "Artiste"
        verbose_name_plural = "Artistes"

    def __str__(self):
        return self.name

    def like_by_user(self, user):
        """Permet à un utilisateur de liker une seule fois"""
        if not self.users_who_liked.filter(id=user.id).exists():
            self.likes += 1
            self.users_who_liked.add(user)
            self.save()
            return True
        return False

    def delete(self, *args, **kwargs):
        """Supprime l'image de profil lors de la suppression de l'artiste"""
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)


class Song(models.Model):
    title = models.CharField(max_length=100, verbose_name="Titre")
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='songs',
        verbose_name="Artiste"
    )
    audio_file = models.FileField(
        upload_to='songs/',
        verbose_name="Fichier audio",
        help_text="Format MP3 recommandé"
    )
    release_date = models.DateField(verbose_name="Date de sortie")

    class Meta:
        ordering = ['-release_date']
        verbose_name = "Chanson"
        verbose_name_plural = "Chansons"

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    def delete(self, *args, **kwargs):
        """Supprime le fichier audio lors de la suppression de la chanson"""
        if self.audio_file:
            if os.path.isfile(self.audio_file.path):
                os.remove(self.audio_file.path)
        super().delete(*args, **kwargs)


# Signaux pour la suppression propre des fichiers
@receiver(pre_delete, sender=Beat)
def beat_pre_delete(sender, instance, **kwargs):
    """Garantit la suppression du fichier audio quand un beat est supprimé"""
    if instance.audio_file:
        if os.path.isfile(instance.audio_file.path):
            os.remove(instance.audio_file.path)

@receiver(pre_delete, sender=Artist)
def artist_pre_delete(sender, instance, **kwargs):
    """Supprime automatiquement toutes les chansons de l'artiste"""
    for song in instance.songs.all():
        song.delete()

@receiver(pre_delete, sender=Song)
def song_pre_delete(sender, instance, **kwargs):
    """Garantit la suppression du fichier audio quand une chanson est supprimée"""
    if instance.audio_file:
        if os.path.isfile(instance.audio_file.path):
            os.remove(instance.audio_file.path)