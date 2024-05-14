from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import * 

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
        user = request.data.get('user_id')
        post_id = request.data.get('post_id')
        content = request.data.get('content')

        try:
            # Check if the post exists
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

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



