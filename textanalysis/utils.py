from io import BytesIO
import boto3
import json
import re
import pandas as pd
from django.http import JsonResponse

def extract_text_and_entities(image_file):
    # Convert image file to BytesIO
    image_bytes = BytesIO()
    for chunk in image_file.chunks():
        image_bytes.write(chunk)
    
    image_bytes.seek(0)  # Rewind the BytesIO object for reading
    
    # Initialize AWS clients
    textract_client = boto3.client('textract')
    comprehend_client = boto3.client('comprehend')

    # Use AWS Textract to extract text from the image
    textract_response = textract_client.detect_document_text(
        Document={'Bytes': image_bytes.getvalue()}
    )

    # Extract the text
    extracted_text = ''
    for item in textract_response.get('Blocks', []):
        if item.get('BlockType') == 'LINE':
            extracted_text += item.get('Text', '') + '\n'

    # Detect entities using Comprehend
    comprehend_response = comprehend_client.detect_entities(Text=extracted_text, LanguageCode='en')
    df = pd.DataFrame(comprehend_response['Entities'])

    # Define patterns for phone, email, website, and postal code
    phone_pattern = re.compile(r'\+?\d[\d -]{8,}\d')
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    website_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    postal_code_pattern = re.compile(r'\b\d{6}\b')

    # Identify the type of each entity
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

    # Apply the identify_entity function
    df['Type'] = df.apply(identify_entity, axis=1)
    df = df[['Score', 'Type', 'Text', 'BeginOffset', 'EndOffset']]

    # Initialize detected entities dictionary
    detected_entities = {
        "phone_number": None,
        "email": None,
        "address": None,
        "date": None,
        "PERSON":None,
        "POSTAL_CODE":None,
        "ORGANIZATION":None,
        "WEBSITE":None

    }

    # Extract specific entities
    for _, row in df.iterrows():
        if row['Type'] == 'PHONE_NUMBER' and detected_entities['phone_number'] is None:
            detected_entities['phone_number'] = row['Text']
        elif row['Type'] == 'EMAIL' and detected_entities['email'] is None:
            detected_entities['email'] = row['Text']
        elif row['Type'] == 'LOCATION' and detected_entities['address'] is None:
            detected_entities['address'] = row['Text']
        elif row['Type'] == 'DATE' and detected_entities['date'] is None:
            detected_entities['date'] = row['Text']
        elif row['Type'] == 'PERSON' and detected_entities['PERSON'] is None:
            detected_entities['PERSON'] = row['Text']    
        elif row['Type'] == 'POSTAL_CODE' and detected_entities['POSTAL_CODE'] is None:
            detected_entities['POSTAL_CODE'] = row['Text']
        elif row['Type'] == 'ORGANIZATION' and detected_entities['ORGANIZATION'] is None:
            detected_entities['ORGANIZATION'] = row['Text']   
        elif row['Type'] == 'WEBSITE' and detected_entities['WEBSITE'] is None:
            detected_entities['WEBSITE'] = row['Text']        
                    

    return extracted_text, detected_entities