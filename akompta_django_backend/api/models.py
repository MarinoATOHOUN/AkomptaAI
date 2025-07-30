from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default="fr")
    
    def __str__(self):
        return self.username

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    min_stock_threshold = models.IntegerField(default=5)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="sales")
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default="cash")
    notes = models.TextField(blank=True, null=True)
    voice_command = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name if self.product else 'N/A'}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, default="autres")
    expense_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default="cash")
    receipt_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    voice_command = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.description} - {self.amount} FCFA"

class Savings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="savings_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # "deposit" or "withdrawal"
    transaction_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default="mobile_money")
    mobile_money_provider = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default="pending") # "pending", "completed", "failed"
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.user.username}"

class StockMovement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stock_movements")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    movement_type = models.CharField(max_length=20)  # "in" or "out"
    quantity = models.IntegerField()
    movement_date = models.DateTimeField(auto_now_add=True)
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reason = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    reference_id = models.IntegerField(blank=True, null=True) # ID of related sale/expense
    voice_command = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.movement_type} {self.quantity} of {self.product.name}"

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    report_type = models.CharField(max_length=50) # "daily", "weekly", "monthly", "annual"
    report_period_start = models.DateTimeField()
    report_period_end = models.DateTimeField()
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"Report {self.report_type} for {self.user.username}"


