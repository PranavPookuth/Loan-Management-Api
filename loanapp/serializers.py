import datetime
import random

from rest_framework import serializers
from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    payment_schedule = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'amount', 'tenure', 'interest_rate', 'monthly_installment',
                  'total_interest', 'total_amount', 'payment_schedule']
        read_only_fields = ['loan_id', 'monthly_installment', 'total_interest',
                            'total_amount', 'payment_schedule']

    def get_payment_schedule(self, obj):
        """Generate a list of monthly installment payments with due dates"""
        payment_schedule = []
        due_date = datetime.date.today()  # Start from today

        for i in range(1, obj.tenure + 1):
            due_date += datetime.timedelta(days=30)  #
            payment_schedule.append({
                "installment_no": i,
                "due_date": due_date.strftime("%Y-%m-%d"),
                "amount": round(obj.monthly_installment, 2)
            })

        return payment_schedule

    def create(self, validated_data):
        # Assign user from request
        validated_data['user'] = self.context['request'].user
        # Generate unique Loan ID
        validated_data['loan_id'] = f"LOAN{random.randint(1000, 9999)}"

        # Extract loan details
        amount = validated_data.get("amount")
        tenure = validated_data.get("tenure")
        interest_rate = validated_data.get("interest_rate") / 100  # Convert percentage to decimal

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
