from rest_framework import serializers
from .models import ImageModel



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
    
        # if not model.objects.first() or model.objects.first().thumbnail == "":
        #     fields = ['photo'] 
        # else:
        #     
        fields = ['photo', 'thumbnail', 'thumbnail400']

