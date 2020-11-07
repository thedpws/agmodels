from django.conf import settings
from django.core.files.storage import Storage
from django.core.files import File

from main.hipergator.hipergator_client import HiPerGatorClient

class HiPerGatorStorage(Storage):
    def __init__(self, option=None):
        self.hpg = HiPerGatorClient()
        #option = option if option else settings.CUSTOM_STORAGE_OPTIONS

    def _open(self, filepath, mode='rb'):
        with self.hpg.open_file(filepath, mode, from_storage=True) as f:
            g = File(f)
        return g

    def _save(self, filepath, content):
        with self.hpg.open_file(filepath, 'wb', from_storage=True) as f:
            with content.open('rb') as c:
                f.write(c.read())
        return filepath
    
    def exists(self, filepath):
        stdout, stderr = self.hpg.exec_command(f'test -f {filepath} && echo hi', from_storage=True)
        return bool(stdout.strip())





