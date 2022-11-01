from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now

class Tweet(models.Model):
    # 记录这篇帖子是谁发的
    # 下面的换行格式推荐
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True)
    content = models.CharField(max_length=255) # 一般255，其实是256因为最后有\0
    created_at = models.DateTimeField(auto_now_add=True) # 每次创建时，自动加入创建时间

    @property
    def hours_to_now(self):
        # datetime.now 不带时区信息，需要增加上 utc 的时区信息
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # 这里是你执行 print(tweet instance) 的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'