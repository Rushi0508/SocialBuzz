from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.http import HttpResponse
from django.contrib import messages
from .models import Profile,Post,LikePost,FollowerCount
from django.contrib.auth.decorators import login_required
import json
from itertools import chain
# Create your views here.

@login_required(login_url='/signin')
def index(req):
    curr_user_object = User.objects.get(username=req.user.username)
    curr_user_profile = Profile.objects.get(user=curr_user_object)
    user_following_list = []
    feed = []

    user_following = FollowerCount.objects.filter(follower=req.user.username)
    for users in user_following:
        user_following_list.append(users.user)
    
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)
    
    feed_list = list(chain(*feed))
    return render(req, 'home.html', {'curr_user_profile' : curr_user_profile, 'posts' : feed_list})


@login_required(login_url='/signin')
def profile(req,pk):
    curr_user_object = User.objects.get(username=req.user.username)
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts);
    user_followers = FollowerCount.objects.filter(user=pk)
    user_following = FollowerCount.objects.filter(follower=pk)

    follower = req.user.username
    user = pk
    if(FollowerCount.objects.filter(follower=follower,user=user)):
        follow_status = 'Unfollow'
    else:
        follow_status = 'Follow'
    context = {
        'curr_user_object' : curr_user_object,
        'curr_user_profile': Profile.objects.get(user=curr_user_object),
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts' : user_posts,
        'user_post_length':user_post_length,
        'user_followers' : len(user_followers),
        'user_following' : len(user_following),
        'follow_status' : follow_status
    }
    return render(req,'profile.html',context)

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
def likepost(req):
    username = req.user.username
    post_id = req.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    if(like_filter == None):
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.likes = post.likes + 1
        post.save()
        return HttpResponse(post.likes)
        # return redirect('/')
    else:
        like_filter.delete()
        post.likes = post.likes - 1
        post.save()
        return HttpResponse(post.likes)
        # return redirect('/')
@login_required(login_url='/signin')
def search(req):
    text = req.GET['text']
    if(text == ""):
        return None
    user_filter = User.objects.filter(username__contains=text).values('username')
    data = {'user_filter': list(user_filter)}
    return HttpResponse(json.dumps({'data': data}), content_type="application/json")

@login_required(login_url='/signin')
def follow(req):
    follower = req.GET['follower']
    user = req.GET['user']

    if(FollowerCount.objects.filter(follower=follower, user=user).first()):
        delete_follower = FollowerCount.objects.get(follower=follower, user=user)
        delete_follower.delete()

        followerCount = FollowerCount.objects.filter(user=user)
        data = {'followerCount': len(followerCount), 'isFollowed': False}
        return HttpResponse(json.dumps({'data': data}), content_type="application/json");
    else:
        add_follower = FollowerCount.objects.create(follower=follower,user=user)
        add_follower.save()
        followerCount = FollowerCount.objects.filter(user=user)
        data = {'followerCount': len(followerCount), 'isFollowed': True}
        return HttpResponse(json.dumps({'data': data}), content_type="application/json");

@login_required(login_url='/signin')
def delete(req,pk):
    user_posts = Post.objects.filter(id=pk)
    user_posts.delete()
    curr_user = req.user.username
    return redirect('/profile/'+curr_user)

@login_required(login_url='/signin')
def settings(req):
    curr_user_profile = Profile.objects.get(user=req.user)

    if (req.method == 'POST'):
        if(req.POST['username']!=req.user.username):
            username = req.POST['username']
            if(User.objects.filter(username=username).exists()):
                messages.info(req,'Username already exists')
                return redirect('/settings')
            else:
                new_username = User.objects.get(username=req.user.username);
                new_username.username = username;
                new_username.save();
        if (req.FILES.get('image') == None):
            image = curr_user_profile.profileimg
            bio = req.POST['bio']
            location = req.POST['location']
            name = req.POST['name']


            curr_user_profile.profileimg = image
            curr_user_profile.name = name
            curr_user_profile.bio = bio
            curr_user_profile.location = location
            curr_user_profile.save()
        if (req.FILES.get('image') != None):
            image = req.FILES.get('image')
            bio = req.POST['bio']
            location = req.POST['location']
            name = req.POST['name']

            curr_user_profile.profileimg = image
            curr_user_profile.name = name
            curr_user_profile.bio = bio
            curr_user_profile.location = location
            curr_user_profile.save()
        return redirect('profile/'+curr_user_profile.user.username)
    return render(req, 'settings.html', {'curr_user_profile': curr_user_profile})

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