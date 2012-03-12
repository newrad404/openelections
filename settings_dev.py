from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_openelections',
        'USER': 'root',
        'PASSWORD': 'hello1'
    }
}

MEDIA_ROOT = '/Users/trusheim/Desktop/openelections/public/media'
BALLOT_ROOT = '/Users/trusheim/Desktop/openelections/ballots'
LOG_ROOT = '/Users/trusheim/Desktop/openelections/logs'
STUDENT_CSV = '/Users/stephen/Desktop/openelections/students.csv'



WEBAUTH_SHARED_SECRET = 'test'
WEBAUTH_URL = 'https://www.stanford.edu/~trusheim/cgi-bin/wa-authenticate-test.php'

MEDIA_URL = 'http://localhost:8000/media/' #'http://corn24.stanford.edu:32145/'
