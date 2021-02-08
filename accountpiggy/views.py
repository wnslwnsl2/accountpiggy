from .forms import RoomCreateForm,ExpenseCreateForm,NameForm,CleanedPageUserSelectForm
from .models import Room,Expense,IndexedUser, ExpenseMatrix, ExpenseMatrixEntry
from accounts.models import User
from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.http import HttpResponse,HttpResponseRedirect

## main_page
def test_page(request):
    context = {}

    if request.method=='POST':
        form = NameForm(request.POST)
        if form.is_valid():
            context['name'] = form.cleaned_data['name']
    else:
        form = NameForm()

    context['form'] = form
    return render(request,'accountpiggy/test_page.html',context)
# 방 찾기, 방 만들기 버튼 제공
# 본인이 속한 방 list 보여줌
def main_page(request):
    context={}
    if request.user.is_authenticated:
        # user가 속한 방 보여주기
        # indexed_set을 불러옴, indexed_user.room으로 room 배열 만들어 줌
        indexed_user_set = request.user.indexed_set
        context['rooms'] = [indexed_user.room for indexed_user in indexed_user_set.all()]
    return render(request,'accountpiggy/main_page.html',context)

def room_create_page(request):
    if request.method == "POST":
        form = RoomCreateForm(request.POST)
        if form.is_valid():
            room = form.save()
            # IndexedUser로 방장을 room에 연결 시킨다.
            adminUser = IndexedUser.objects.create(user=request.user,room=room,index=room.get_next_index(),is_admin=True)
            adminUser.save()
            matrix = ExpenseMatrix.objects.create(room=room)
            matrix.save()
            return HttpResponseRedirect(reverse(viewname="accountpiggy:room_reception_page",kwargs={'room_id':room.id}))
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
            # 사용자를 방에 연결시켜줌
            participantUser = IndexedUser.objects.create(user=request.user, room=room, index=room.get_next_index(), is_admin=False)
            participantUser.save()
            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    # 사용자가 방에 있는지 확인하고 있으면, expenses_page로 이동할 수 있게 해줌
    if IndexedUser.objects.filter(room=room,user=request.user).exists():
        return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    context['room']=room
    return render(request,'accountpiggy/room_reception_page.html',context)

def room_expenses_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room
    context['expense_list'] = Expense.objects.expenses_in_room(room=room).order_by('-datetime')
    return render(request, 'accountpiggy/room_expenses_page.html', context)

def room_expense_add_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    form = ExpenseCreateForm()
    # 방장일 때만 돈을 쓴 사람을 입력할 수 있게 하고 싶다.
    # template에서 form을 좀 더 세분화 해서 사용하고 싶다.
    indexedUser = IndexedUser.objects.get(room=room, user=request.user)

    if request.method == "POST":
        form = ExpenseCreateForm(request.POST)
        if indexedUser.is_admin:
            form.fields['expend_user'].required = True
        else:
            form.fields['expend_user'].required = False

        if form.is_valid():
            #방장만 expend_user를 선택할 수 있음
            if indexedUser.is_admin:
                Expense.objects.CreateExpense(form=form,room=room,indexed_user=form.cleaned_data['expend_user'])
            else:
                Expense.objects.CreateExpense(form=form,room=room,indexed_user=indexedUser)
            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    form.fields['users'].queryset = IndexedUser.objects.filter(room=room)
    form.fields['expend_user'].queryset = IndexedUser.objects.filter(room=room)
    context['room'] = room
    context['form'] = form
    context['is_admin'] = indexedUser.is_admin
    return render(request, 'accountpiggy/room_expense_add_page.html', context)

def room_expense_delete(request,room_id):
    context={}
    room = Room.objects.get(id=room_id)
    expense = Expense.objects.get(id=request.GET['expense_id'])
    expense.delete()
    return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

def room_expense_cleanup_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        form = CleanedPageUserSelectForm(request.POST)
        if form.is_valid():
            matrix = room.expensematrix
            matrix.cleanup(room)
            indexedUser = form.cleaned_data['selectedUser']
            print(indexedUser)
            context['send_item_list'] = ExpenseMatrixEntry.objects.filter(matrix=matrix, sender=indexedUser,
                                                                          is_cleaned_data=True, ).exclude(
                receiver=indexedUser).all()
            context['recv_item_list'] = ExpenseMatrixEntry.objects.filter(matrix=matrix, receiver=indexedUser,
                                                                          is_cleaned_data=True).exclude(
                sender=indexedUser).all()
    else:
        form = CleanedPageUserSelectForm()

    form.fields['selectedUser'].queryset = IndexedUser.objects.filter(room=room)
    context['room'] = room
    context['form'] = form
    return render(request, 'accountpiggy/room_expense_cleanup_page.html', context)

def room_info_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST" and 'adddummy' in request.POST:
        IndexedUser.objects.create(room=room,user=User.objects.get_or_create_dummyuser(),index=room.get_next_index(),is_admin=False)

    indexed_user = IndexedUser.objects.get(user=request.user,room=room)

    context['room'] = room
    context['users'] = room.users.all().order_by('index')
    context['is_admin'] = indexed_user.is_admin
    return render(request, 'accountpiggy/room_info_page.html', context)

def room_dummy_edit(request,room_id):
    context ={}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room
    if request.method == "GET":
        user_id = request.GET['user_id']
        index = request.GET['index']
        context['user_id'] = user_id
        context['index'] = index

        indexed_user = IndexedUser.objects.get(room=room,user=user_id,index=index)
        context['nickname']=indexed_user.nickname

        if 'changed_nickname' in request.GET:
            indexed_user.nickname = request.GET['changed_nickname']
            indexed_user.save()
            return HttpResponseRedirect(reverse('accountpiggy:room_info_page',kwargs={'room_id':room_id}))

    return render(request,'accountpiggy/room_dummy_edit.html',context)

def room_dummy_delete(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room

    if request.method == "GET":
        user = IndexedUser.objects.get(
            room=room,
            user=request.GET['user_id'],
            index=request.GET['index'],
        )
        user.delete()
        return HttpResponseRedirect(reverse('accountpiggy:room_info_page',kwargs={'room_id':room_id}))

def room_admin_ban_user(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room

    if request.method == "GET":
        user = IndexedUser.objects.get(
            room=room,
            user=request.GET['user_id'],
            index=request.GET['index'],
        )
        user.delete()
        return HttpResponseRedirect(reverse('accountpiggy:room_info_page',kwargs={'room_id':room_id}))