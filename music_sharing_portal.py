# music_sharing_portal/urls.py
from django.urls import path
from music_app.views import register, login_view, upload_file, homepage

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('upload/', upload_file, name='upload'),
    path('', homepage, name='homepage'),
]


# music_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    email = models.EmailField(unique=True)


class MusicFile(models.Model):
    PUBLIC = 'public'
    PRIVATE = 'private'
    PROTECTED = 'protected'
    ACCESS_CHOICES = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (PROTECTED, 'Protected'),
    )

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='music_files/')
    access_type = models.CharField(
        max_length=10,
        choices=ACCESS_CHOICES,
        default=PUBLIC,
    )
    allowed_emails = ArrayField(
        models.EmailField(),
        blank=True,
        null=True,
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
    )


# music_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from music_app.models import User, MusicFile


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        User.objects.create_user(email=email, password=password)
        return redirect('login')
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            return redirect('login')
    return render(request, 'login.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        title = request.POST['title']
        file = request.FILES['file']
        access_type = request.POST['access_type']
        allowed_emails = []
        if access_type == 'protected':
            emails = request.POST.getlist('allowed_emails')
            for email in emails:
                if User.objects.filter(email=email).exists():
                    allowed_emails.append(email)
        MusicFile.objects.create(
            title=title,
            file=file,
            access_type=access_type,
            allowed_emails=allowed_emails,
            uploaded_by=request.user,
        )
        return redirect('homepage')
    return render(request, 'upload.html')


@login_required
def homepage(request):
    music_files = MusicFile.objects.filter(
        models.Q(access_type=MusicFile.PUBLIC) |
        models.Q(access_type=MusicFile.PRIVATE, uploaded_by=request.user) |
        models.Q(access_type=MusicFile.PROTECTED, allowed_emails=request.user.email)
    )
    return render(request, 'homepage.html', {'music_files': music_files})


# music_sharing_portal/settings.py
...
INSTALLED_APPS = [
    ...
    'music_app',
]

TEMPLATES = [
    {
        ...
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        ...
    },
]

...

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# music_sharing_portal/templates/register.html
<form method="POST" action
