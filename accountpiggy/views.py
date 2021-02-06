from .decorators import membership_required
from .forms import RoomSaveForm,ExpenseCreateForm,NameForm
from . import models
from .models import Room,Expense,Member, ExpenseMatrix, ExpenseMatrixEntry
from accounts.models import User
from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.utils import timezone
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

def test(request):
    return render(request,'accountpiggy/test.html')

"""
    메인
    ===
    
    설명:
        1) 방 찾기, 방 만들기 페이지로 이동
        2) home 역할
        3) user가 참여한 방 리스트 보여줌
"""
def main_page(request):
    """
    context:
        rooms: 내가 참여한 방 리스트
    """
    context={}
    if request.user.is_authenticated:
        # user가 참여한 방을 넘겨줌
        # print(request.user.rooms)
        context['rooms'] = request.user.rooms
    return render(request,'accountpiggy/main_page.html',context)

"""
방 만들기
========
    
설명:
    방 만들기
"""
@login_required
def room_create_page(request):
    ajax = 'ajax' in request.GET

    if 'room_id' in request.GET:
        room_id = request.GET['room_id']
    else:
        room_id = -1

    if request.method == "POST":
        form = RoomSaveForm(request.POST)

        if form.is_valid():
            #1) 방을 만든다.
            room,created = form.save_or_create(room_id)
            #2) 방장을 넣는다.
            room.accept_user(request.user,True)

            if ajax:
                return ""
            else:
                return HttpResponseRedirect(
                    reverse(viewname="accountpiggy:room_reception_page", kwargs={'room_id': room.id}))
        else:
            return form.errors
    else:
        if ajax:
            form = RoomSaveForm(instance=Room.objects.get(id=room_id))
        else:
            form = RoomSaveForm()

    context = {'form': form}
    return render(request, 'accountpiggy/room_create_page.html', context)

"""
    방 찾기
    ========

    설명:
        GET으로 검색어 가져와서 방 찾는다
"""
@login_required
def room_search_page(request):
    """
        Point
            검색어가 방정보 name에 포함되면 검색한다. > name_contains
    """
    context ={}
    if 'name' in request.GET:
        query = request.GET['name']
        context['rooms'] = Room.objects.filter(name__contains=query).all()
    return render(request,'accountpiggy/room_search_page.html',context)

"""
방 리셉션
========

설명:
    1) user가 방에 포함되었으면 방 내역 페이지(room_expenses_page)로 redirect한다.
    2) user가 방에 포함되지 않았으면 방 코드를 입력하는 창(리셉션)을 보여준다.
"""
@login_required
def room_reception_page(request,room_id):
    context = {}
    room = get_object_or_404(Room,id=room_id)

    # 사용자가 방에 있는지 확인하고 있으면, expenses_page로 이동할 수 있게 해줌
    if request.user in room:
        return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    if request.method == "POST":
        if room.QA.match_code(request.POST['codeword']):
            # 방 입장
            room.accept_user(request.user,False)
            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    context['room']=room
    return render(request,'accountpiggy/room_reception_page.html',context)



"""
지출 내역 정보
============

사용자의 지출내역을 보여준다. 
"""
@login_required
@membership_required
def room_expenses_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    all_expense_list = Expense.objects.expenses_in_room(room=room).order_by('-datetime')

    if len(all_expense_list)!=0:
        #
        last_date = timezone.localdate(all_expense_list[0].datetime)
        eids = []
        eid = models.ExpensesInDay(last_date)

        for expense in all_expense_list:
            # 날짜가 같으면 eid에 저장한다.
            if timezone.localdate(expense.datetime) == last_date:
                eid.add_expense(expense)
            else:
                # 날짜가 달라지면, eids에 eid를 저장한다.
                eids.append(eid)

                # last_date를 갱신한다.
                last_date=timezone.localdate(expense.datetime)
                # eid를 초기화한다.
                eid=models.ExpensesInDay(last_date)
                # 현재 expense를 넣어준다.
                eid.add_expense(expense)

        eids.append(eid)

        context['expense_in_day_list'] = eids
        #print(eids[0].date)
        context['expense_exist'] = True
    else:
        context['expense_exist'] = False

    context['room'] = room
    context['indexed_user'] = Member.objects.get(user=request.user, room=room)

    return render(request, 'accountpiggy/room_expenses_page.html', context)

"""
추가하기
=======

지출 내역을 추가하는 페이지

특이:
    현재, 방장만 돈 쓴자를 선택할 수 있게 해두었다.
    수정하기 위해 접근/생성하기 위해 접근 하는 것
    실제로 수정이 이루어지는 부분은 POST로 접근할 때 이루어져야 한다.
"""
@login_required
@membership_required
def room_expense_save_page(request,room_id):
    """
        TODO 돈쓴자 처음에 바로 방장 자신으로 선택되도록
        TODO 돈 보낸자 처음에 모두 선택되도록
        TODO 돈 보낸자 all 버튼, 내가 쏜다 버튼
    """
    context = {}
    room = get_object_or_404(Room, id=room_id)
    # 방장인지 알려고
    current_member = Member.objects.get(room=room, user=request.user)

    if request.method == "POST":
        # 아 수정..
        expense_id = int(request.POST['expense_id'])
        form = ExpenseCreateForm(request.POST)

        # 방장만 expend_user를 선택할 수 있도록 한다.
        # 방장인지 여부에 따라서 expend_user 필드의 required를 설정함
        if current_member.is_admin:
            form.fields['expend_user'].required = True
        else:
            form.fields['expend_user'].required = False

        if form.is_valid():
            if current_member.is_admin:
                spend_user = form.cleaned_data['expend_user']
            else:
                spend_user = current_member

            Expense.objects.create_or_save(expense_id,form=form,room=room,indexed_user=spend_user)

            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))
    elif 'expense_id' in request.GET:
        expense_id = request.GET['expense_id']
        expense = Expense.objects.get(id=expense_id)
        dt = timezone.localtime(expense.datetime)

        form = ExpenseCreateForm({
            'expend_user': expense.expend_user,
            'users': expense.users.all(),
            'cost': expense.cost,
            'purpose': expense.purpose,
            'purpose_category': expense.purpose_category,
            'date':dt.date(),
            'hour':dt.hour,
            'minute':dt.minute,
        })
    else:
        expense_id = -1
        form = ExpenseCreateForm()

    # field의 queryset을 room에 있는 유저로 한정한다.
    form.fields['users'].queryset = Member.objects.filter(room=room)
    form.fields['expend_user'].queryset = Member.objects.filter(room=room)
    context['expense_id'] = expense_id
    context['room'] = room
    context['form'] = form
    context['is_admin'] = current_member.is_admin
    return render(request, 'accountpiggy/room_expense_save_page.html', context)

"""
지출내역 삭제하기
===============
지출내역 id를 delete로 받아서 삭제를 하는데 이건 아닌듯
POST로 바꿔야 겠다.
"""
@login_required
@membership_required
def room_expense_delete(request,room_id):
    """
        TODO delete할 expense_id POST로 받아오기
    """
    context={}
    room = Room.objects.get(id=room_id)
    expense = Expense.objects.get(id=request.GET['expense_id'])
    expense.delete()
    room.matrix.needed_to_clean_up = True
    room.matrix.save()
    return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

"""
정산하기 페이지
=============

정산 알고리즘을 실행하고 정산 내역을 보여줌
"""
@login_required
@membership_required
def room_expense_cleanup_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)

    matrix = room.matrix
    matrix.cleanup(room)  # 정산 알고리즘 실행

    indexedUser = Member.objects.get(user=request.user,room=room)

    context['send_item_list'] = matrix.get_send_item_list(indexedUser)
    context['recv_item_list'] = matrix.get_recv_item_list(indexedUser)
    context['selfexpense'] = matrix.get_self_expense(indexedUser)
    total_members_expense = matrix.get_total_members_expense()

    now_date = timezone.localtime(timezone.now()).date()

    if now_date<room.start_date:
        current_travel_days = -1
    elif now_date>room.end_date:
        current_travel_days = (room.end_date-room.start_date).days+1
    else:
        current_travel_days = (now_date-room.start_date).days+1


    context['total_members_expense'] = total_members_expense
    context['current_travel_days'] = current_travel_days
    context['total_members_daily_expense'] =total_members_expense//current_travel_days

    sum_to_send = sum_to_recv = 0

    for entry in context['send_item_list']:
        sum_to_send += entry.value

    for entry in context['recv_item_list']:
        sum_to_recv += entry.value

    context['totalexpense'] = sum_to_recv + context['selfexpense']
    context['realexpense'] = sum_to_send + context['selfexpense']

    context['room'] = room

    # 그래프 요소
    foods = Expense.objects.filter(room=room,purpose_category='fo').all()
    context['expense_food'] = sum([food.cost for food in foods])

    sleeps = Expense.objects.filter(room=room,purpose_category='sl').all()
    context['expense_sleep'] = sum([sleep.cost for sleep in sleeps])

    drs = Expense.objects.filter(room=room,purpose_category='dr').all()
    context['expense_drink'] = sum([dr.cost for dr in drs])

    trs = Expense.objects.filter(room=room,purpose_category='tr').all()
    context['expense_transfer'] = sum([tr.cost for tr in trs])

    etcs = Expense.objects.filter(room=room,purpose_category='et').all()
    context['expense_etc'] = sum([etc.cost for etc in etcs])

    return render(request, 'accountpiggy/room_expense_cleanup_page.html', context)

"""
방 정보 페이지
============

1. 방 정보를 볼 수 있는 페이지
2. 방장은 이곳에서 더미를 관리할 수 있다.
"""
@login_required
@membership_required
def room_info_page(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST" and 'adddummy' in request.POST:
        dummy = User.dummy.all()
        dummyMemeber = room.accept_user(dummy)
        dummyMemeber.nickname = "이름을입력해주세요"
        dummyMemeber.save()

    current_member = room.get_member_instance_of_user(request.user)

    qa = room.QA

    context = {
        'room': room,
        'current_member':current_member,
        'members':room.members.all(),
        'is_admin': current_member.is_admin,
        'roomQ':qa.Q,
        'roomA':qa.A,
    }
    return render(request, 'accountpiggy/room_info_page.html', context)

"""
nickname 변경
============

room 과 index를 통해 유저의 nickname 변경한다
"""
@login_required
@membership_required
def room_member_edit(request,room_id):
    """
        TODO 처음 페이지 들어올 때 닉네임 설정도 동일한 method로 사용할 수 있도록
        TODO 닉네임 추천 알고리즘 구현 or 검색
    """
    room = get_object_or_404(Room, id=room_id)

    if 'member_id' in request.GET:
        member_id = request.GET['member_id']
    else:
        member_id = -1

    if request.method == "POST":
        form = NameForm(request.POST)

        if form.is_valid():
            member = Member.objects.get(id=member_id)
            member.change_nickname(form.cleaned_data['name'])
            return HttpResponseRedirect(reverse('accountpiggy:room_info_page',kwargs={'room_id':room_id}))
    else:
        form = NameForm()

    context ={
        'room':room,
        'form':form,
        'member_id':member_id
    }
    return render(request,'accountpiggy/room_member_edit.html',context)

"""
방 멤버 삭제
===========
"""
@login_required
@membership_required
def room_member_delete(request,room_id):
    """
        TODO (Ajax) POST로 바꿔줘야 됨 > POST로 바꿔주면 버튼(submit) 배치를 어떻게 해야할 지 난감함 > javascript html을 조금 더 하고 진행하자
    """
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room

    if request.method == "GET":
        member = Member.objects.get(id=request.GET['member_id'])
        if member.user.is_dummy():
            member.delete()
        else:
            member.user = User.dummy.all()
            member.save()
        return HttpResponseRedirect(reverse('accountpiggy:room_info_page',kwargs={'room_id':room_id}))

@csrf_exempt
@membership_required
def transfer_receiver_communication(request,room_id):
    entry = ExpenseMatrixEntry.objects.get(id=request.POST['entry_id'])
    if entry.state != 3:
        entry.state = 3
        entry.save()

    room = get_object_or_404(Room, id=room_id)
    matrix = room.matrix
    indexedUser = Member.objects.get(user=request.user,room=room)
    context = {
        'room':room,
        'send_item_list':matrix.get_send_item_list(indexedUser),
        'recv_item_list':matrix.get_recv_item_list(indexedUser),
    }
    return render(request,'accountpiggy/transfer_list.html',context)

@csrf_exempt
@membership_required
def transfer_sender_communication(request,room_id):
    entry = ExpenseMatrixEntry.objects.get(id=request.POST['entry_id'])

    if entry.state == 0 or entry.state == 2:
        entry.state = 1
        entry.save()

    room = get_object_or_404(Room, id=room_id)
    matrix = room.matrix
    indexedUser = Member.objects.get(user=request.user,room=room)
    context = {
        'room':room,
        'send_item_list':matrix.get_send_item_list(indexedUser),
        'recv_item_list':matrix.get_recv_item_list(indexedUser),
    }
    return render(request,'accountpiggy/transfer_list.html',context)

@csrf_exempt
def room_name_edit(request,room_id):
    input_room_name = request.POST['targetText']
    room = get_object_or_404(Room, id=room_id)

    if len(input_room_name)>0 or len(input_room_name)<=30:
        room = get_object_or_404(Room,id=room_id)
        room.name = input_room_name
        room.save()
        ret = input_room_name
    else:
        ret = room.name

    context={
        'text':ret,
        'is_editable':True,
        'targetURL':reverse('accountpiggy:room_name_edit',kwargs={'room_id':room_id})
    }
    return render(request,'accountpiggy/inline_edit.html',context)