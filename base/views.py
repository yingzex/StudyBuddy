from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q
# from django.contrib.auth.models import User 
from django.contrib import messages 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def loginPage(request):
    page = 'login'
    # redirect loged in user to home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # these two values are sent from frontend
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try: # user exist
            user = User.objects.get(email=email)
        except: # user not exist
            messages.error(request, 'User does not exist')

        # authenticate this user, return a user object or an error
        user = authenticate(request, email=email, password=password) 

        # use the user to login
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST) # request.POST is username and password we sent
        if form.is_valid(): # user get created
            user = form.save(commit=False) # commit=False: so we can access user before save it
            user.username = user.username.lower() # make sure username is lower case
            user.save()
            login(request, user) # login the newly registered user
            return redirect('home') # send the user to home page
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'base/login_register.html', {'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q')!=None else '' # get parameter q from url
    # filter: get all rooms in the database that meet requirement
    # search based on 3 attributes, any of them contains q
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) | 
        Q(description__icontains=q))
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    # return HttpResponse('Home page') # return http response
    return render(request, 'base/home.html', context) # pass dictionary rooms

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created') # query child objects of a specific room
    participants = room.participants.all()

    if request.method == 'POST':
        # create a message
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') # passed from room.html
        )
        room.participants.add(request.user) # when a user send a message in a room, add the user to participants
        return redirect('room', pk=room.id) # reload the page and use get request instead

    context = {'room':room, 'room_messages':room_messages, 'participants':participants} 
    # pass in value of room into base/room.html
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() # all rooms of this user
    room_messages = user.message_set.all() # all msg of the user
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login') # if session id not in browser, redirect to login page
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic, # newly created topic, or topic from database
            name=request.POST.get('name'), # get from frontend
            description=request.POST.get('description') # get from frontend
        )
        return redirect('home') # redirect user to home page
    context = {'form': form, 'topics': topics} # pass into room_form.html
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk) # get the old room instance
    form = RoomForm(instance=room) # form will be prefilled with previous value
    topics=Topic.objects.all()
    # not the owner of the room
    if request.user != room.host:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST.get('name')
        room.topic=topic
        room.description=request.POST.get('name')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)



@login_required(login_url='login')
def deleteRoom(request, pk):
    # get the room
    room = Room.objects.get(id=pk)

    # not the owner of the room
    if request.user != room.host:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        room.delete()
        return redirect('home') 

    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    # get the room
    message = Message.objects.get(id=pk)

    # not the owner of the msg
    if request.user != message.user:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        message.delete()
        return redirect('home') 

    return render(request, 'base/delete.html', {'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)
    if request.method=='POST':
        form=UserForm(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    return render(request, 'base/update-user.html', {'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q')!=None else '' # get parameter q from url
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, "base/activity.html", {'room_messages':room_messages})