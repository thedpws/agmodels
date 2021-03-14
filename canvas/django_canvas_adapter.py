from django.core.files.storage import Storage
from .canvas_file_storage import CanvasFileStorage

class DjangoCanvasStorage(Storage):
    def __init__(self, option=None):
        pass

    def _open(name, mode='rb'):
        course_id = name.split('/')[0]
        name = name.removeprefix('/').removeprefix(course_id)

        return CanvasFileStorage(course_id).open(name)

    def _save(name, content):
        course_id = name.split('/')[0]
        name = name.removeprefix('/').removeprefix(course_id)

        with open(content, 'rb') as c:
            with CanvasFileStorage(course_id).open(name) as f:
                f.write(c.read())
        return name

    def exists(name):
        course_id = name.split('/')[0]
        name = name.removeprefix('/').removeprefix(course_id)

        return CanvasFileStorage(course_id).exists(name)
