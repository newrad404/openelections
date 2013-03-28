from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'openelections',
        'USER': 'root',
        'PASSWORD': 'dh'
    }
}

ROOT = '/home/daniel/openelections_ballot/openelections/'
MEDIA_ROOT = ROOT + 'public/media'
BALLOT_ROOT = ROOT + 'public/ballots'
LOG_ROOT = ROOT + '/logs'
STUDENT_CSV = ROOT + 'students.csv'



WEBAUTH_SHARED_SECRET = 'test'
WEBAUTH_URL = 'https://www.stanford.edu/~trusheim/cgi-bin/wa-authenticate-test.php'

MEDIA_URL = 'http://localhost:8000/media/' #'http://corn24.stanford.edu:32145/'
