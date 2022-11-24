from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from django.contrib.auth.models import User
from utils.time_helpers import utc_now

class Tweet(models.Model):
    # 记录这篇帖子是谁发的
    # 下面的换行格式推荐
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True)
    content = models.CharField(max_length=255)  # 一般255，其实是256因为最后有\0
    created_at = models.DateTimeField(auto_now_add=True)  # 每次创建时，自动加入创建时间

    # 建立联合索引 对应views里面
    # tweets = Tweet.objects.filter(
    # user_id=request.query_params['user_id']
    # ).order_by('-created_at')
    class Meta:
        index_together = (('user', 'created_at'),) # 定义联合索引，必须通过class meta索引
        ordering = ('user', '-created_at') # 默认的排序规则

    @property
    def hours_to_now(self):
        # datetime.now 不带时区信息，需要增加上 utc 的时区信息
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        # 这里是你执行 print(tweet instance) 的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'
