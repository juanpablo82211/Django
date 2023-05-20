import datetime
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UserRegisterForm
from .models import Template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from .models import Template, Comment
from .forms import CommentForm
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
import os
from django.conf import settings
from django.core.files import File
from django.conf import settings
from io import BytesIO
from django.core.files.storage import default_storage
from PIL import Image
from django.core.files.base import ContentFile
import io

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        self.stopped = False
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.stop()

    def stop(self):
        self.stopped = True
        self.video.release()

    def get_frame(self):
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

    def update(self):
        while not self.stopped:
            (self.grabbed, self.frame) = self.video.read()

camera = VideoCamera()


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            
            messages.success(request, f'Usuario {username} creado')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    context = {'form': form}
    return render(request, 'registration/register.html', context)
    

@login_required

@login_required
def home(request):
    username = request.user.username
    templates = Template.objects.all().order_by('-id')
    context = {'username': username, 'templates': templates}

    # Crear una instancia de la cámara solo si se accede a la página principal
    if request.path == '/':
        context['show_camera'] = True

    return render(request, 'home.html', context)




'''@login_required
def templates_view(request, video_number=None):
    templates = Template.objects.all().order_by('-id')[:10]

    if request.method == 'POST':
        if len(templates) == 10:
            template_to_delete = templates[9]
            Comment.objects.filter(template=template_to_delete).delete()
            template_to_delete.delete()

        template = Template(name=f'video.html', user=request.user)
        template.save()

        # Obtiene el video_number del nuevo template agregado
        video_number = template.id

        # Redirige a la vista del nuevo template agregado
        capture_last_frame()
        return redirect('template_detail', video_number=video_number)

    if video_number:
        video_number = int(video_number)
        if video_number < 1 or video_number > len(templates):
            return redirect('home')

    username = request.user.username
    return render(request, 'home.html', {'templates': templates, 'current_video': video_number, 'username': username})'''

@login_required
def templates_view(request, video_number=None):
    templates = Template.objects.all().order_by('-id')[:10]

    if request.method == 'POST':
        if len(templates) == 10:
            template_to_delete = templates[9]
            Comment.objects.filter(template=template_to_delete).delete()
            template_to_delete.delete()

        template = Template(name=f'video.html', user=request.user)
        template.save()

        # Capturar el último frame de la cámara y guardarlo en la carpeta de medios
        image_url = capture_last_frame()

        # Guardar la URL del último frame en el nuevo template
        template.last_frame_url = image_url
        template.save()

        # Obtiene el video_number del nuevo template agregado
        video_number = template.id

        # Redirige a la vista del nuevo template agregado
        return redirect('template_detail', video_number=video_number)

    if video_number:
        video_number = int(video_number)
        if video_number < 1 or video_number > len(templates):
            return redirect('home')

    username = request.user.username

    context = {
        'templates': templates,
        'current_video': video_number,
        'username': username,
        'show_camera': True,
    }

    return render(request, 'home.html', context)



@login_required
def template_detail(request, video_number):
    template_number = int(video_number)
    template = Template.objects.filter(id=template_number).first()
    

    if not template:
        return redirect('home')

    template_text = ""
    if template_number == 1:
        template_text = "Hola"
    elif template_number == 2:
        template_text = "Adiós"

    templates = Template.objects.all().order_by('-id')[:10]

    # Filtrar los comentarios específicamente para el template actual
    comments = Comment.objects.filter(template=template)

    # Crear una nueva instancia de CommentForm
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.template = template
            comment.save()
            return redirect('template_detail', video_number=template.id)

    username = request.user.username
    context = {
        'template_text': template_text,
        'templates': templates,
        'username': username,
        'comments': comments,
        'form': form,
        'template_id': template.id,
        'video_number': template.id,
        'imagen' : template.last_frame_url,
    }

    return render(request, 'template_detail.html', context)




def clear_templates(request):
    Template.objects.all().delete()
    return redirect('home')




@gzip.gzip_page
@login_required
def video_feed(request):
    current_url = request.META['HTTP_REFERER']
    if current_url == 'http://127.0.0.1:8000/':
        return StreamingHttpResponse(gen(camera), content_type="multipart/x-mixed-replace;boundary=frame")
    else:
        return HttpResponse()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        


def capture_last_frame():
    # Capturar el último frame de la cámara
    frame = camera.get_frame()

    # Obtener el nombre del archivo de imagen
    image_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.jpg'

    # Guardar el frame en la carpeta de medios
    image_path = default_storage.path(os.path.join(settings.MEDIA_ROOT, 'imagenes', image_name))
    with open(image_path, 'wb') as f:
        f.write(frame)

    # Obtener la URL de la imagen guardada
    image_url = os.path.join(settings.MEDIA_URL, 'imagenes', image_name)

    # Actualizar la URL del último frame en el modelo Template
    template = Template.objects.latest('id')
    template.last_frame_url = image_url
    template.save()

    print("Último frame capturado y guardado correctamente.")
    return image_url