from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from AlumniFinder import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token

# Create your views here.
def home(request):
    return render(request, "home/index.html")

def signup(request):
    if request.method == "POST":
        # fullname = request.POST.get('fullname')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!! Please login your account or forgot password.")
            return redirect('signin')
        
        if pass1 != pass2:
            messages.error(request, "Password did'nt match!!")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your account has been successfully created. We have sent you confirmation email, please confirm your email in order to activate your account.")
        
        
        ## Welcome email
        subject = "Welcome to AlumniFinder!!"
        messagess = "Hello, " + myuser.first_name + "!! Welcome to AlumniFinder.\nThank you for signup our website.\nWe have aslo sent you a confirmation email, Please confirm your email address in order to active your account.\n\nBest regards,\nMohammad Mahfuz\nDeveloper of AlumniFinder."
        from_email = settings.EMAIL_HOST_USER
        to_email = [myuser.email]
        send_mail(subject, messagess, from_email, to_email, fail_silently = True)

        
        ## email address confirmation email
        current_site = get_current_site(request)
        email_subjects = "Confirm your email @ ALumniFinder"
        messagess2 = render_to_string('authentication/email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subjects,
            messagess2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')


    return render(request, "authentication/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        # print(username)
        # print(pass1)

        user = authenticate(username=username, password=pass1)

        print(f"user: {user}")

        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, "Your account logged in successfully.")
            return render(request, "home/index.html", {'fname': fname})
        else:
            messages.error(request, "Provide valid credentials!!")
            return redirect('signin')
        
    return render(request, 'authentication/login.html')


def signOut(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request, 'authentication/activationFailed.html')
