from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import * 
from django.db.models import F, Count, Case, When, Value, BooleanField
from django.db.models import Subquery, OuterRef

@api_view(['POST'])
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def like_post(request):
    try:
        # Extract user instance from the request
        user_id = request.data.get('user_id')

        # Extract post_id from the request data
        post_id = request.data.get('post_id')

        try:
            # Check if the post exists
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


        try:
            # Check if the post exists
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if PostInteraction.objects.filter(user=user, post=post, interaction_type=PostInteraction.LIKE).exists():
            return Response({"error": "You have already liked this post"}, status=status.HTTP_400_BAD_REQUEST)

        interaction_data = {"user": user_id, "post": post_id, "interaction_type": PostInteraction.LIKE}
        # Create a serializer instance with the interaction_data
        serializer = PostInteractionSerializer(data=interaction_data)
        
        if serializer.is_valid():
            serializer.save()
            post.nb_likes += 1
            post.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # If the serializer is not valid, return a 400 error with the serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e : 
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def comment_post(request):
    try:

        # Extract post_id and comment content from the request data
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')
        content = request.data.get('content')

        try:
            # Check if the post exists
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND)


        try:
            # Check if the post exists
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        # Create a comment instance with the user and post
        comment = Comment.objects.create(
            user=user,
            post=post,
            content=content,
            nb_likes=0  # Assuming no likes initially
        )

        # Increment the number of comments for the post
        post.nb_comments += 1
        post.save()

        # Serialize the comment instance
        serializer = CommentSerializer(comment)

        # Return the serialized comment data
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def reply_to_comment(request):
    try:
        # Extract user instance from the request
        user_id = request.data.get('user_id')

        parent_comment_id = request.data.get('comment_id')
        reply_content = request.data.get('content')

        try:
            # Check if the parent comment exists
            parent_comment = Comment.objects.get(pk=parent_comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Parent comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Create the reply comment
        reply = Comment.objects.create(
            user_id=user_id,
            post=parent_comment.post, 
            is_reply=True,
            content=reply_content,
            created_at=timezone.now()
        )

        # Link the reply comment to the parent comment
        reply_to = ReplyTo.objects.create(parent=parent_comment, comment=reply)

        # Increment the number of comments for the parent comment

        return Response({"success": "Reply added successfully"}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_recent_posts(request):
    try:
        # Assuming the user is authenticated and available through request.user
        user_id = int(request.GET.get('user_id'))
        try:
            # Check if the post exists
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        followed_user_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        # Get IDs of posts liked by the current user
        liked_posts_ids = set(PostInteraction.objects.filter(user=user, interaction_type='like').values_list('post_id', flat=True))
        saved_posts_ids = set(PostInteraction.objects.filter(user=user, interaction_type='save').values_list('post_id', flat=True))

        recent_posts = Post.objects.filter(user_id__in=followed_user_ids).order_by('-created_at')[:10]

        serializer = RecentPostSerializer(recent_posts, many=True)
        data = serializer.data

        for post_data in data:
            post_id = post_data['id']
            post_data['is_liked'] = post_id in liked_posts_ids
            post_data['is_saved'] = post_id in saved_posts_ids

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)