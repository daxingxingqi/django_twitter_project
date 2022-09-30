from django.contrib.auth.models import User, Group
from rest_framework import serializers, exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class LoginSerializer(serializers.Serializer):
    # 检查username和password是否存在
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    # ModelSerializer可以把用户实际创建出来
    # username和email希望大小写不敏感，但是serializers.CharField只会绝对对比
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    # 所以这里需要指定出来meta
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, data):
        # username和email希望大小写不敏感，所以输入的时候传入小写
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()  # 输入的时候传入小写
        email = validated_data['email'].lower()
        password = validated_data['password'] # 大小写敏感

        # django定义好的
        """
        不能像如下这种传，因为加密了
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        """
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user
