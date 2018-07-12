ARTIFACT IMPORTER v1.0
======================

Archived as of 2018-07-12
=========================

TEST PROJECT REQUIREMENTS: A simple Excel/CSV importer
Abstract a data model from the attached excel file. Express it as a data store schema and/or API.
Describe data cleanup needed and how you would approach it, and prototype some of the following (your choice which):
Year & Size - clean them up for range searching
Title - Untitled is a special title term; Series is an ordered collection of artworks
Medium - do we want searches on "oil" to return "oil on canvas"? (I would leave this alone for now)
Artist - we'll want artist names to be matched against our DB of artists, so it should be set up for that
Missing values - flag them for follow-up cleansing
Simple UI to upload the file and display a table of processed results.
You can write the above on your own from scratch or pull from available django/python tools

I wrote the app using Python 2.6, and it should work unmodified on 2.7. I've
included a requirements.txt for use with pip and virtualenv. Create a new 
virtualenv and install the requirements via:

```
pip install -r requirements.txt
```

The app uses sqlite3 by default, as that obviates the need for installing
Postgres or MySQL, but should work with either. If you choose to run it
against a different database, you will need to edit settings.py and set
your database appropriately. You will also need to install the necessary
database adaptor.

Once the requirements are installed, cd into the project directory and run:

```
python manage.py syncdb
```

to install the database tables, followed by:

```
python manage.py runserver
```

You may also run the test suite, via:

```
python manage.py test importer
```

Note that the test suite covers the various parsers, and also note that one
test is known to fail. I came up with some nicely ambiguous size measurements
to throw at the parser, and have not yet worked up the necessary solution. That
solution involves more regexes, rather than the simplistic "in" approach my
naive implementation uses.

USAGE
=====
The app itself is basically an importer for galleries' artworks CSVs. It
includes a form for uploading a CSV, and has been tested with the
sample_art.csv. That file is separate from the package, for
confidentiality.

The home page of the app is the upload form. As per the note on the page, the
import process takes a few minutes to complete, in part because it imports not
just the artwork metadata, but also the image associated with the artwork.
If one comments out the image import portion, the import runs nearly instantly.
In production, one would delegate the image import jobs to e.g. Celery.

Once the import completes, you will be redirected to a summary page for the
upload. That summary page lists all the artworks that were imported, and
displays a warning for fields that were not supplied in the CSV. Each row of
the table has a button to open an editing form for the artwork. 

I designed the parsing process to convert whatever size measurements could be
found into centimeters. Normalizing the size measurements to a single unit of
measurement will make search easier in the backend. If we normalize users' input
in the UI and convert it to cm, we can then search across all artworks without
worrying about converting multiple times within the backend. However, I have
NOT implemented search, or the necessary functionality to convert arbitrary user
input from inches or feet to centimeters. Thus, the cleanup forms request the
user convert the measurements as needed.

The app allows the user to select from whatever import runs have been previously
loaded and go to their respective cleanup page. I envision a workflow where
users will upload a file and come back to it later for cleanup. I simplified
the app by building the parsing process into the upload view, but in the real
world, this approach is not as friendly as it should be. Since parsing takes a
bit of time, the webserver would be tied up with the job, and the user would
need to allow the entire parse job to run. If the user gets bored and clicks
away in the middle, the upload would fail. In a real-world scenario, the upload
process would run in the browser, but the parse process would be off-loaded to
an asynchronous worker system. In the Python & Django ecosphere, the common
choice for such a system is Celery, which I've previously found to be easy to
set up and get working. In this scenario, the parsing would be run by a Celery
worker, and when the task is complete a notification would be sent to the user.
The user would then log back in to the system and perform whatever cleanup is
necessary.

I additionally implemented two more views that allow the user to explore the
artworks, either by artist or from a global list of works.

IMPLEMENTATION NOTES
====================
I used Twitter Bootstrap 2.0 as the basis for the UI. It has the virtues of
allowing me to build a very usable UI very quickly indeed. However, its style
is rapidly becoming well-known, and should not be used unmodified for a
polished application.

I have not handled any subtleties regarding artwork title or medium, or
an external database of artist information. I have abstracted the artist
creation step in parsing, so that any validation against an external DB can be
added to that step.  Similar abstraction can be added for title and medium as
needed.

For search, I would recommend adding Haystack to the app. In production, I 
would want to use Solr as the search backend, and use Celery to update the
indexes as changes are made in the database. Specialty searching, the kind
that Solr cannot handle easily, can still be done in the database itself.

If you have any questions or comments, or run into issues with the app, do feel
free to contact me.
