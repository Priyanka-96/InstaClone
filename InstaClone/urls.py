"""InstaClone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf.urls import url
from MyInsta.views import signup_view
from MyInsta.views import login_view,feed_view,post_view,like_view,comment_view,logout_view,points_view,upvote_view,self_view
urlpatterns = [
  url('self/',self_view),
  #url('upvote/',upvote_view),
  url('points/', points_view),
  url('logout/', logout_view),
  url('like/', like_view),
  url('post/', post_view),
  url('feed/', feed_view),
  url('comment/',comment_view),
 # url(r'^/(?P<username>\w+)/$', profile_page_view),

  url('login/', login_view),
  url('signup', signup_view),
  #url(r'^(?P<username>\w+)/$', profile_page_view),

]