from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from .utils import getCodeJson, findCodeJson

from .models import Room, Message
# Create your views here.


@login_required
def roomsPage(request):
    rooms = Room.objects.all()
    # print(rooms)
    # context = getCodeJson()
    # findCodeJson("python")
    return render(request, "room/roomsPage.html", {'rooms':rooms})

@login_required
def chatroomPage(request, slug):
    room = Room.objects.get(slug = slug)
    messages = Message.objects.filter(room=room)
    data={'room': room, 'messages':messages}
    return render(request, "room/chatroomPage.html", data)
