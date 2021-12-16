from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from . models import Room, Topic, Message
from . forms import RoomForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


# ------------------------ USER LOGINS ---------------------------
def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST': #if form was submitted
        username = request.POST.get('username').lower() #lowercases username, they can login with whatever case
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

    

    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm() #Default creation form for DJANGO users

    if request.method == "POST":
        form = UserCreationForm(request.POST) #Passed in data
        if form.is_valid():
            user = form.save(commit=False) #Get user object but not save ("Freeze in time")
            user.username = user.username.lower() #cleaning up the user information
            user.save()
            login(request, user) #once user is saved, log them in
            return redirect('home')
        else:
            messages.error(request, "An error has occurred during registration")

    context = {"form":form}
    return render(request, 'base/login_register.html', context)

#------------------------- MAIN PAGES --------------------------

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

    comments = Message.objects.filter(
        Q(room__topic__name__icontains=q) #filters activity feed through topic if clicked
        ).order_by("-created")

    #Context is the data being passed into the HTML page
    context = {'rooms' : rooms , "topics": topics, "room_count": room_count, "comments":comments}
    return render(request, 'base/home.html', context)

def room(request, pk):

    room = Room.objects.get(id=pk)
    comments = room.message_set.all().order_by('-created') #gets the set of objects related to object. Called by objname in lowercase
    participants = room.participants.all()
    if request.method == "POST":
        comment =  Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') #data that was submitted via input 'body'
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)


    context = {'room': room, 'comments':comments, 'participants':participants}
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    comments = user.message_set.all().order_by('-created')
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'comments':comments, 'topics':topics} #important to use 'rooms' as our feed component uses that variable
    return render(request, 'base/profile.html', context)

#----------------------------- CRUD Operations ----------------

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

@login_required(login_url='login')
def DeleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here!")


    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})    
