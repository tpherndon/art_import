from django.contrib import admin
from imagekit.admin import AdminThumbnail

from collectrium_exercise.importer.models import Artist, Artwork


class ArtistAdmin(admin.ModelAdmin):
    ordering = ('last_name', 'first_name')


class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'admin_thumbnail')
    list_filter = ('artist',)
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    ordering = ('artist', 'title')
    search_fields = ('artist__first_name', 'artist__last_name', 'title', 'medium')
    fieldsets = (
        (None, {
        'fields': (
            'title', ('create_start', 'create_finish'), 'medium', 'raw_size',
            ('depth', 'height', 'width'), 'image_url', 'artist', 'import_run',
            'original_image',
            )
        }
        ),
    )


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Artwork, ArtworkAdmin)
