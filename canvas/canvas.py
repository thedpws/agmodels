import os

from canvasapi import Canvas
from canvasapi.requester import Requester

CANVAS_API_URL = os.environ['CANVAS_API_URL']
CANVAS_API_KEY = os.environ['CANVAS_API_KEY']

canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)
requester = Requester(CANVAS_API_URL, CANVAS_API_KEY)
