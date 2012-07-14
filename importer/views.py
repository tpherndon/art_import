from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from importer.models import Artist, Artwork, ImportRun
from importer.forms import ArtworkForm, UploadForm
from importer.parser import parse_uploaded_file

def importer(request):
    """
    Upload a CSV of artworks by artist, parse the CSV and create
    :model:`importer.models.Artist` and :model:`importer.models.Artwork` items
    from each record.

    **Context**

    ``RequestContext``

    ``form``
        An instance of 'importer.forms.UploadForm'.

    **Template:**

    :template:`importer/importer.html`
    """
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # create an ImportRun from the imported file's name
            run_name = request.FILES['importer'].name
            importrun = ImportRun(name=run_name)
            importrun.save()
            parse_uploaded_file(request.FILES['importer'], importrun)
            return redirect('import-detail', pk=importrun.pk)
    else:
        form = UploadForm()
    return render(request, 'importer/importer.html', {'form': form })

def import_detail(request, pk):
    """
    Returns both a list of :model:`importer.models.Artist` objects and the
    requested :model:`importer.models.ImportRun` object.

    **Context**

    ``RequestContext``

    ``importrun``
        An instance of :model:`importer.models.Artist`.

    **Template:**

    :template:`importer/import_detail.html`
    """
    importrun = get_object_or_404(ImportRun, pk=pk)
    artists = Artist.objects.all()
    return render(request, 'importer/import_detail.html', {'importrun': importrun,
        'artists': artists})


@require_POST
def artwork_edit(request, pk):
    """
    Allows editing of an instance of :model:`importer.models.Artwork`.

    **Context**

    ``RequestContext``

    **Template:**

    None. This view is meant for use as an AJAX call
    """
    artwork = get_object_or_404(Artwork, pk=pk)
    if request.method == 'POST':
        form = ArtworkForm(request.POST, instance=artwork)
        if form.is_valid():
            form.save()
            return redirect('import-detail', pk=artwork.import_run.pk)
        else:
            return HttpResponse("ERROR", status=500)

