
from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image
from django.core.validators import MinValueValidator, MaxValueValidator

class FetchLink(models.Model):
    original_url = models.CharField(max_length=100)
    temporary_url = models.CharField(max_length=100)
    expiration_date = models.DateTimeField()

    def __str__(self) -> str:
        return f"temp/{self.temporary_url}"

class User(AbstractUser):
    is_basic = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_enterprise = models.BooleanField(default=False)

class ImageModel(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(blank=True, null=True)
    thumbnail = models.ImageField(editable=False, null=True, blank=True)
    thumbnail400 = models.ImageField(editable=False, null=True, blank=True)
    custom_thumbnail = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(10),
                                       MaxValueValidator(1000)])


    def delete(self):
        self.photo.storage.delete(self.photo.name)
        if self.owner.is_premium or self.owner.is_enterprise:
            self.thumbnail.storage.delete(self.thumbnail.name)
            self.thumbnail400.storage.delete(self.thumbnail400.name)
        super().delete()
        

    def save(self, *args, **kwargs):

        if self.owner.is_superuser:
            if self.custom_thumbnail is None:
                super(ImageModel, self).save(*args, **kwargs)
            else:
                self.make_thumbnail((20000, self.custom_thumbnail))
                super(ImageModel, self).save(*args, **kwargs)

        elif self.owner.is_enterprise or self.owner.is_premium:   
            #the first number 2000 is thumbnail's width. 
            #I just put a random high number for the width, so only height matters
            self.make_thumbnail((2000, 200)) 
            self.make_thumbnail((4000, 400))    
            super(ImageModel, self).save(*args, **kwargs)
        else:   
            #if the user is basic I make a thumbnail and I save it as 'photo'
            self.make_thumbnail((2000, 200)) 
            self.photo = self.thumbnail
            self.thumbnail = None
            super(ImageModel, self).save()


    def make_thumbnail(self, size):

        image = Image.open(self.photo)

        image.thumbnail(size)
      
        thumb_name, thumb_extension = os.path.splitext(self.photo.name)
        thumb_extension = thumb_extension.lower()

        if size == (4000, 400):
            thumb_filename = thumb_name + '_thumb400' + thumb_extension
        else:
            thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    
        
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        
        temp_thumb.seek(0)
        if size == (4000, 400):
            self.thumbnail400.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        else:
            self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True

    



