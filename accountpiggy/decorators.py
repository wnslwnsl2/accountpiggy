from .models import Room,Member
from django.shortcuts import render,reverse
from django.http import HttpResponseRedirect

def membership_required(function):
    def wrapper(*args,**kwargs):
        request = args[0]
        room_id = kwargs['room_id']
        if Member.objects.filter(room=room_id,user=request.user).exists():
            return function(*args,**kwargs)
        return HttpResponseRedirect(reverse('accountpiggy:room_reception_page',kwargs={'room_id':room_id}))
    return wrapper