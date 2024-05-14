from django.urls import path

from .views import *

urlpatterns = [
    path('likepost/', like_post,name="like post"),
    path('commentpost/', comment_post,name="comment post"),
    path('replycomment/', reply_to_comment,name="reply comment post")

    
]


