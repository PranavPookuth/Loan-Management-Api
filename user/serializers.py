from django.core.mail import send_mail
from .models import *
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email','mobile_number']

    def validate_email(self, value):
        """
        Check if the email is already registered and verified.
        """
        try:
            user = User.objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("User with this email is already verified.")
            else:
                # Allow OTP regeneration for unverified users
                self.context['existing_user'] = user
        except User.DoesNotExist:
            pass
        return value

    def create(self, validated_data):
        email = validated_data.get('email')  # Ensure email is extracted
        username = validated_data.get('username')


        if 'existing_user' in self.context:
            user = self.context['existing_user']
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()

            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'pranavpookuth@gmail.com',
                [user.email]
            )
            return user
        else:
            otp = str(random.randint(100000, 999999))
            user = User.objects.create_user(
                username=username,
                email=email,  # Ensure email is passed correctly
                otp=otp,
                otp_generated_at=timezone.now(),
                is_active=False
            )
            user.save()

            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'pranavpookuth@gmail.com',
                [user.email]
            )

            return user


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)

            # Log OTP timestamp for debugging
            print(f"User OTP Generated At: {user.otp_generated_at}, Current Time: {now()}")

            # if user.is_otp_expired():
            #     raise serializers.ValidationError("OTP has expired. Please request a new OTP.")

            if user.otp != otp:
                raise serializers.ValidationError("Invalid OTP. Please enter the correct OTP.")

            # If OTP is correct, verify the user
            user.otp = None
            user.otp_generated_at = None
            user.is_verified = True
            user.is_active = True
            user.save()

        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email.")

        return data


class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError("This account is not active. Please contact support.")
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email.")

        # Generate a new OTP for the user every time they request it
        otp = random.randint(100000, 999999)  # Generate a new 6-digit OTP
        user.otp = str(otp)
        user.otp_generated_at = timezone.now()  # Optionally store the timestamp of the OTP generation
        user.save()

        # Send OTP via email
        send_mail(
            'OTP Verification',
            f'Your OTP is {otp}',
            'pranavpookuth@gmail.com',
            [user.email]
        )

        return value

class VerifyOTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
