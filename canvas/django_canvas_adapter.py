from django.core.files.storage import Storage
from .canvas_file_storage import CanvasFileStorage


class DjangoCanvasStorage(Storage):
    def __init__(self, option=None):
        pass

    def _open(self, name, mode='rb'):
        course_id = name.split('/')[0]
        name = name.removeprefix('/').removeprefix(course_id)

        return CanvasFileStorage(course_id).open(name)

    def _save(self, name, content):
        original_name = name
        course_id = name.split('/')[0]
        name = name.removeprefix('/').removeprefix(course_id)

        with CanvasFileStorage(course_id).open(name) as f:
            f.write(content.read())

        return original_name

    def exists(self, name):
        course_id = name.split('/')[0]
        name = name.removeprefix('/').removeprefix(course_id)

        return CanvasFileStorage(course_id).exists(name)

    # TODO: Delete file if exists...
    def get_available_name(self, name, max_length):
        original_name = name

        return original_name

    def url(self, name):
        raise NotImplementedError('CanvasStorage does not support public URL\'s')
