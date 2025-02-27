from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Loan
from .serializers import LoanSerializer, LoanForeclosureSerializer

# Create your views here.

class LoanListCreateView(generics.ListCreateAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LoanRetrieveView(generics.RetrieveAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)


class LoanForeclosureView(generics.GenericAPIView):
    serializer_class = LoanForeclosureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            loan_id = serializer.validated_data["loan_id"]
            try:
                loan = Loan.objects.get(loan_id=loan_id, user=request.user)
                if loan.status == "CLOSED":
                    return Response({"message": "Loan is already foreclosed."}, status=status.HTTP_400_BAD_REQUEST)

                result = loan.foreclose()
                return Response({
                    "status": "success",
                    "message": "Loan foreclosed successfully.",
                    "data": {
                        "loan_id": loan.loan_id,
                        "amount_paid": loan.amount_paid,
                        "foreclosure_discount": result["foreclosure_discount"],
                        "final_settlement_amount": result["final_settlement_amount"],
                        "status": loan.status,
                    }
                }, status=status.HTTP_200_OK)
            except Loan.DoesNotExist:
                return Response({"message": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
