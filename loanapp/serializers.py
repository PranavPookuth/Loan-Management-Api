import datetime
import random
from rest_framework import serializers
from .models import Loan

class LoanSerializer(serializers.ModelSerializer):
    payment_schedule = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['id', 'loan_id', 'amount', 'tenure', 'interest_rate', 'monthly_installment',
                  'total_interest', 'total_amount', 'payment_schedule']
        read_only_fields = ['loan_id', 'monthly_installment', 'total_interest',
                            'total_amount', 'payment_schedule']

    def validate_amount(self, value):
        """Validate loan amount (₹1,000 - ₹100,000)."""
        if value < 1000 or value > 100000:
            raise serializers.ValidationError("Loan amount must be between ₹1,000 and ₹100,000.")
        return value

    def validate_tenure(self, value):
        """Validate loan tenure (3 - 24 months)."""
        if value < 3 or value > 24:
            raise serializers.ValidationError("Tenure must be between 3 and 24 months.")
        if not isinstance(value, int):
            raise serializers.ValidationError("Tenure must be a whole number.")
        return value

    def get_payment_schedule(self, obj):
        """Generate a list of monthly installment payments with due dates"""
        payment_schedule = []
        due_date = datetime.date.today()

        for i in range(1, obj.tenure + 1):
            due_date += datetime.timedelta(days=30)
            payment_schedule.append({
                "installment_no": i,
                "due_date": due_date.strftime("%Y-%m-%d"),
                "amount": round(obj.monthly_installment, 2)
            })

        return payment_schedule

    def create(self, validated_data):
        # Assign user from request
        validated_data['user'] = self.context['request'].user

        # Extract loan details
        amount = validated_data.get("amount")
        tenure = validated_data.get("tenure")
        interest_rate = validated_data.get("interest_rate") / 100  

        # **Loan Calculation (Monthly Compound Interest)**
        monthly_rate = interest_rate / 12
        total_interest = amount * ((1 + monthly_rate) ** tenure - 1)
        total_amount = amount + total_interest
        monthly_installment = total_amount / tenure

        # Set calculated values
        validated_data['monthly_installment'] = round(monthly_installment, 2)
        validated_data['total_interest'] = round(total_interest, 2)
        validated_data['total_amount'] = round(total_amount, 2)

        return super().create(validated_data)



class LoanForeclosureSerializer(serializers.Serializer):
    loan_id = serializers.CharField()
