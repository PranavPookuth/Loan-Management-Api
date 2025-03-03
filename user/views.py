from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from .models import *
from .serializers import *


# Create your views here.
class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists. Please choose a different username.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                return Response({'error': 'User with this email is already verified.'},
                                status=status.HTTP_400_BAD_REQUEST)

                # Send the new OTP to the user's email
                send_mail(
                    'OTP Verification',
                    f'Your new OTP is {otp}',
                    'pranavpookuth.com',
                    [user.email]
                )

                return Response({'message': 'A new OTP has been sent to your email. Please verify your OTP.'},
                                status=status.HTTP_200_OK)

            return Response({'message': 'OTP already sent. Please verify your OTP.'},
                            status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # If the user does not exist, create a new user
            otp = random.randint(100000, 999999)
            user = User.objects.create_user(
                username=username,
                email=email,
                otp=otp,
                otp_generated_at=timezone.now()
            )

            send_mail(
                'OTP Verification',
                f'Your new OTP is {otp}',
                'pranavpookuth@gmail.com',
                [user.email]
            )

            return Response({"message": "User registered successfully. OTP sent."}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Email verified successfully! You can now log in.'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []  # No authentication required for OTP login

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                user = User.objects.get(email=email)

                # Debugging logs
                print(f"User OTP: {user.otp}, Entered OTP: {otp}")
                print(f"OTP Generated At: {user.otp_generated_at}, Current Time: {now()}")


                # Check if OTP is correct
                if user.otp != otp:
                    return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

                # If OTP is correct, mark user as verified
                user.is_verified = True
                user.otp = None  # Reset OTP after successful login
                user.otp_generated_at = None
                user.save()

                # Generate JWT token
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Return user details and JWT token
                return Response({
                    "message": "Login successful",
                    "user": {
                        "email": user.email,
                        "is_verified": user.is_verified,
                    },
                    "access_token": access_token,
                    # "refresh_token": str(refresh),  # Uncomment if refresh token is needed
                }, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserlistView(generics.ListAPIView):
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserListSerializer

