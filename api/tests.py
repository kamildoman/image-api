import json
from .models import User, ImageModel, FetchLink
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
from django.utils import timezone
import time


def create_image():
    bts = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    return SimpleUploadedFile("test.jpg", bts.getvalue())

def delete_test_images():
    for image in ImageModel.objects.all():
        if "test" in image.photo.name:
            image.delete()

class ImageModelCreationTestCase(APITestCase):
    #basic user should only create a photo without any thumbnails; premium and enterprise users 
    #should create photo, thumbnail200 and thumbnail400
    def test_basic_user(self):
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        fp = create_image()
        image_model = ImageModel.objects.create(owner=user, photo=fp)
        self.assertTrue(image_model.photo != None)
        self.assertTrue(image_model.thumbnail == None)
        self.assertTrue(image_model.thumbnail400 == None)
        delete_test_images()

    def test_premium_user(self):
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_premium = True)
        fp = create_image()
        image_model = ImageModel.objects.create(owner=user, photo=fp)
        self.assertTrue(image_model.photo != None)
        self.assertTrue(image_model.thumbnail != None)
        self.assertTrue(image_model.thumbnail400 != None)
        delete_test_images()


    def test_enterprise_user(self):
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_enterprise = True)
        fp = create_image()
        image_model = ImageModel.objects.create(owner=user, photo=fp)
        self.assertTrue(image_model.photo != None)
        self.assertTrue(image_model.thumbnail != None)
        self.assertTrue(image_model.thumbnail400 != None)
        delete_test_images()



class TemporaryImageTestCase(APITestCase):

    #I check if temporary images really get expired. The first one is not expired, the second one is
    def test_not_expired(self):
        now = timezone.now()
        added = datetime.timedelta(0, 300)
        expiration = now + added
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        fp = create_image()
        image_model = ImageModel.objects.create(owner=user, photo=fp)
        FetchLink.objects.create(original_url = image_model.photo.name, temporary_url="bbb", expiration_date=expiration)
        url = reverse('temporary_image', args=["bbb"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expired(self):
        now = timezone.now()
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        fp = create_image()
        image_model = ImageModel.objects.create(owner=user, photo=fp)
        FetchLink.objects.create(original_url = image_model.photo.name, temporary_url="ccc", expiration_date=now)
        time.sleep(1)
        response = self.client.get(reverse('temporary_image', args=["bbb"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        delete_test_images()




class MediaAccessTestCase(APITestCase):
    #check if user can access his own image
    def test_users_own_image(self):
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        fp = create_image()
        image_model = ImageModel.objects.create(owner=user, photo=fp)
        self.assertTrue(self.client.login(username='my_username', password='ASasDwdWADsDW1122@@'))
        url = reverse('media_access', args=[str(image_model.photo.name)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #check if other user can access other user's image
    def test_user_other_users_image(self):
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        user2 = User.objects.create_user(username="my_username2", email="aa@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        fp = create_image()
        image_model = ImageModel.objects.create(owner=user, photo=fp)
        self.assertTrue(self.client.login(username='my_username2', password='ASasDwdWADsDW1122@@'))
        url = reverse('media_access', args=[str(image_model.photo.name)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)     
        delete_test_images()



class ImageUploadTestCase(APITestCase):
    #users upload photos from API
    def test_basic_user_upload(self):
        user = User.objects.create_user(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        self.client.force_authenticate(user)
        fp = create_image()
        response = self.client.post(reverse('upload'), 
                                   {'photo': fp}, 
                                   format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        delete_test_images()
        

    def test_enterprise_user_upload(self):
        user = User.objects.create(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_enterprise = True)
        self.client.force_authenticate(user)
        fp = create_image()
        response = self.client.post(reverse('upload'), 
                                   {'photo': fp}, 
                                   format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        delete_test_images()

    def test_anonymous_user_upload(self):
        fp = create_image()
        response = self.client.post(reverse('upload'), 
                                   {'photo': fp}, 
                                   format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        delete_test_images()


            




class FetchTestCase(APITestCase):
    #Only enterprise users can fetch images from the API. This class checks if it's true
    def test_basic_user_permission(self):
        user = User.objects.create(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_basic = True)
        self.client.force_authenticate(user)
        data = {"link":"http://127.0.0.1:8000/media/pic.jpg",
        "expiration_time": "5000"}
        response = self.client.post(reverse('fetch'),
                           data=json.dumps(data),
                           content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_premium_user_permission(self):
        user = User.objects.create(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_premium = True)
        self.client.force_authenticate(user)
        data = {"link":"http://127.0.0.1:8000/media/pic.jpg",
        "expiration_time": "5000"}
        response = self.client.post(reverse('fetch'),
                           data=json.dumps(data),
                           content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_enterprise_user_permission(self):
        user = User.objects.create(username="my_username", email="a@gmail.com", password="ASasDwdWADsDW1122@@", is_enterprise = True)
        self.client.force_authenticate(user)
        data = {"link":"http://127.0.0.1:8000/media/pic.jpg",
        "expiration_time": "5000"}
        response = self.client.post(reverse('fetch'),
                           data=json.dumps(data),
                           content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        





