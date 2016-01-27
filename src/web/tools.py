from django.http import HttpResponse
import json

from host_moniter.settings import *

def init_jresponse():
    return {"errorno": FAILED_NUM, "errmsg": ""}

def error_jresponse(errmsg):
    result = {"errorno": FAILED_NUM, "errormsg":errmsg}
    return HttpResponse(json.dumps(result))

def success_jresponse(data):
    result = {"errorno":SUCCESS_NUM, "errormsg":"", "data":data}
    return HttpResponse(json.dumps(result))
