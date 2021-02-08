from django.contrib import admin
from .models import Room,Expense,IndexedUser,ExpenseMatrix,ExpenseMatrixEntry

# Register your models here.

class AdminRoom(admin.ModelAdmin):
    list_display = ("name","start_date","end_date")
    ordering = ("id",)
    search_fields = ("name",)

class AdminExpense(admin.ModelAdmin):
    list_display = ("datetime","purpose",)
    ordering = ("datetime",)
    search_fields = ("spend_user",)

# Register your models here.
admin.site.register(IndexedUser)
admin.site.register(Room)
admin.site.register(Expense)
admin.site.register(ExpenseMatrix)
admin.site.register(ExpenseMatrixEntry)