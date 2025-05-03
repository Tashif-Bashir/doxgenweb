from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from .models import EmailOTP
import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect

def generate_otp(user):
    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})
    send_mail(
        subject='Your OTP Code',
        message=f'Your verification OTP is: {otp}',
        from_email='noreply@yourapp.com',
        recipient_list=[user.email]
    )


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        CustomUser = get_user_model()
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {'error': 'Email already exists'})

        user = CustomUser.objects.create_user(username=email, email=email, password=password, is_active=False)
        user.save()

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        send_mail(
            'Your OTP Verification Code',
            f'Your OTP is: {otp}',
            'noreply@doxygenapp.com',
            [email],
            fail_silently=False,
        )

        request.session['otp_user_id'] = user.id  # store user in session
        return redirect('verify_otp')

    return render(request, 'users/register.html')


def verify_otp(request):
    CustomUser = get_user_model()

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        user_id = request.session.get('otp_user_id')

        if not user_id:
            return redirect('register')

        user = CustomUser.objects.get(id=user_id)
        user_otp = EmailOTP.objects.filter(user=user).first()

        if user_otp and user_otp.otp == otp_input:
            user.is_active = True
            user.is_email_verified = True
            user.save()
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'users/verify.html', {'error': 'Invalid OTP'})

    return render(request, 'users/verify.html')


def resend_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('register')

    user = get_user_model().objects.get(id=user_id)
    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

    send_mail(
        'Your New OTP Code',
        f'Your OTP is: {otp}',
        'noreply@doxygenapp.com',
        [user.email],
        fail_silently=False
    )

    return redirect('verify_otp')