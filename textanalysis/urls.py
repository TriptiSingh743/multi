from django.contrib import admin
from django.urls import path
from textanalysis.views import home
from . import views

from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # This should be the default route
    path('document-type-selection/', views.document_type_selection, name='document_type_selection'),
    path('upload-page/', views.upload_page, name='upload_page'),
    path('api/upload-image/', views.upload_image, name='upload_image'),
    path('entities/', views.entities, name='entities'),
    path('contact/', views.contact_view, name='contact'),
    path('success/', views.success_view, name='success'),
    
]
     




