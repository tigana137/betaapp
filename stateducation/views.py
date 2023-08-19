from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Value
from django.db.models.functions import Concat

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ecole_data, eleves, classes

import requests
import time
from bs4 import BeautifulSoup as bs
# Create your views here.


request = requests.session()
payloadd = {"login": "843422",
            "mp": "rB3Mv1"}
url = "http://stat.education.tn/"
request.post(url, data=payloadd)


@api_view(['GET'])
def test(request):
    payload = {"1": "","choix_annee":"2021","choix_dre":"84","choix_typeetab":"10","choix_etab":"843422"
               }
    
