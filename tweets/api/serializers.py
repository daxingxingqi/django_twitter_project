from accounts.api.serializers import UserSerializer,UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from rest_framework import serializers
from tweets.models import Tweet
from likes.api.serializers import LikeSerializer
from likes.services import LikeService


# 只需要制定field ModelSerializer
class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet() # user这里必须要写，dict套dict
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = ('id',
            'user',
            'created_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
                  ) # 就是database里的key

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)


class TweetSerializerForCreate(serializers.ModelSerializer):

    content = serializers.CharField(min_length=6, max_length=140)
    # 使用了ModelSerializer，那么要指定用了那个model，指定那些fields可以写进去
    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet


class TweetSerializerForDetail(TweetSerializer):
    # <HOMEWORK> 使用 serialziers.SerializerMethodField 的方式实现 comments
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = ('id',
            'user',
            'comments',
            'created_at',
            'content',
            'likes',
            'comments',
            'likes_count',
            'comments_count',
            'has_liked',
                  )