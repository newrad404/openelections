from django.conf import settings

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Daniel Holstein', 'holstein@stanford.edu'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = ''

BASE_URL = 'http://localhost:8000/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = BASE_URL + 'media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = BASE_URL + 'media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'qszo)3canz!+28v)6ha)6*8oe$2hpjibn0il$@2sk$tqp&5)lv'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'webauth.middleware.WebauthMiddleware',
)

ROOT_URLCONF = 'openelections.urls'

TEMPLATE_DIRS = (
    'templates/',
)

FIXTURE_DIRS = ('fixtures/',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'openelections.issues',
    'openelections.petitions',
    'webauth',
    'openelections.ballot',
    #'openelections.webauth',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

WEBAUTH_SHARED_SECRET = 'a2d24bf589b1dea3d83f317019e2ff83bf430b8d1c2a3f741dbf7d72f196d8cf6a6d113de356dc77'
WEBAUTH_URL = 'https://www.stanford.edu/~trusheim/cgi-bin/wa-authenticate-test.php'

STUDENT_CSV = '' # FILL ME!
