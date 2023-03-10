from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.http import HttpResponse
from django.contrib import messages
from .models import Profile,Post
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='/signin')
def index(req):
    user_object = User.objects.get(username=req.user.username)
    user_profile = Profile.objects.get(user=user_object)
    return render(req, 'index.html', {'user_profile' : user_profile})

@login_required(login_url='/signin')
def upload(req):
    if(req.method=='POST'):
        user = req.user.username
        image = req.FILES.get('image_upload')
        caption = req.POST['caption']

        new_post = Post.objects.create(user=user,image=image,caption=caption)
        new_post.save();
        return redirect('/');
    else:
        return redirect('/');
          
        

@login_required(login_url='/signin')
def settings(req):
    user_profile = Profile.objects.get(user=req.user)

    if (req.method == 'POST'):
        
        if (req.FILES.get('image') == None):
            image = user_profile.profileimg
            bio = req.POST['bio']
            location = req.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if (req.FILES.get('image') != None):
            image = req.FILES.get('image')
            bio = req.POST['bio']
            location = req.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')
    return render(req, 'setting.html', {'user_profile': user_profile})

def signin(req):
    if(req.method=='POST'):
        username = req.POST['username']
        password = req.POST['password']

        user = auth.authenticate(username=username, password=password)

        if(user is not None):
            auth.login(req,user)
            try:
                next = req.GET['next'];
            except:
                next = '/';
            return redirect(next);
        else:
            messages.info(req, 'Username or Password is incorrect')
            return redirect('signin')
    else:
        return render(req, 'signin.html')
        
@login_required(login_url='/signin')
def logout(req):
    auth.logout(req)
    return redirect('signin')

def signup(req):
    if(req.method=='POST'):
        username = req.POST['username']
        email = req.POST['email']
        password = req.POST['password']
        password2 = req.POST['password2']

        if(password==password2):
            if(User.objects.filter(email=email).exists()):
                messages.info(req,'Email already exists')
                return redirect('signup')
            elif(User.objects.filter(username=username).exists()):
                messages.info(req,'Username already exists')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Login user
                user_login = auth.authenticate(username=username, password=password)
                auth.login(req,user_login)           

                # Create a Profile object for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user = user_model.id)
                new_profile.save()
                return redirect('/')
        else:
            messages.info(req, 'Password do not match')
            return redirect('signup')
    else:
        return render(req,'signup.html')