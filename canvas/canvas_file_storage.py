from __future__ import annotations
from typing import TYPE_CHECKING

import os
import io
from tempfile import TemporaryDirectory

from canvasapi.exceptions import ResourceDoesNotExist
from .canvas import requester, canvas

if TYPE_CHECKING:
    from typing import Union


# These classes act as a wrapper around the ucfopen/canvasapi library. They are inherently hard to test.
AG_ROOT_FULLPATH = 'Autograding'
IMPLICIT_FS_ROOT = 'course files'


class CanvasFile(io.FileIO):
    def __init__(self, canvasapi_course, filepath: str):
        self._canvasapi_course = canvasapi_course
        self._filepath = filepath

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _get_folder(self, dirname: str):
        dirname = '/'.join([AG_ROOT_FULLPATH, dirname])

        _course_root_folder = self._canvasapi_course.resolve_path(full_path=None)[0]
        current_folder = _course_root_folder

        for subdirname in dirname.split('/'):
            # find folder in current folder with matching name
            try:
                full_name = '/'.join([current_folder.full_name.removeprefix(IMPLICIT_FS_ROOT), subdirname])
                folders_in_path = self._canvasapi_course.resolve_path(full_name)
                current_folder = list(folders_in_path)[-1]
            except ResourceDoesNotExist:
                current_folder = current_folder.create_folder(name=subdirname)

        return current_folder

    def write(self, data: Union[str, bytes]):

        dirname = os.path.dirname(self._filepath)
        filename = os.path.basename(self._filepath)

        destination_folder = self._get_folder(dirname)

        with TemporaryDirectory() as tmpdirpath:
            tmpfilepath = '/'.join([tmpdirpath, filename])

            with open(tmpfilepath, 'wb') as f:
                f.write(data)

            is_successful, json_res = destination_folder.upload(file=tmpfilepath)

            if not is_successful:
                raise RuntimeError(f'Uploading to {tmpfilepath} failed. (Response was "{json_res}".)')

        bytes_written = len(data)

        return bytes_written

    def read(self) -> bytes:

        dirname = os.path.dirname(self._filepath)
        filename = os.path.basename(self._filepath)

        destination_folder = self._get_folder(dirname)

        for file in destination_folder.get_files():
            if file.display_name == filename:
                return requester.request(method='GET', _url=file.url).content
        else:
            return b''

    def exists(self) -> bool:

        dirname = os.path.dirname(self._filepath)
        filename = os.path.basename(self._filepath)

        destination_folder = self._get_folder(dirname)

        for file in destination_folder.get_files():
            if file.display_name == filename:
                return True
        else:
            return False

    def open(self, mode):
        return self

    def close(self):
        pass


class CanvasFileStorage(object):
    def __init__(self, course_id: Union[str, int]):
        self._canvasapi_course = canvas.get_course(course_id)

    def open(self, filepath: str):
        filepath = filepath.removeprefix('/')
        return CanvasFile(self._canvasapi_course, filepath)

    def exists(self, filepath: str):
        filepath = filepath.removeprefix('/')
        return CanvasFile(self._canvasapi_course, filepath).exists()
