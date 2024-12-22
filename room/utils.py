import os
import json
from django.conf import settings

def getCodeJson():
    file_path = os.path.join(settings.BASE_DIR, 'djangochat/static/json/codes.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)   
    return data

def findCodeJson(slug):
    codeJson = getCodeJson()
    data = codeJson['data']
    codeRec = [rec for rec in data if rec['slug'] == slug  ]
    return codeRec[0]