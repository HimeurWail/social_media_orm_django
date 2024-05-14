from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=500, blank=True, null=True)
    nb_followers = models.IntegerField(default=0)
    nb_followings = models.IntegerField(default=0)
    nb_posts = models.IntegerField(default=0)
    profile_picture = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    photo = models.CharField(max_length=100, blank=True, null=True)
    nb_likes = models.IntegerField(default=0)
    nb_comments = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content[:50]

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_reply = models.BooleanField(default=False)
    content = models.CharField(max_length=500)
    nb_likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content[:50]

class ReplyTo(models.Model):
    parent = models.ForeignKey(Comment, related_name='parent_comment', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='replied_comment', on_delete=models.CASCADE)

    def __str__(self):
        return f"Reply to {self.parent_id}"

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('follower', 'following'),)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class PostInteraction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    SAVE = 'save'
    ARCHIVE = 'archive'
    INTERACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
        (SAVE, 'Save'),
        (ARCHIVE, 'Archive')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('user', 'post', 'interaction_type'),)

    def __str__(self):
        return f"{self.user.username} {self.interaction_type}d post {self.post_id}"

class CommentInteraction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    INTERACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('user', 'comment', 'interaction_type'),)

    def __str__(self):
        return f"{self.user.username} {self.interaction_type}d comment {self.comment_id}"
