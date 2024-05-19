from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from AlumniFinder import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site

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

        messages.success(request, "Your account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your account.")
        
        
        ## Welcome email
        subject = "Welcome to AlumniFinder!!"
        messagess = "Hello, " + myuser.first_name + "!! Welcome to AlumniFinder.\n Thank you for signup our website. \n We have aslo sent you a confirmation email, Please confirm your email address in order to active your account. \n\n Thanking You \n Mahfuz Mia\nDeveloper of AlumniFinder."
        from_email = settings.EMAIL_HOST_USER
        to_email = [myuser.email]
        send_mail(subject, messagess, from_email, to_email, fail_silently = True)

        
        ## email address confirmation

        
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
