from .models import ImageModel, FetchLink
from .serializers import ImageSerializer
from rest_framework import generics
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import json
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http.response import FileResponse, Http404
from django.http import HttpResponseForbidden
import random
import string
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test



def delete_expired_links():
    now = timezone.now()
    for link in FetchLink.objects.all():
        print(link.expiration_date)
        print(now)
        if link.expiration_date < now:
            link.delete()


@api_view(["POST"])
@user_passes_test(lambda u: u.is_enterprise)
def fetch_link(request):
    path = request.data["link"].split("media/")[1]
    expiration_time = int(request.data["expiration_time"])
    if expiration_time < 300 or expiration_time > 30000:
        return Response({"error": "The expiration time should be between 300 and 30000"})
    else:
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))   
        now = timezone.now()
        added = datetime.timedelta(0, expiration_time)
        expiration = now + added
        FetchLink.objects.create(original_url = path, temporary_url = ran, expiration_date = expiration)
        current_url = request.get_host()
        Res = {"Link:": f"http://{current_url}/temp/{ran}"}
        
        return Response(Res)


def temporary_image(request, path):
    #every time someone wants to see a temporary image I delete all expired temp images
    delete_expired_links()
    try:
        image = FetchLink.objects.get(temporary_url = path)
    except Exception:
        raise Http404("The image doesn't exist or get expired")
    image_data = open(f"media/{image.original_url}", 'rb')
    photo = FileResponse(image_data)
    return photo


        
#Only image owners can see them.
def media_access(request, path):    
    user = request.user
    if user.is_anonymous:
        return HttpResponseForbidden("Please log in to see the image")


    try:
        if "thumb400" in path:
            image_model = ImageModel.objects.get(thumbnail400=path)
        elif "thumb" in path and not user.is_basic:
            image_model = ImageModel.objects.get(thumbnail=path)
        else:
            image_model = ImageModel.objects.get(photo=path)
    except Exception:
        return HttpResponseForbidden("The image does not exist or you don't have permission to see it")

    if image_model.owner == user:
        img = open(f'media/{path}', 'rb')
        response = FileResponse(img)
        return response
    else:
        return HttpResponseForbidden("You cannot see the image")



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_logout(request):

    logout(request)

    return Response('User Logged out successfully')

@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):

        data = {}
        reqBody = json.loads(request.body)
        username = reqBody['username']
        password = reqBody['password']
        try:
            Account = User.objects.get(username=username)
        except BaseException as e:
            raise ValidationError({"400": f'{str(e)}'})

        
        if password != Account.password:
            raise ValidationError({"message": "Wrong password!"})

        if Account:
            login(request, Account)
            data["message"] = "user logged in"
            data["username"] = Account.username

            Res = {"data": data}
            request.session.save()
            return Response(Res)

        else:
            raise ValidationError({"400": f'Account doesnt exist'})


class ImageViewSet(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self):
        return ImageModel.objects.all().filter(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        try:
            file = request.FILES['photo']
        except Exception:
            return HttpResponse("Please upload a photo")
        image = ImageModel.objects.create(owner=request.user, photo=file)

        page=request.build_absolute_uri('')
        photo_url = image.photo.url[1:]
        
        if request.user.is_basic:
                return HttpResponse(f"Photo Link: <a href='{page}{photo_url}'>here</a>,      <a href='/'>Go back</a>", status=201)
        else:
            thumbnail = image.thumbnail.url[1:]
            thumbnail400 = image.thumbnail400.url[1:]
            return HttpResponse(f"Photo Link: <a href='{page}{photo_url}'>here</a>, Thumb200 Link: <a href='{page}{thumbnail}'>here</a>, Thumb400 Link: <a href='{page}{thumbnail400}'>here</a>,      <a href='/'>Go back</a>", status=201)

