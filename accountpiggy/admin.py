from django.contrib import admin
from .models import Room,Expense

# Register your models here.

class AdminRoom(admin.ModelAdmin):
    list_display = ("name","max_number_of_members","start_date","end_date")
    ordering = ("id",)
    search_fields = ("name",)

class AdminExpense(admin.ModelAdmin):
    list_display = ("datetime","purpose",)
    ordering = ("datetime",)
    search_fields = ("spend_user",)

# Register your models here.
admin.site.register(Room,AdminRoom,)
admin.site.register(Expense,AdminExpense)