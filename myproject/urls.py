# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('textanalysis.urls')),  # Ensure this points to your app's urls.py
]

urlpatterns += staticfiles_urlpatterns()

