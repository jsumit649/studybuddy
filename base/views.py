from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


# Create your views here.

# rooms = [
#     {'id': 1, 'name': "Let's learn Python!"},
#     {'id': 2, 'name': 'Design with Figma'},
#     {'id': 3, 'name': 'Frontend Developers'},
#     {'id': 4, 'name': 'Backend Developers'},
# ]


# Handles user login functionality
def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("Password")

        if not email or not password:
            messages.error(request, "Both username and password are required")
            context = {'page': page}
            return render(request, "base/login_register.html", context)

        email = email.lower()
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Email OR Password doesn't exist")

    context = {'page' : page}
    return render(request, "base/login_register.html", context)


# Handles user logout functionality
def logoutUser(request):
    logout(request)
    return redirect("home")

def registerPage(request):
    form = MyUserCreationForm()

    if request.method =='POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render (request, 'base/login_register.html', {'form': form})


# Renders the home page with a list of rooms, topics, and room count
def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {"rooms": rooms, "topics": topics, "room_count": room_count, 'room_messages': room_messages}
    return render(request, "base/home.html", context)  # Render the home page template


# Renders a specific room page based on room id (pk)
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {"room": room, 'room_messages' : room_messages, 'participants': participants}  # Prepare context with the room data

    return render(request, "base/room.html", context)  # Render the room page template


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms' : rooms, 'room_messages' : room_messages, 'topics' : topics}
    return render(request,'base/profile.html', context)


# Allows logged-in users to create a new room
@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        room.participants.add(request.user)  # Add host as participant
        return redirect("home")
    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


# Allows logged-in users to update an existing room
@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return  HttpResponse("You're not allowed here")

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')    
        room.topic = topic
        room.description = request.POST.get('description')  
        room.save()
        return redirect("home")
    context = {"form": form, "topics": topics,"room": room}
    return render(request, "base/room_form.html", context)


# Allows logged-in users to delete a room
@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return  HttpResponse("You're not allowed here")
    
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"OBJ": Room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return  HttpResponse("You're not allowed to do that..")
    
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"OBJ": message})

@login_required(login_url='login')
def updateUser(request):
    user= request.user
    form = UserForm(instance=user)

    if request.method =='POST':
        form =UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form':form})

def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html',{'room_messages': room_messages})