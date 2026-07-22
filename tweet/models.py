from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Tweet(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_tweets', blank=True)


    def __str__(self):
        return f'{self.user.username} - {self.text[:10]}'
    

class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} commented on {self.tweet.id}'


#notifiction
class Notification(models.Model):
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    tweet = models.ForeignKey(
        'Tweet',
        on_delete=models.CASCADE
    )

    notification_type = models.CharField(
        max_length=20
    )  # like or comment

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"

#profile

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    bio = models.TextField(blank=True)

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        default="profile_pics/default.png"
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    followers = models.ManyToManyField(
        User,
        related_name="following",
        blank=True
      )

    def __str__(self):
        return self.user.username