from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from . models import Room, Topic
from . forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST': #if form was submitted
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) #adds session to database and browser
            return redirect('home')
        else:
            messages.error(request, "Username OR Password does not exist")

    

    context = {}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    
    #Main list data being shown
    q = request.GET.get('q') if request.GET.get('q') != None else '' #filters query with q
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | #get the value of the variable (name) in topic obj
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count = rooms.count()

    #This is for the side bar to display
    topics = Topic.objects.all()

    #Context is the data being passed into the HTML page
    context = {'rooms' : rooms , "topics": topics, "room_count": room_count}
    return render(request, 'base/home.html', context)

def room(request, pk):

    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, "base/room.html", context)


#CRUD Operations ----Room---

@login_required(login_url='login')
def CreateRoom(request):
    form = RoomForm()

# Create method to submit forms onto the database
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def UpdateRoom(request, pk):
    
    room = Room.objects.get(id=pk) #Get a specific room with primary key (pk)
    form = RoomForm(instance=room) #Set the form data equal to the room data (pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here!")


    #If the form is submitted redirect to home
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    #Direct user to form page with form data
    context = {'form': form}
    return render(request, "base/room_form.html", context)

@login_required(login_url='login')
def DeleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here!")


    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})  
