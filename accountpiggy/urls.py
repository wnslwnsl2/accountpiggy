from . import views
from django.urls import path

app_name = 'accountpiggy'

urlpatterns = [
    path('test/',views.test,name='test'),
    path('',views.main_page,name='main_page'),

    # 방 만들기/ 찾기
    path('room/create/',views.room_create_page, name='room_create_page'),
    path('room/search/', views.room_search_page, name='room_search_page'),

    # 방 리셉션/ 방정보/ 지출 내역
    path('room/reception/<int:room_id>/',views.room_reception_page, name='room_reception_page'),
    path('room/info/<int:room_id>/', views.room_info_page, name='room_info_page'),
    path('room/expenses/<int:room_id>/', views.room_expenses_page, name='room_expenses_page'),
    path('room/info/edit/name/<int:room_id>/',views.room_name_edit,name='room_name_edit'),

    # 방 지출내역 추가/삭제/정산
    path('room/expense/cleanup/<int:room_id>/', views.room_expense_cleanup_page, name='room_expense_cleanup_page'),
    path('room/expense/save/<int:room_id>/', views.room_expense_save_page, name='room_expense_save_page'),
    path('room/expense/delete/<int:room_id>/', views.room_expense_delete, name='room_expense_delete'),

    path('room/expense/transfer_receiver_communication/<int:room_id>/',views.transfer_receiver_communication,name='transfer_receiver_communication'),
    path('room/expense/transfer_sender_communication/<int:room_id>/', views.transfer_sender_communication, name='transfer_sender_communication'),

    # room_admin_member
    path('room/member/edit/<int:room_id>/', views.room_member_edit, name='room_member_edit'),
    path('room/member/delete/<int:room_id>/', views.room_member_delete, name='room_member_delete'),
]