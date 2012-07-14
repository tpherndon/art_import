from django import forms

from importer.models import Artwork

class UploadForm(forms.Form):
    """
    Allows the user to upload a CSV file of artworks.
    """
    importer = forms.FileField()


class ArtworkForm(forms.ModelForm):
    """
    Allows the user to edit a :model:`importer.models.Artwork` instance.
    """
    class Meta:
        model = Artwork
