from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer, TweetSerializerWithComments
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params

# 尽量不要使用ModelViewSet，因为这个默认可以增删查改全部权限
class TweetViewSet(viewsets.GenericViewSet):
    """
       API endpoint that allows users to create, list tweets
       """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer # 创建时的表单
    # 权限制定
    def get_permissions(self):
        # self.action就是指代下面的list和create，带request的方法
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]  # list 任何人都能访问
        return [IsAuthenticated()] # 其它需要登陆

    def retrieve(self, request, *args, **kwargs):
        # <HOMEWORK 1> 通过某个 query 参数 with_all_comments 来决定是否需要带上所有 comments
        # <HOMEWORK 2> 通过某个 query 参数 with_preview_comments 来决定是否需要带上前三条 comments
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)
    # request 用户请求
    # 查询用户tweets

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        """
        重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        """
        #if 'user_id' not in request.query_params:
         #   return Response('missing user_id', status=400)

        # 这句查询会被翻译为
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # 这句 SQL 查询会用到 user 和 created_at 的联合索引
        # 单纯的 user 索引是不够的
        # user_id 是字符串
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        # many=True 返回json
        serializer = TweetSerializer(tweets, many=True)
        # 一般来说 json 格式的 response 默认都要用 hash 的格式，最外层是dict{'tweets': serializer.data}
        # 而不能用 list 的格式（约定俗成）
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        重载 create 方法，因为需要默认用当前登录用户作为 tweet.user
        """
        """
        def get_permissions(self):
            if self.action == 'list':
                return [AllowAny()]  # list 任何人都能访问
            return [IsAuthenticated()] # 其它需要登陆
        进行验证，看是否登陆，如果是creat必须登陆
        
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        ) 接受用户request
        
        serializer.is_valid() 调用 serilizers.py里面的content = serializers.CharField(min_length=6, max_length=140)
        
        验证通过后，tweet = serializer.save()调用serilizers.py下面的
        def create(self, validated_data):
            user = self.context['request'].user
            content = validated_data['content']
            tweet = Tweet.objects.create(user=user, content=content)
            return tweet
            
        之后丢给 Response(TweetSerializer(tweet).data, status=201)显示1其它丰富信息
        """
        # 相当于deserialize
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        # save will traigger create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        # 相当于serialize
        return Response(TweetSerializer(tweet).data, status=201)