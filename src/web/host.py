from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from host_moniter.models import Host

import json

def hosts(request):
    # host is a list
    hosts = Host.get_all()
    return render_to_response("hosts.html", {"hosts":hosts, "breadcrumb": [{"name": "Hosts"}]})

def detail(request, host=""):
    # detail is a dict
    details = Host.get_detail(host)
    ip = details['ip']
    cpu = details['cpu']
    disk_per = details['disk_per']
    mem = details['mem']
    net = details['net_bandwidth']
    times = json.dumps(details['time'])
    return render_to_response("host_detail.html", {"host":host, "ip":ip, "cpu":cpu, "disk_per":disk_per, "mem":mem, "net":net, 
                                                   "time":times, "details":details, "breadcrumb": [{"name": "Host", "url": "/"}, {"name": host}]})


def to_add_host_page(request):
    return render_to_response('add_host.html', {"breadcrumb":[{"name": "Home","url": "/"}, {"name":"Add Host"}]})


def add_host(request):
    if request.method != "POST":
        return None
    host = request.POST["hostname"]
    ip = request.POST["ip"]
    user = request.POST["user"]
    password = request.POST["password"]
    try:
        Host(name=host).add_host(host, ip, user, password)
    except RuntimeError:
        return None
    return redirect(request.session.get("last_visited"))


def test(request):
    return render_to_response("test.html")