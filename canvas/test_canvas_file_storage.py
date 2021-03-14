import unittest
from unittest.mock import Mock
from .canvas_file_storage import CanvasFileStorage

class CanvasFileStorageTests(unittest.TestCase):

    def setUp(self):
        self.test_course_id = 388639

    # A documentation of how this is expected to be used.
    def test_reads_files(self):
        course_id = self.test_course_id

        with CanvasFileStorage(course_id).open('hello.txt') as f:
            self.assertEqual(b'Hello, world!', f.read())

    def test_writes_files(self):
        course_id = self.test_course_id

        with CanvasFileStorage(course_id).open('hello.txt') as f:
            self.assertEqual(f.write(b'Hello, world!'), 13)
