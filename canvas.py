from canvasapi import Canvas
from canvasapi.requester import Requester

API_URL = 'https://ufl.instructure.com'
API_KEY = '1016~pVuFpEDKZyEnlPMBZofMA6MuWUJtaHyd9dekfdThHNFMYmKGSHzroSqX1uIUu1RA'
canvas = Canvas(API_URL, API_KEY)
requester = Requester(API_URL, API_KEY)
