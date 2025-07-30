from django.contrib import admin
from api.models import User, Product, Sale, Expense, Savings, StockMovement, Report
# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(Expense)
admin.site.register(Savings)
admin.site.register(StockMovement)
admin.site.register(Report)
