from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class ReplaceFileStorage(FileSystemStorage):
    """
    Replaces a file on a server (with the same name) instead of renaming it and retaining the old file.

    If you have a FileField with file 'example.txt' uploaded and then upload another 'example.txt' to the same field,
    by default this would rename the new file like 'example_938r38.txt' and retain both files.
    Whereas this deletes the old 'example.txt' and uploads the new 'example.txt' as is.

    Example of usage in a model field:
    my_file_field = models.FileField(upload_to='mediasubdir', storage=storage.ReplaceFileStorage(), blank=True, null=True)
    """

    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
