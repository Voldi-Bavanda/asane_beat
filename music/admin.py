from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Beat, Artist, Song

class BeatAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'is_available', 'upload_date', 'audio_preview', 'purchase_count')
    list_filter = ('is_available', 'upload_date')
    search_fields = ('title', 'author')
    readonly_fields = ('purchase_count', 'audio_preview', 'upload_date')
    actions = ['delete_selected_beats']
    list_per_page = 20

    fieldsets = (
        ('Information', {
            'fields': ('title', 'author', 'price', 'is_available', 'upload_date')
        }),
        ('Fichier Audio', {
            'fields': ('audio_file', 'audio_preview'),
        }),
        ('Statistiques', {
            'fields': ('purchase_count', 'users_who_bought'),
            'classes': ('collapse',)
        }),
    )

    def audio_preview(self, obj):
        if obj.audio_file:
            return format_html(
                '<audio controls style="height:30px"><source src="{}"></audio>',
                obj.audio_file.url
            )
        return "-"
    audio_preview.short_description = "Preview"

    def purchase_count(self, obj):
        return obj.users_who_bought.count()
    purchase_count.short_description = "Achats"

    def delete_selected_beats(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} beats supprimés avec succès", messages.SUCCESS)
    delete_selected_beats.short_description = "Supprimer les beats sélectionnés"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('users_who_bought')

class SongInline(admin.TabularInline):
    model = Song
    extra = 1
    readonly_fields = ('audio_preview',)
    fields = ('title', 'audio_file', 'audio_preview', 'release_date')
    show_change_link = True

    def audio_preview(self, obj):  # Correction: audio_preview (pas audio_preview)
        if obj.audio_file:
            return format_html(
                '<audio controls style="height:30px"><source src="{}"></audio>',
                obj.audio_file.url
            )
        return "-"
    audio_preview.short_description = "Preview"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist')

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile_picture_display', 'likes_count', 'featured', 'social_media_link', 'song_count')
    list_filter = ('featured',)
    search_fields = ('name', 'bio')
    inlines = [SongInline]
    actions = ['delete_selected_artists', 'make_featured', 'remove_featured']
    list_per_page = 20
    filter_horizontal = ('users_who_liked',)
    readonly_fields = ('profile_picture_display', 'likes_count', 'song_count')

    fieldsets = (
        ('Information', {
            'fields': ('name', 'bio', 'featured')
        }),
        ('Médias', {
            'fields': ('profile_picture', 'profile_picture_display', 'social_media_link')
        }),
        ('Likes', {
            'fields': ('users_who_liked',),
            'classes': ('collapse',)
        }),
    )

    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-height:100px;max-width:100px" />',
                obj.profile_picture.url
            )
        return "-"
    profile_picture_display.short_description = "Photo actuelle"

    def likes_count(self, obj):
        return obj.users_who_liked.count()
    likes_count.short_description = "Likes"

    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = "Chansons"

    def delete_selected_artists(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} artistes supprimés avec succès", messages.SUCCESS)
    delete_selected_artists.short_description = "Supprimer les artistes sélectionnés"

    def make_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f"{updated} artistes mis en vedette", messages.SUCCESS)
    make_featured.short_description = "Mettre en vedette"

    def remove_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f"{updated} artistes retirés de la vedette", messages.SUCCESS)
    remove_featured.short_description = "Retirer de la vedette"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('users_who_liked', 'songs')
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_link', 'release_date', 'audio_preview')
    search_fields = ('title', 'artist__name')
    list_filter = ('artist', 'release_date')
    actions = ['delete_selected_songs']
    list_per_page = 20
    list_select_related = ('artist',)
    date_hierarchy = 'release_date'
    readonly_fields = ('audio_preview',)

    def artist_link(self, obj):
        if obj.artist:
            url = reverse(f'admin:{obj.artist._meta.app_label}_{obj.artist._meta.model_name}_change', 
                        args=[obj.artist.id])
            return format_html('<a href="{}">{}</a>', url, obj.artist.name)
        return "-"
    artist_link.short_description = "Artiste"
    artist_link.admin_order_field = 'artist__name'

    def audio_preview(self, obj):
        if obj.audio_file:
            return format_html(
                '<audio controls style="height:30px"><source src="{}"></audio>',
                obj.audio_file.url
            )
        return "-"
    audio_preview.short_description = "Preview"

    def delete_selected_songs(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} chansons supprimées avec succès", messages.SUCCESS)
    delete_selected_songs.short_description = "Supprimer les chansons sélectionnées"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist')

admin.site.register(Beat, BeatAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)