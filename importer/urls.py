from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView

from importer.models import Artist, Artwork
from importer.views import importer, import_detail, artwork_edit

urlpatterns = patterns('',
    url(r'^artists/$', ListView.as_view(model=Artist,), name='artist-list'),
    url(r'^artists/(?P<pk>\d+)/$', DetailView.as_view(model=Artist,), name='artist-detail'),
    url(r'^artworks/$', ListView.as_view(model=Artwork,), name='artworks-list'),
    url(r'^editart/(?P<pk>\d+)/$', artwork_edit, name='artwork-edit'),
    url(r'^importrun/(?P<pk>\d+)/$', import_detail, name='import-detail'),
    url(r'^$', importer, name='importer'),

)
