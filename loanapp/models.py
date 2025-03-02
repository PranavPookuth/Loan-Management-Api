from decimal import Decimal
from django.db import models
from user.models import User
import uuid
# Create your models here.

class Loan(models.Model):
    loan_id = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2)
    total_interest = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_remaining = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=[('ACTIVE', 'Active'), ('CLOSED', 'Closed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.loan_id:
            self.loan_id = f"LOAN{uuid.uuid4().hex[:6].upper()}"  # Unique Loan ID
        super().save(*args, **kwargs)

    def foreclose(self):
        """Handles loan foreclosure (early loan settlement)."""
        if self.status == "CLOSED":
            return {"message": "Loan is already foreclosed."}

        # Calculate remaining balance with early foreclosure
        remaining_interest = self.total_amount - self.amount_paid
        foreclosure_discount = remaining_interest * Decimal(0.1)  # Example: 10% discount
        final_settlement_amount = remaining_interest - foreclosure_discount

        # Update loan status
        self.amount_paid = self.total_amount
        self.amount_remaining = 0
        self.status = "CLOSED"
        self.save()

        return {
            "foreclosure_discount": round(foreclosure_discount, 2),
            "final_settlement_amount": round(final_settlement_amount, 2),
        }

