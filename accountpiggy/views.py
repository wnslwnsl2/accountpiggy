from .forms import RoomCreateForm,ExpenseCreateForm,NameForm,CleanedPageUserSelectForm
from . import models
from .models import Room,Expense,Member, ExpenseMatrix, ExpenseMatrixEntry
from accounts.models import User
from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.http import HttpResponse,HttpResponseRedirect

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
def room_create_page(request):
    """
        Room.objects.create_room
            1) room 생성
            2) user - room 연결
            3) matrix 생성
    """
    if request.method == "POST":
        form = RoomCreateForm(request.POST)
        if form.is_valid():
            room = Room.objects.create_room(form,request.user)
            return HttpResponseRedirect(reverse(viewname="accountpiggy:room_reception_page",kwargs={'room_id':room.id}))
    else:
        form = RoomCreateForm()
    context = {'form':form}
    return render(request,'accountpiggy/room_create_page.html',context)


"""
    방 찾기
    ========

    설명:
        GET으로 검색어 가져와서 방 찾는다
"""
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
def room_reception_page(request,room_id):
    """
        TODO 방 코드만들기
            1) 방 생성시 방 코드 생성 알고리즘 검색 > room에서 코드 관리
            2) 리셉션에서 room 질문코드를 context로 내보냄
            3) POST['codeword']와 답변 코드를 비교함
        TODO 방 접근 권한 설정하기
    """
    context = {}
    room = get_object_or_404(Room,id=room_id)

    # 사용자가 방에 있는지 확인하고 있으면, expenses_page로 이동할 수 있게 해줌
    if Member.objects.filter(room=room, user=request.user).exists():
        return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    if request.method == "POST":
        if request.POST['codeword']=='고구마':
            # 사용자를 방에 연결시켜줌 (IndexedUser 만들기)
            # TODO user.indexedUser 기능
            participantUser = Member.objects.create(user=request.user, room=room, index=room.get_next_index(), is_admin=False)
            participantUser.save()
            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

    context['room']=room
    return render(request,'accountpiggy/room_reception_page.html',context)

"""
지출 내역 정보
============

사용자의 지출내역을 보여준다. 
"""
def room_expenses_page(request,room_id):
    """
        TODO
            사용자의 지출내역을 일자별로 정렬하여 보여준다.
            일자 별로 정렬하여 보여주는 클래스를 만들어서 사용해야 할 듯
            ExpensesInDay
            - day
            - expenses
        TODO 추가하기 & 정산하기 한페이지에서 이뤄지도록
    """
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room
    context['expense_list'] = Expense.objects.expenses_in_room(room=room).order_by('-datetime')
    return render(request, 'accountpiggy/room_expenses_page.html', context)

"""
추가하기
=======

지출 내역을 추가하는 페이지

특이:
    현재, 방장만 돈 쓴자를 선택할 수 있게 해두었다.
"""
def room_expense_save_page(request,room_id):
    """
        TODO 돈쓴자 처음에 바로 방장 자신으로 선택되도록
        TODO 돈 보낸자 처음에 모두 선택되도록
        TODO 돈 보낸자 all 버튼, 내가 쏜다 버튼
        TODO 쓴시간 입력 date time 나누어 사용자가 쉽게 입력 할 수 있도록
        TODO expense save refactoring
    """
    context = {}
    room = get_object_or_404(Room, id=room_id)
    indexedUser = Member.objects.get(room=room, user=request.user)

    if request.method == "POST":
        expense_id = int(request.POST['expense_id'])
        form = ExpenseCreateForm(request.POST)

        # 방장만 expend_user를 선택할 수 있도록 한다.
        # 방장인지 여부에 따라서 expend_user 필드의 required를 설정함
        if indexedUser.is_admin:
            form.fields['expend_user'].required = True
        else:
            form.fields['expend_user'].required = False

        if form.is_valid():
            if expense_id==-1:
                if indexedUser.is_admin:
                    spend_user = form.cleaned_data['expend_user']
                else:
                    spend_user = indexedUser
                Expense.objects.CreateExpense(form=form,room=room,indexed_user=spend_user)
            else:
                expense = Expense.objects.get(id=expense_id)
                expense.expend_user = form.cleaned_data['expend_user']
                expense.users.set(form.cleaned_data['users'].all())
                expense.cost = form.cleaned_data['cost']
                expense.purpose = form.cleaned_data['purpose']
                expense.purpose_category = form.cleaned_data['purpose_category']
                expense.datetime = form.cleaned_data['datetime']
                expense.save()
            # 추가 이체 할 경우
            # if "save_another" in  request.POST:
            #     expense_id=-1
            #     form = ExpenseCreateForm({
            #         'expend_user': form.cleaned_data['expend_user'],
            #         'users': form.cleaned_data['users'].all(),
            #     })
            # else:
            return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))
    elif 'expense_id' in request.GET:
        expense_id = request.GET['expense_id']
        expense = Expense.objects.get(id=expense_id)
        form = ExpenseCreateForm({
            'expend_user': expense.expend_user,
            'users': expense.users.all(),
            'cost': expense.cost,
            'purpose': expense.purpose,
            'purpose_category': expense.purpose_category,
            'datetime':expense.datetime,
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
    context['is_admin'] = indexedUser.is_admin
    return render(request, 'accountpiggy/room_expense_save_page.html', context)

"""
지출내역 삭제하기
===============
지출내역 id를 delete로 받아서 삭제를 하는데 이건 아닌듯
POST로 바꿔야 겠다.
"""
def room_expense_delete(request,room_id):
    """
        TODO delete할 expense_id POST로 받아오기
    """
    context={}
    room = Room.objects.get(id=room_id)
    expense = Expense.objects.get(id=request.GET['expense_id'])
    expense.delete()
    return HttpResponseRedirect(reverse('accountpiggy:room_expenses_page',kwargs={'room_id':room_id}))

"""
정산하기 페이지
=============

정산 알고리즘을 실행하고 정산 내역을 보여줌
"""
def room_expense_cleanup_page(request,room_id):
    """
        TODO 정산이 필요할 때만 정산을 진행하도록 변경
        TODO CleanedPageUserSelectForm은 GET으로 받아오는게 좋다.
        TODO 보냈다 받았다 기능
    """
    context = {}
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        form = CleanedPageUserSelectForm(request.POST)
        if form.is_valid():
            matrix = room.expensematrix
            matrix.cleanup(room) # 정산 알고리즘 실행

            indexedUser = form.cleaned_data['selectedUser']

            context['send_item_list'] = matrix.send_item_list(indexedUser)
            context['recv_item_list'] = matrix.recv_item_list(indexedUser)
            context['selfexpense'] = matrix.self_expense(indexedUser)
            totalexpense = realexpense = 0

            for entry in context['send_item_list']:
                realexpense += entry.value
            for entry in context['recv_item_list']:
                totalexpense += entry.value
            context['totalexpense'] = totalexpense + context['selfexpense']
            context['realexpense'] = realexpense + context['selfexpense']
    else:
        form = CleanedPageUserSelectForm()

    form.fields['selectedUser'].queryset = Member.objects.filter(room=room)
    context['room'] = room
    context['form'] = form
    return render(request, 'accountpiggy/room_expense_cleanup_page.html', context)

"""
방 정보 페이지
============

1. 방 정보를 볼 수 있는 페이지
2. 방장은 이곳에서 더미를 관리할 수 있다.
"""
def room_info_page(request,room_id):
    """
        TODO 사용자 - dummy 연결
        TODO dummy 삭제하고나서 사이에 비어있는 index 채우는 것
    """
    context = {}
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST" and 'adddummy' in request.POST:
        Member.objects.create(room=room, user=User.dummy.all(), index=room.get_next_index(), is_admin=False)

    indexed_user = Member.objects.get(user=request.user, room=room)

    context['room'] = room
    context['indexed_user'] = indexed_user
    context['users'] = room.users.all().order_by('index')
    context['is_admin'] = indexed_user.is_admin
    qa = models.EnteringQA.objects.get(room=room)
    context['roomQ']=qa.Q
    context['roomA']=qa.A
    return render(request, 'accountpiggy/room_info_page.html', context)

"""
nickname 변경
============

room 과 index를 통해 유저의 nickname 변경한다
"""
def room_member_edit(request,room_id):
    """
        TODO 처음 페이지 들어올 때 닉네임 설정도 동일한 method로 사용할 수 있도록
        TODO 닉네임 추천 알고리즘 구현 or 검색
    """
    context ={}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room

    if request.method == "POST":
        index = request.POST['index']
        form = NameForm(request.POST)

        if form.is_valid():
            indexed_user = Member.objects.get(room=room, index=index)
            indexed_user.nickname = form.cleaned_data['name']
            indexed_user.save()
            return HttpResponseRedirect(reverse('accountpiggy:room_info_page',kwargs={'room_id':room_id}))
        else:
            # 정보가 올바르지 않으면 get으로 디리렉션 시킴
            return HttpResponseRedirect('{}?index={}'.format(reverse('accountpiggy:room_member_edit',kwargs={'room_id':room_id}),index))
    else:
        form = NameForm()
        index = request.GET['index']
        indexed_user = Member.objects.get(room=room, index=index)
        form.name = indexed_user.nickname

    context['index'] = index
    context['form'] = form
    return render(request,'accountpiggy/room_member_edit.html',context)

"""
방 멤버 삭제
===========
"""
def room_member_delete(request,room_id):
    """
        TODO (Ajax) POST로 바꿔줘야 됨 > POST로 바꿔주면 버튼(submit) 배치를 어떻게 해야할 지 난감함 > javascript html을 조금 더 하고 진행하자
        TODO 삭제하고 나서 INDEX 재조정 알고리즘 작성
    """
    context = {}
    room = get_object_or_404(Room, id=room_id)
    context['room'] = room

    if request.method == "GET":
        user = Member.objects.get(
            room=room,
            index=request.GET['index'],
        )
        user.delete()
        return HttpResponseRedirect(reverse('accountpiggy:room_info_page',kwargs={'room_id':room_id}))