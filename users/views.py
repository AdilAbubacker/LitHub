from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from core import settings
import pyotp
import datetime
from users.tokens import account_activation_token


# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.warning(request, "You are already registered. Use another username")
            return redirect('signup')
        elif User.objects.filter(email=email):
            messages.warning(request, "Email already registered. Use another email")
            return redirect('signup')
        elif pass1 != pass2:
            messages.warning(request, "Password didn't match")
            return redirect('signup')

        user = User.objects.create_user(username, email, pass1)
        user.is_active = False
        user.save()
        messages.success(request, 'Your account has been created successfully!! Please check your email inorder to '
                                  'activate your account ')

        # Welcome Email
        subject = "Welcome to LitHub Login!!"
        message = "Hello " + user.username + "!! \n" + "Welcome to LitHub!! \nThank you for visiting our website.\n " \
                                                       "We have also sent you a confirmation email, " \
                                                       "please confirm your email address. \n\nThanking " \
                                                       "You\nAdil Abubacker"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email address confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ LitHub Login!!"
        message2 = render_to_string('email_confirmation.html', {
            'user': user.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)

        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signup')

    return render(request, 'users/signup.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        # user.profile.signup_confirmation = True
        user.save()
        # login(request, user)
        messages.success(request, "Your Account has been activated!!. Login now and enjoy shopping")
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')


def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)
        user_id = user.id
        if user is not None:
            return redirect('generate_otp', user_id=user_id, n=0)
        else:
            messages.warning(request, "Incorrect username or password")
            return redirect('signin')
    return render(request, 'users/signin.html')


def generate_otp(request, user_id, n):
    user = User.objects.get(id=user_id)

    # Generate a TOTP secret
    totp_secret = pyotp.random_base32()

    # Create a TOTP object
    totp = pyotp.TOTP(totp_secret)

    # Generate a TOTP OTP for the current time
    otp = totp.now()

    # setting timer
    expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=1)

    # Store OTP in the session
    session = SessionStore(request.session.session_key)
    request.session['otp'] = otp
    request.session['user_id'] = user.id
    request.session['otp_expiration_time'] = expiration_time.timestamp()

    # Compose the email content
    subject = 'OTP verification'
    message = f'Hello {user.username},\n\n' \
              f'Please use the following OTP to verify your email: {otp}\n\n' \
              f'Thank you!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    # Send the email
    send_mail(subject, message, from_email, recipient_list)

    if n == 1:
        messages.success(request, "Resend successful! Your message has been sent again.")

    return redirect('otp_login')


def otp_login(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        otp = request.POST.get('otp')

        # Retrieve OTP from session
        session_otp = request.session.get('otp')
        user_id = request.session.get('user_id')
        expiration_time = request.session.get('otp_expiration_time')

        if session_otp == otp:
            if datetime.datetime.now().timestamp() < expiration_time:
                user = User.objects.get(id=user_id)
                login(request, user)

                user = User.objects.get(id=user_id)
                login(request, user)
                # Clear OTP from session
                request.session['otp'] = None
                request.session['user_id'] = None

                return redirect('home')
                # return render(request, 'homepage/home.html', {'user': request.user})

            else:
                # expired otp
                request.session['otp'] = None
                request.session['user_id'] = None
                request.session['otp_expiration_time'] = None
                messages.warning(request, 'OTP has expired. Please request a new one.')
                # return redirect('otp_login')
        else:
            # OTP is invalid, display an error message
            messages.warning(request, 'Invalid OTP')

    return render(request, 'users/otp_login.html', {'user': user})


def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')
