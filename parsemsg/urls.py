from django.conf.urls import url

from .views import UploadMsg, ShowMsg


urlpatterns = [
    url('^$', UploadMsg.as_view(), name='upload_msg'),
    url('^(?P<file_name>[a-zA-Z0-9.-_]+)/?$', ShowMsg.as_view(), name='show_msg'),
]