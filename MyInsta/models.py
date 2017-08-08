# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.



class UserModel(models.Model):
    """
    This class is for user profile.
    """
    email=models.EmailField(null=False)
    name=models.CharField(max_length=120,unique=True,null=False)
    username=models.CharField(max_length=120,null=False)
    password=models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)



class UserSession(models.Model):
    user= models.ForeignKey(UserModel , on_delete=models.PROTECT)
    session_token=models.CharField(max_length=255)
    is_valid=models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def create_session_token(self):
        from uuid import uuid4
        self.session_token= uuid4()

class PostModel(models.Model):
  user = models.ForeignKey(UserModel)
  image = models.FileField(upload_to='user_images')
  image_url = models.CharField(max_length=255)
  caption = models.CharField(max_length=240)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)
  has_liked = False

  @property  #signifies a derived value , virtual column
  def like_count(self):
          return len(LikeModel.objects.filter(post=self))

  @property
  def comments(self):
      return CommentModel.objects.filter(post=self).order_by('-created_on')


class LikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class CommentModel(models.Model):
  user = models.ForeignKey(UserModel)
  post = models.ForeignKey(PostModel)
  comment_text = models.CharField(max_length=555)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)
  has_liked = False

  @property
  def comment_like(self):
      return len(LikeModel.objects.filter(post=self))


class CommentLikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    comment = models.ForeignKey(CommentModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class BrandModel(models.Model):
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class PointsModel(models.Model):
    user = models.ForeignKey(UserModel)
    brand = models.ForeignKey(BrandModel)
    points = models.IntegerField(default=1)
    total_points = 0
    image_url = models.CharField(max_length=255,default=None)
    caption = models.CharField(max_length=255,default=None)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)





