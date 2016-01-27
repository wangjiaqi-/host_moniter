"""host_moniter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""


from django.conf.urls import url
from web import host, api

urlpatterns = [
    url(r"^$", host.hosts, name='index'),
    url(r"^hosts$", host.hosts, name='hosts'),
    url(r"^hosts/(.*)$", host.detail, name='details'),
    url(r"^add_host$", host.to_add_host_page, name='add_host_page'),
    url(r"^hosts$", host.add_host, name='add_host'),
    url(r"^test$", host.test, name='test'),
    url(r'^api_test/$', api.list, name = 'api_test'),
    url(r'^api_test/group/(.+)/(\d{1,3})$', api.get_errors, name='get_errors'),
]

# urlpatterns += patterns('web.api',
#     (r'^api_test$', 'list'),
#     (r'^api_test/group/(.+)/(\d{1,3})/$', 'get_errors'),
# )
