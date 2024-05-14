import random
from faker import Faker
from django.utils import timezone
import os
import django
# Manually set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media_orm_django.settings")
django.setup()

from api.models import CustomUser, Post, Comment, Follow, PostInteraction, CommentInteraction


fake = Faker()

def create_users(num_users=3):
    for _ in range(num_users):
        user = CustomUser.objects.create_user(
            username=fake.user_name(),
            password='password',
            full_name=fake.name(),
            email=fake.email(),
            bio=fake.text(),
            nb_followers=random.randint(0, 100),
            nb_followings=random.randint(0, 100),
            nb_posts=random.randint(0, 100),
            profile_picture='profile_picture.jpg',
            created_at=timezone.now()
        )

def create_posts(num_posts=3):
    users = CustomUser.objects.all()
    for _ in range(num_posts):
        user = random.choice(users)
        post = Post.objects.create(
            user=user,
            content=fake.text(max_nb_chars=200),
            photo='post_photo.jpg',
            nb_likes=random.randint(0, 100),
            nb_comments=random.randint(0, 100),
            created_at=timezone.now()
        )

def create_comments(num_comments=3):
    users = CustomUser.objects.all()
    posts = Post.objects.all()
    for _ in range(num_comments):
        user = random.choice(users)
        post = random.choice(posts)
        comment = Comment.objects.create(
            user=user,
            post=post,
            is_reply=False,
            content=fake.text(max_nb_chars=100),
            nb_likes=random.randint(0, 100),
            created_at=timezone.now()
        )

def create_follows(num_follows=3):
    users = CustomUser.objects.all()
    for _ in range(num_follows):
        follower = random.choice(users)
        following = random.choice(users.exclude(pk=follower.pk))
        Follow.objects.create(follower=follower, following=following)

def create_post_interactions(num_interactions=3):
    users = CustomUser.objects.all()
    posts = Post.objects.all()
    for _ in range(num_interactions):
        user = random.choice(users)
        post = random.choice(posts)
        interaction_type = random.choice([choice[0] for choice in PostInteraction.INTERACTION_CHOICES])
        PostInteraction.objects.create(user=user, post=post, interaction_type=interaction_type, created_at=timezone.now())

def create_comment_interactions(num_interactions=3):
    users = CustomUser.objects.all()
    comments = Comment.objects.all()
    for _ in range(num_interactions):
        user = random.choice(users)
        comment = random.choice(comments)
        interaction_type = random.choice([choice[0] for choice in CommentInteraction.INTERACTION_CHOICES])
        CommentInteraction.objects.create(user=user, comment=comment, interaction_type=interaction_type, created_at=timezone.now())

if __name__ == '__main__':
    create_users()
    create_posts()
    create_comments()
    create_follows()
    create_post_interactions()
    create_comment_interactions()
    print("Data populated successfully!")
