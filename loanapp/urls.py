from django.urls import path
from .views import *

urlpatterns = [
    path("loans/", LoanListCreateView.as_view(), name="loan-list-create"),
    path("loans/<int:pk>/", LoanRetrieveView.as_view(), name="loan-retrieve"),
    path("loans/foreclose/", LoanForeclosureView.as_view(), name="loan-foreclose"),
]
