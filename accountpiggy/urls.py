from . import views
from django.urls import path

app_name = 'accountpiggy'
urlpatterns = [
    path('',views.main_page,name='main_page'),
    path('room/create/',views.room_create_page, name='room_create_page'),
    path('room/search/', views.room_search_page, name='room_search_page'),
    path('room/reception/<int:room_id>/',views.room_reception_page, name='room_reception_page'),
    path('room/expenses/<int:room_id>/', views.room_expenses_page, name='room_expenses_page'),
    path('room/expense/add/<int:room_id>/', views.room_expense_add_page, name='room_expense_add_page'),
    path('room/expense/delete/<int:room_id>/', views.room_expense_delete, name='room_expense_delete'),
    path('room/expense/cleanup/<int:room_id>/', views.room_expense_cleanup_page, name='room_expense_cleanup_page'),
    path('room/info/<int:room_id>/', views.room_info_page, name='room_info_page'),
    path('room/admin/dummy/edit/<int:room_id>/', views.room_dummy_edit, name='room_dummy_edit'),
    path('room/admin/dummy/delete/<int:room_id>/', views.room_dummy_delete, name='room_dummy_delete'),
    path('room/admin/banuser/<int:room_id>/', views.room_admin_ban_user, name='room_admin_ban_user'),
    path('test/', views.test_page, name='test_page'),
]