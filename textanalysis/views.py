from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .forms import ContactForm
from twilio.rest import Client
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from .models import UploadedImage
from .utils import (
    extract_text_from_image,
    process_passport,
    process_identity_card,
    process_aadhar_card,
    process_payment_receipt
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS credentials (from environment)
aws_access_key_id = os.getenv("AWS_ACCESS")
aws_secret_access_key = os.getenv("AWS_SECRET_KEY")

# Initialize AWS clients
textract_client = boto3.client(
    'textract',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

comprehend_client = boto3.client(
    'comprehend',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Validate image format
def validate_image_format(image):
    valid_image_formats = ['image/jpeg', 'image/png']
    if image.content_type not in valid_image_formats:
        raise ValidationError('Unsupported file format. Please upload a JPEG or PNG image.')

# Home page view
def home(request):
    return render(request, 'home.html')

# Document type selection view
def document_type_selection(request):
    return render(request, 'types.html')

# Upload page view
def upload_page(request):
    return render(request, 'upload_page.html')

# Handle image upload and process extracted text
@api_view(['POST'])
def upload_image(request):
    if request.method == 'POST':
        images = request.FILES.getlist('image')
        if not images:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        extracted_data = []
        
        try:
            for image in images:
                validate_image_format(image)
                
                # Save image to the server
                uploaded_image = UploadedImage(image=image)
                uploaded_image.save()

                # Extract text from the image
                image_path = uploaded_image.image.path
                extracted_text = extract_text_from_image(image_path)
                
                # Process extracted text based on document type
                document_type = request.data.get('document_type', 'unknown')
                if document_type == 'passport':
                    entities = process_passport(extracted_text)
                elif document_type == 'identity_card':
                    entities = process_identity_card(extracted_text)
                elif document_type == 'aadhar_card':
                    entities = process_aadhar_card(extracted_text)
                elif document_type == 'payment_receipt':
                    entities = process_payment_receipt(extracted_text)
                else:
                    return Response({"error": "Invalid document type provided."}, status=status.HTTP_400_BAD_REQUEST)

                extracted_data.append({
                    "name": uploaded_image.image.name,
                    "extracted_text": extracted_text,
                    "detected_entities": entities
                })

            # Save extracted data in the session for redirection to the results page
            request.session['extracted_data'] = extracted_data

            # Redirect to the results page
            return redirect('extracted_text_page')
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid request method."}, status=status.HTTP_400_BAD_REQUEST)

# Page to display extracted text for each uploaded image
def extracted_text_page(request):
    extracted_data = request.session.get('extracted_data', [])
    return render(request, 'extracted_text_page.html', {'extracted_data': extracted_data})




# Page to display detected entities for each uploaded image
def detected_entities_page(request):
    extracted_data = request.session.get('extracted_data', [])
    return render(request, 'detected_entities.html', {'extracted_data': extracted_data})


# Contact form view
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send SMS to admin
            client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
            sms_message = f"New contact from {name} ({email}): {message}"
            client.messages.create(
                body=sms_message,
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                to=os.getenv('ADMIN_PHONE_NUMBER')
            )

            return redirect('success')

    else:
        form = ContactForm()

    return render(request, 'home.html', {'form': form})

# Success page view
def success_view(request):
    return render(request, 'success.html')

