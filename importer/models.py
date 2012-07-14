from StringIO import StringIO

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from imagekit.models import ImageSpec
from imagekit.processors import resize, Adjust
from PIL import Image
import requests


class ImportRun(models.Model):
    """
    Stores the metadata for a given import run, collecting all artworks added
    during the import. Related to :model:`importer.models.Artwork`.
    """
    import_date = models.DateTimeField(auto_now_add=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return u'Import Run %s on %s' % (self.pk, self.import_date)

class Artist(models.Model):
    """
    Stores a single artist, related to :model:`importer.models.Artwork`.
    """
    first_name = models.CharField(max_length=255, db_index=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    last_name = models.CharField(max_length=255, db_index=True)

    def _get_full_name(self):
        """Returns the artist's full name."""
        if self.middle_name:
            return u'%s %s %s' % (self.first_name, self.middle_name,
                self.last_name)
        else:
            return u'%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def __unicode__(self):
        return self.full_name

class Artwork(models.Model):
    """
    Stores the metadata for a single work of art, including a thumbnail
    if available. Related to :model:`importer.models.Artist` and
    :model:`importer.models.ImportRun`.
    """
    title = models.CharField(max_length=255, db_index=True)
    create_start = models.DateField("year started")
    create_finish = models.DateField("year finished")
    medium = models.CharField(max_length=255, db_index=True)
    raw_size = models.CharField(max_length=255, null=True, blank=True)
    depth = models.DecimalField(null=True, blank=True, help_text="in centimeters", max_digits=10, decimal_places=2)
    height = models.DecimalField(null=True, blank=True, db_index=True, help_text="in centimeters", max_digits=10, decimal_places=2)
    width = models.DecimalField(null=True, blank=True, db_index=True, help_text="in centimeters", max_digits=10, decimal_places=2)
    image_url = models.URLField(null=True, blank=True)
    original_image = models.ImageField(null=True, blank=True, upload_to='uploads')
    thumbnail = ImageSpec([Adjust(contrast=1.2, sharpness=1.1),
        resize.Fit(50, 50)], image_field='original_image',
        format='PNG', options={'quality': 90}, pre_cache=True)
    midsize = ImageSpec([resize.Fit(200, 200)], image_field='original_image',
        format='PNG', options={'quality': 90}, pre_cache=True)
    modalsize = ImageSpec([resize.Fit(500, 350)], image_field='original_image',
        format='PNG', options={'quality': 90}, pre_cache=True)

    artist = models.ForeignKey(Artist)
    import_run = models.ForeignKey(ImportRun)

    def __unicode__(self):
        return '%s by %s' % (self.title, self.artist)

    def save(self, *args, **kwargs):
        # If the artwork does not yet have an image, but does have URL for
        # the image, download the image for local use
        super(Artwork, self).save(*args, **kwargs)
        if self.image_url and not self.original_image:
            file_ext = self.image_url.split("/")[-1].split(".")[-1]
            # If the URL points to something that *isn't* an image, skip it
            if file_ext.lower() in ('jpg', 'png', 'gif', 'tif'):
                r = requests.get(self.image_url, config={'safe_mode': True})
                # If the request fails, there's no image, so don't bother
                # trying to save the image
                if r.status_code == 200:
                    # Read in the content of the image
                    img_str = StringIO(r.content)
                    # Pull the filename out of the URL
                    filename = r.url.split("/")[-1]
                    # Create a temporary file to save the image
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(img_str.read())
                    img_temp.flush()
                    # Save the temp file to the model as the original image
                    self.original_image.save(filename, File(img_temp))
