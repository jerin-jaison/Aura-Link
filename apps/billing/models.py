"""
Billing models (Phase 2 stub).
"""

from django.db import models
from django.conf import settings


class Invoice(models.Model):
    """Invoice model for future payment integration."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoices'


class Transaction(models.Model):
    """Payment transaction record."""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    gateway = models.CharField(max_length=50)  # stripe, razorpay, etc.
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'