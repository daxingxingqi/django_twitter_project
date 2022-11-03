from accounts.api.serializers import UserSerializer,UserSerializerForTweet
from rest_framework import serializers
from tweets.models import Tweet


# 只需要制定field ModelSerializer
class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet() # user这里必须要写，dict套dict

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content') # 就是database里的key


class TweetCreateSerializer(serializers.ModelSerializer):
    #
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