from django import forms
from django.shortcuts import render, redirect
from . models import Room
from . forms import RoomForm
# rooms = [
#      {'id':1 , 'name':'Lets learn python!'},
#      {'id':2 , 'name':'Design with me'},
#      {'id':3 , 'name':'Front end developers'},
#  ]

def home(request):
    rooms = Room.objects.all()
    context = {'rooms' : rooms}
    return render(request, 'base/home.html', context)

def room(request, pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, "base/room.html", context)


#CRUD Operations ----Room---

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

def UpdateRoom(request, pk):
    
    room = Room.objects.get(id=pk) #Get a specific room with primary key (pk)
    form = RoomForm(instance=room) #Set the form data equal to the room data (pk)

    #If the form is submitted redirect to home
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    #Direct user to form page with form data
    context = {'form': form}
    return render(request, "base/room_form.html", context)

def DeleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})  
