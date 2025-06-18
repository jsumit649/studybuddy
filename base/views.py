from django.shortcuts import render

# Create your views here.

rooms = [
    {'id': 1, 'name': "Let's learn Python!"},
    {'id': 2, 'name': 'Design with Figma'},
    {'id': 3, 'name': 'Frontend Developers'},
    {'id': 4, 'name': 'Backend Developers'},
]

def home(request):
    context =  {"rooms": rooms}
    return render(request, 'base/home.html', context)  # Render the home page template

def room(request, pk): 
    room = None
    for i in rooms:
        if i['id'] == int(pk):
            room = i
    context = {'room': room}  # Prepare context with the room data

    return render(request, 'base/room.html', context)  # Render the room page template