from APIBackendService.settings.common import *

# Production env settings. Must not be used in production.
# Connects to the production database.

DEBUG = False
# SESSION_COOKIE_SECURE = True
CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ['*']
