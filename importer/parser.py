import csv
import datetime
from decimal import *
import os
import re

from django.conf import settings

from importer.models import Artist, Artwork


def create_artist(name):
    """
    Gets or creates an instance of :model:`importer.models.Artist` from a
    string of the artist's name.
    """
    artist_name = name.split()
    if len(artist_name) > 2:
        artist, created = Artist.objects.get_or_create(first_name=artist_name[0],
                                last_name=artist_name[-1],
                                middle_name=' '.join(artist_name[1:-1]))
    else:
        artist, created = Artist.objects.get_or_create(first_name=artist_name[0],
                                last_name=artist_name[1])
    return artist, created

def conversion_factor(size):
    """
    Determines the multiplier for normalizing the size measurements.
    """
    # look for cm, in., ft., meters
    conversion_factor = Decimal('1.0')
    if 'in.' in size:
        conversion_factor = Decimal('2.54')
    elif 'ft.' in size:
        conversion_factor = Decimal('12.0') * Decimal('2.54')
    elif 'meter' in size:
        conversion_factor = Decimal('1000.0')
    return conversion_factor



def parse_size(size):
    """
    Normalizes a size measurement into centimeters. Returns a tuple of depth,
    height, width.
    """
    converter = conversion_factor(size)
    depth = height = width = Decimal('0.0')

    # basic existence check
    if not size:
        return depth, height, width

    # look for num x num x num pattern
    # ex: '8.25 x 16.25 x 1 in.'
    d_h_w = re.compile("(?P<depth>\d+.?\d*) x (?P<height>\d+\.?\d*) x (?P<width>\d+\.?\d*)")
    r = d_h_w.search(size)
    if r:
        depth = Decimal(r.group('depth')) * converter
        height = Decimal(r.group('height')) * converter
        width = Decimal(r.group('width')) * converter
        return depth, height, width

    # look for num x num pattern
    # ex: '21.3 x 45 in.'
    h_w = re.compile("(?P<height>\d+\.?\d*) x (?P<width>\d+\.?\d*)")
    if 'and' in size:
        # there are two h/w pairs, return the larger
        # ex: '21.3 x 45 and 32 x 56 in. ea.'
        r = h_w.findall(size)
        r.sort(reverse=True)
        height = Decimal(r[0][0]) * converter
        width = Decimal(r[0][1]) * converter
        return depth, height, width

    # look for num x num pattern
    # ex: '21.3 x 45 in.'
    # single h/w pair only
    r = h_w.search(size)
    if r:
        height = Decimal(r.group('height')) * converter
        width = Decimal(r.group('width')) * converter
        return depth, height, width

    # look for num-num pattern
    # ex: '6-8 ft. tall'
    h = re.compile("(?P<shorter>\d+\.?\d*)-(?P<taller>\d+\.?\d*)")
    r = h.search(size)
    if r:
        height = Decimal(r.group('taller')) * converter
        return depth, height, width

    # look for any single number
    # ex: '8 ft. tall'
    h = re.compile("(?P<height>\d+\.?\d*)")
    r = h.search(size)
    if r:
        height = Decimal(r.group('height')) * converter
        return depth, height, width


def parse_year(year):
    """
    Normalizes the year or years a work of art was created. Returns a tuple of
    year started, year finished.
    """
    if not year or year.startswith('nd'):
        return 1, 1

    if year.startswith('c.'):
        year = year[2:]

    try:
        year = int(year)
        return year, year
    except ValueError:
        # year currently looks like "1995-96"
        start, end = year.split("-")
        start = start.strip()
        end = end.strip()
        if len(start) != 4:
            return 0, 0
        else:
            if len(end) != 4:
                end = ''.join((start[:2], end))
            return int(start), int(end)


def parse_uploaded_file(upload, importrun):
    """
    Receives an uploaded CSV of artworks and parses the CSV file into
    :model:`importer.models.Artist` instances, :model:`importer.models.Artwork`
    instances, and creates a new :model:`importer.models.ImportRun` instance
    to track the import process itself, and allow users to clean up the results
    of a given import.
    """
    # Save the file to the upload directory, using chunks rather than
    # all-in-memory to avoid memory exhaustion from large files
    destination = open(os.path.join(settings.MEDIA_ROOT, upload.name), 'wb+')
    for chunk in upload.chunks():
        destination.write(chunk)
    destination.close()
    with open(os.path.join(settings.MEDIA_ROOT, upload.name), 'Urb') as f:
        # Using DictReader allows the parser to address columns by name, a
        # strategy which works well as long as the CSV column names are
        # known in advance. If user-supplied column names, or no names at all,
        # will be used, then a means of mapping columns to database fields
        # would need to be used instead.
        reader = csv.DictReader(f)
        for row in reader:
            artist, artist_created = create_artist(row['artist name'])
            depth, height, width = parse_size(row['size'])
            year_started, year_finished = parse_year(row['year'])
            year_started = datetime.date(year_started, 1, 1)
            year_finished = datetime.date(year_finished, 1, 1)
            artwork, artwork_created = Artwork.objects.get_or_create(title=row['artwork title'],
                                                                     create_start=year_started,
                                                                     create_finish=year_finished,
                                                                     medium=row['medium'],
                                                                     raw_size=row['size'],
                                                                     depth=depth,
                                                                     height=height,
                                                                     width=width,
                                                                     image_url=row['largest_resolution image URL'],
                                                                     artist=artist,
                                                                     import_run=importrun)
