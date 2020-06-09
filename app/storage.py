#from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage

class ForgivingManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):

    def hashed_name(self, name, content=None, filename=None):
        try:
            result = super().hashed_name(name, content, filename)
        except ValueError:
            
            result = name
        return result