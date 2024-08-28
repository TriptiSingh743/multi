from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import boto3
import json
import re
import pandas as pd
from django.http import JsonResponse
from dotenv import load_dotenv

load_dotenv()

# AWS credentials
aws_access_key_id = os.getenv("AWS_ACCESS")
aws_secret_access_key = os.getenv("AWS_SECRET_KEY")

# Initialize Textract and Comprehend clients
textract_client = boto3.client(
    'textract',
    region_name='us-west-2',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

comprehend_client = boto3.client(
    'comprehend',
    region_name='us-west-2',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


def document_type_selection(request):
    return render(request, 'types.html')

def upload_page(request):
    return render(request, 'upload_page.html')

def upload_image(request):
    # Handle image upload logic here
    pass

def entities(request):
    extracted_text = request.session.get('extracted_text', '')
    entities_json = request.session.get('entities', '[]')
    entities = json.loads(entities_json)
    document_type = request.session.get('document_type', 'Unknown')
    return render(request, 'detected_entities.html', {
        'extracted_text': extracted_text,
        'entities': entities,
        'document_type': document_type
    })


from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm
from twilio.rest import Client
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import ContactForm

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

            return redirect('success')  # Redirect to a success page

    else:
        form = ContactForm()

    return render(request, 'home.html', {'form': form})


def success_view(request):
    return render(request, 'success.html')

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import extract_text_and_entities

@api_view(['POST'])
def upload_image(request):
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        image_file = request.FILES.get('image')
        if image_file:
            try:
                # Extract text and entities from the image
                extracted_text, detected_entities = extract_text_and_entities(image_file)
            # Initialize df with an empty DataFrame
                df = pd.DataFrame()

                # Detect entities using Comprehend
                comprehend_response = comprehend_client.detect_entities(Text=extracted_text, LanguageCode='en')
                if comprehend_response.get('Entities'):
                    df = pd.DataFrame(comprehend_response['Entities'])    

                phone_pattern = re.compile(r'\+?\d[\d -]{8,}\d')
                email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                website_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                postal_code_pattern = re.compile(r'\b\d{6}\b')


                def identify_entity(row):
                    text = row['Text']
                    if row['Type'] in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                        return row['Type']
                    elif phone_pattern.search(text):
                        return 'PHONE_NUMBER'
                    elif email_pattern.search(text):
                        return 'EMAIL'
                    elif website_pattern.search(text):
                        return 'WEBSITE'
                    elif postal_code_pattern.search(text):
                        return 'POSTAL_CODE'
                    else:
                        return 'OTHER'

                df['Type'] = df.apply(identify_entity, axis=1)
                df = df[['Score', 'Type', 'Text', 'BeginOffset', 'EndOffset']]

                # Store data in session
                request.session['extracted_text'] = extracted_text
                request.session['entities'] = json.dumps(df.to_dict(orient='records'))
                request.session['document_type'] = document_type

                return JsonResponse({
                    'extracted_text': extracted_text,
                    'show_entities_button': True,
                    'entities':detected_entities,
                })
            except Exception as e:
                print(f"Error processing image: {e}")
                return JsonResponse({'error': 'There was an error processing the image.'})
        else:
            return JsonResponse({'error': 'No image file provided.'})
    return JsonResponse({'error': 'Invalid request method.'})

    
def entities(request):
    extracted_text = request.session.get('extracted_text', '')
    entities_json = request.session.get('entities', '[]')
    entities = json.loads(entities_json)
    document_type = request.session.get('document_type', 'Unknown')
    
    
    return render(request, 'detected_entities.html', {
        'extracted_text': extracted_text,
        'entities': entities,
        'document_type': document_type
    })

