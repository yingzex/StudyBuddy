from django.shortcuts import render, redirect
# from django.http import HttpResponse
from .models import Room, Topic
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User 
from django.contrib import messages 
from django.contrib.auth import authenticate, login, logout

# Create your views here.

# rooms = [
#     {'id':1, 'name':'learn python'},
#     {'id':2, 'name':'front'},
#     {'id':3, 'name':'backend'},
# ]

def loginPage(request):
    if request.method == 'POST':
        # these two values are sent from frontend
        username = request.POST.get('username')
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

    context = {}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

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

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count}
    # return HttpResponse('Home page') # return http response
    return render(request, 'base/home.html', context) # pass dictionary rooms

def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room':room} 
    # pass in value of room into base/room.html
    return render(request, 'base/room.html', context)

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

def updateRoom(request, pk):
    room = Room.objects.get(id=pk) # get the old room instance
    form = RoomForm(instance=room) # form will be prefilled with previous value
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) # update value of the room instance
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def deleteRoom(request, pk):
    # get the room
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
            room.delete()
            return redirect('home') 
    return render(request, 'base/delete.html', {'obj':room})