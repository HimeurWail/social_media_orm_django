from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'photo', 'nb_likes', 'nb_comments', 'created_at']




class PostInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostInteraction
        fields = ['id', 'user', 'post', 'interaction_type', 'created_at']

    def validate(self, data):
        interaction_type = data.get('interaction_type')
        if interaction_type not in [choice[0] for choice in PostInteraction.INTERACTION_CHOICES]:
            raise serializers.ValidationError("Invalid interaction type")

        return data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']