#-*- coding:utf-8 -*-

from django.http import JsonResponse
from django.shortcuts import render_to_response
from time import time as _time
from time import strptime
from time import mktime

import json

from tools import *
from host_moniter.settings import *
from host_moniter.models import APITest, APITestTime
import datetime

def list(request):
    return render_to_response('api_test.html', {"breadcrumb": [{"name": "API Test"}]})

def get_errors(request, name, period):
    try:
        period = int(period)
        if period > MAX_PERIOD :
            return error_jresponse("period out of range(1-%d)"%MAX_PERIOD)
        end_time = int(_time())
        start_time = int(end_time - period * PERIOD_INTERVAL_S)
        start_time = datetime.datetime.fromtimestamp(start_time)
        max_slices = period * PERIOD_INTERVAL_M
        
        
        data = APITest.objects.filter(time__gte=start_time).filter(group=name)
        err_datas = []
        if len(data) != 0:
            for d in data:
                err = {}
                err['url'] = d.url
                err['err_no'] = d.err_no
                err['err_msg'] = d.err_msg
                err['time'] = d.time.strftime('%Y-%m-%d %X')
                err_datas.append(err)
            
        times = APITestTime.objects.filter(time__gte=start_time)
        success_times = APITestTime.objects.filter(time__gte=start_time).filter(status=1)
        count = APITestTime.objects.filter(status=1).order_by('-id')[:1]
        if len(count) == 0:
            last = 'None'
        else:
            last = count[0].time.strftime('%Y-%m-%d %X')
            
        ret_data = {
                    'err_datas': err_datas,
                    'times': len(times),
                    'success_times': len(success_times),
                    'last': last,
                    'group': name
                    }
        return success_jresponse(ret_data)

    except Exception, e:
        return error_jresponse(str(e))

