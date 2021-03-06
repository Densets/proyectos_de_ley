from django.conf.urls import url

from .views import index, about, search, congresista, proyecto


urlpatterns = [
    # '',
    url(r'^$', index, name='index'),
    url(r'^about/$', about, name='about'),
    url(r'^search/$', search, name='search'),
    url(r'^congresista/(?P<congresista_slug>.*)$', congresista,
        name='congresista'),

    url(r'^(?P<short_url>[0-9a-z]*)/$', proyecto),
]
