from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User 
from django.contrib import messages 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

# rooms = [
#     {'id':1, 'name':'learn python'},
#     {'id':2, 'name':'front'},
#     {'id':3, 'name':'backend'},
# ]

def loginPage(request):
    page = 'login'
    # redirect loged in user to home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # these two values are sent from frontend
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try: # user exist
            user = User.objects.get(username=username)
        except: # user not exist
            messages.error(request, 'User does not exist')

        # authenticate this user, return a user object or an error
        user = authenticate(request, username=username, password=password) 

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
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # request.POST is username and password we sent
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
    topics = Topic.objects.all()
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
    if request.method == 'POST':
        # print(request.POST) # data submited by user
        form = RoomForm(request.POST) # pass all post data into form, let form extract value
        if form.is_valid():
            form.save() # save that model in database
            return redirect('home') # redirect user to home page
    context = {'form': form} # pass into room_form.html
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk) # get the old room instance
    form = RoomForm(instance=room) # form will be prefilled with previous value

    # not the owner of the room
    if request.user != room.host:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) # update value of the room instance
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
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