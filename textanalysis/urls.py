from django.contrib import admin
from django.urls import path
from . import views
from .views import upload_image

from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), # This should be the default route
    path('document-type-selection/', views.document_type_selection, name='document_type_selection'),
    path('upload-page/', views.upload_page, name='upload_page'),
    path('upload/', upload_image, name='upload_image'),
    path('extracted_text_page/', views.extracted_text_page, name='extracted_text_page'),
   path('detected-entities/', views.detected_entities_page, name='detected_entities_page'),
    path('contact/', views.contact_view, name='contact'),
    path('success/', views.success_view, name='success'),
    
]
     




