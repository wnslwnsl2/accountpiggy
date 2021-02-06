from .forms import RoomCreateForm,ExpenseCreateForm
from .models import Room,Expense
from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.http import HttpResponse,HttpResponseRedirect

# Create your views here.
def main_page(request):
    context={}
    if request.user.is_authenticated:
        context['rooms'] = request.user.participating_room_list.all()
    return render(request,'accountpiggy/main_page.html',context)

def room_create_page(request):
    if request.method == "POST":
        form = RoomCreateForm(request.POST)
        if form.is_valid():
            room = form.save()
            room.users.add(request.user)
            room.save()
            return redirect('/')
    else:
        form = RoomCreateForm()
    context = {'form':form}
    return render(request,'accountpiggy/room_create_page.html',context)

def room_search_page(request):
    context ={}
    if 'name' in request.GET:
        query = request.GET['name']
        context['rooms'] = Room.objects.filter(name__contains=query).all()
    return render(request,'accountpiggy/room_search_page.html',context)

def room_reception_page(request,room_id):
    context = {}
    room = get_object_or_404(Room,id=room_id)

    if request.method == "POST":
        if request.POST['codeword']=='고구마':
            room.users.add(request.user)
            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    if room.isMember(request.user):
        return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    context['room']=room
    return render(request,'accountpiggy/room_reception_page.html',context)

def room_expenses_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room
    context['expense_list'] = Expense.manager.expenses_in_room(room=room)
    return render(request, 'accountpiggy/room_expenses_page.html', context)

def room_expense_add_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    form = ExpenseCreateForm()

    if request.method == "POST":
        form = ExpenseCreateForm(request.POST)

        if form.is_valid:
            Expense.manager.CreateExpense(form=form,room=room,spend_user=request.user)
            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    form.fields['users'].queryset = room.users
    context['room'] = room
    context['form'] = form
    return render(request, 'accountpiggy/room_expense_add_page.html', context)

def room_cleanup_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room
    return render(request, 'accountpiggy/room_cleanup_page.html', context)

def room_info_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room
    return render(request, 'accountpiggy/room_info_page.html', context)