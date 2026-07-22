from django.shortcuts import render, redirect, get_object_or_404
from .models import Tweet, Comment, Notification
from .forms import TweetForm, UserRegistrationForm , CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import ProfileForm


def index(request):
    return render(request, 'index.html')

def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')

    for tweet in tweets:
        tweet.is_liked = request.user in tweet.likes.all()
        return render(request, 'tweet/tweet_list.html', {'tweets': tweets})

@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
          
    else:
        form = TweetForm()

    return render(request, 'tweet/tweet_form.html', {'form': form})

@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)

    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)

    return render(request, 'tweet/tweet_form.html', {'form': form})

@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method =='POST':
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet/tweet_confirm_delete.html', {'tweet': tweet})

def register(request):
    if request.method== 'POST':
      form= UserRegistrationForm(request.POST)
      if form.is_valid():
          user = form.save(commit=False)
          user.set_password(form.cleaned_data['password1'])
          user.save()
          login(request, user)
          return redirect('tweet_list')
          
     
    else:
      form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
        liked = False
    else:
        tweet.likes.add(request.user)
        liked = True
        Notification.objects.create(
            receiver=tweet.user,
            sender=request.user,
            tweet=tweet,
            notification_type='like')

    return JsonResponse({
        'liked': liked,
        'count': tweet.likes.count()
    })

@login_required
def add_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.tweet = tweet
            comment.save()
            Notification.objects.create(
                receiver=tweet.user,
                sender=request.user,
                tweet=tweet,
                notification_type='comment'
               )
            return JsonResponse({
              'id': comment.id,
              'username': comment.user.username,
              'text': comment.text,
             })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        user=request.user
    )

    if request.method == "POST":
        comment.delete()
        return JsonResponse({
         'success': True
          })


@login_required
def notifications(request):

    notifications = request.user.notifications.order_by(
        '-created_at'
    )

    return render(
        request,
        'tweet/notifications.html',
        {
            'notifications': notifications
        }
    )
@login_required
def profile(request, username):

    profile_user = User.objects.get(
        username=username
    )

    tweets = profile_user.tweet_set.order_by(
        "-created_at"
    )

    return render(
        request,
        "tweet/profile.html",
        {
            "profile_user": profile_user,
            "tweets": tweets,
        },
    )

#edit profile
@login_required
def edit_profile(request):

    profile = request.user.profile

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("profile", username=request.user.username)

    else:

        form = ProfileForm(instance=profile)

    return render(
        request,
        "tweet/edit_profile.html",
        {"form": form}
    )

@login_required
def follow_user(request, username):

    user = get_object_or_404(User, username=username)

    if user != request.user:

        profile = user.profile

        if request.user in profile.followers.all():
            profile.followers.remove(request.user)
        else:
            profile.followers.add(request.user)

    return redirect("profile", username=username)