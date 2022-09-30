from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer, LoginSerializer, SignupSerializer
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer

    @action(methods=['GET'], detail=False)
    # 查询登陆状态
    # methods：只能用get去请求 detail：不用去object定义动作，如果detail==True,
    # 地址会变成http://localhost:8000/api/accounts/1/login_status/
    # GET请求会向数据库发索取数据的请求，从而来获取信息，该请求就像数据库的select操作一样，只是用来查询一下数据，
    # 不会修改、增加数据，不会影响资源的内容，即该请求不会产生副作用。无论进行多少次操作，结果都是一样的
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
            # request.user 是一个object，使用UserSerializer可以把object变成json
        return Response(data)  # status默认是200

    @action(methods=['POST'], detail=False)
    # 改变登陆状态
    # POST请求同PUT请求类似，都是向服务器端发送数据的，但是该请求会改变数据的种类等资源，
    # 就像数据库的insert操作一样，会创建新的内容。几乎目前所有的提交操作都是用POST请求的
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        """
                默认的 username 是 admin, password 是222444
        """
        serializer = LoginSerializer(data=request.data)  # data是用户请求的数据 post-request.data，get-request.query_params
        if not serializer.is_valid():  # 如果验证没通过(没有输入信息），返回400
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,  # 只要调用is_valid就有errors信息
            }, status=400)
        username = serializer.validated_data['username'] # validated_data：验证后对字符进行类型转换
        password = serializer.validated_data['password']

        # 验证用户密码和用户名
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match",
            }, status=400)
        # 调用login
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data) # 如果传instance，就是更新。传数据就是创建，数据要加data
        if not serializer.is_valid():  # 如果验证没通过，返回400
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,  # 只要调用is_valid就有errors信息
            }, status=400)
        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)
