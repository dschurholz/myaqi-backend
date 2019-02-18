"""aqi_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, re_path, include
from django.conf import settings

from common.views import home
from au_epa_data.urls import router as au_epa_data_router
from au_epa_data.rest_views import MeasurementsProxy

admin.site.site_header = 'MyAQI'


api_v1_prefix = r'^{0}/'.format(settings.API_PREFIX)

api_urlpatterns = [
    re_path(
        r'',
        include(
            ('au_epa_data.urls', 'au_epa_data'),
            namespace=au_epa_data_router.namespace
        )
    ),
    path(
        'measurements', MeasurementsProxy.as_view(), name='measurements-proxy')
]

urlpatterns = [
    re_path(api_v1_prefix, include((api_urlpatterns, 'api'), namespace='api')),
    path('admin/', admin.site.urls),
    path('', home, name='home')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
