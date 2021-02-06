from . import views
from django.urls import path

app_name = 'accountpiggy'
urlpatterns = [
    path('',views.main_page,name='main_page'),
    path('room/create/',views.room_create_page, name='room_create_page'),
    path('room/search/', views.room_search_page, name='room_search_page'),
    path('room/reception/<int:room_id>',views.room_reception_page, name='room_reception_page'),
    path('room/expenses/<int:room_id>', views.room_expenses_page, name='room_expenses_page'),
    path('room/expense/add/<int:room_id>', views.room_expense_add_page, name='room_expense_add_page'),
    path('room/cleanup/<int:room_id>', views.room_cleanup_page, name='room_cleanup_page'),
    path('room/info/<int:room_id>', views.room_info_page, name='room_info_page'),
]