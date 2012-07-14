from importer.models import ImportRun

def import_list(request):
    """Adds a list of all :model:`importer.models.ImportRun` objects to the
    context."""
    import_list = ImportRun.objects.all()
    return {'import_list': import_list}
