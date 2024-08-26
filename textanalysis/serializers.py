from rest_framework import serializers
from .models import UploadedImage

class ExtractedTextSerializer(serializers.Serializer):
    Score = serializers.FloatField()
    Type = serializers.CharField()
    Text = serializers.CharField()
    BeginOffset = serializers.IntegerField()
    EndOffset = serializers.IntegerField()

class ImageDataSerializer(serializers.ModelSerializer):
    extracted_text = serializers.CharField()
    detected_entities = ExtractedTextSerializer(many=True)

    class Meta:
        model = UploadedImage
        fields = ('id', 'image', 'uploaded_at', 'extracted_text', 'detected_entities')
