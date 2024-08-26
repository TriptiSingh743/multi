from django.contrib import admin
from django.urls import path
from textanalysis.views import home, document_type_selection, upload_page, upload_image, entities
from . import views

from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # This should be the default route
    path('document-type-selection/', document_type_selection, name='document_type_selection'),
    path('upload-page/', upload_page, name='upload_page'),
    path('api/upload-image/', upload_image, name='upload_image'),
    path('entities/', entities, name='entities'),
    path('contact/', views.contact_view, name='contact'),
    path('success/', views.success_view, name='success'),
    
]
     




