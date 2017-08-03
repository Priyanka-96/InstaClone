from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render,redirect
from form import SignUpForm,LoginForm,PostForm,LikeForm,CommentForm,UpvoteForm,CommentLikeForm
from models import UserModel,UserSession,PostModel,LikeModel,CommentModel,BrandModel,PointsModel,CommentLikeModel
from django.contrib.auth.hashers import make_password,check_password
from imgurpython import ImgurClient
from InstaClone.settings import BASE_DIR
from clarifai.rest import ClarifaiApp
import sendgrid
from sendgrid.helpers.mail import *




YOUR_CLIENT_ID='0ae3e0aaab462eb'
YOUR_CLIENT_SECRET='891355a82efb4a5390963c0a522816288a64c11b'
API_KEY='a08a3ac8121d442ba5a967eecdca029d'
SENDGRID_API_KEY="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"



# Create your views here.
def signup_view(request):
    import datetime
    date = datetime.datetime.now()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if len(username)>=4:
                if len(password)>=5:

                    user = UserModel(name=name, password=make_password(password), email=email, username=username)
                    user.save()

                    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
                    from_email = Email("help@instaclone.com")
                    to_email = Email(email)
                    subject = "Sucessfully SIGNED UP!"
                    content = Content("text/plain", "Welcome to Instaclone application. Enjoy your experience :)!")
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())

                    if response.status_code==202:
                        message = "Email Send! :)"
                    else:
                        message="Unable to send Email! :("
                    return render(request, 'success.html',{'response': message})
                else:
                    warning="Password should be of atleast 5 characters!"
                    return render(request, 'index.html',{'error1': warning})
            else:
                warning1="UserName should be of atleast 4 characters!"
                return render(request, 'index.html', {'error': warning1})

    else:
        form = SignUpForm()

    return render(request, 'index.html', {'form':form , 'abhi_ka_time' : date})

def login_view(request):
    import datetime
    date = datetime.datetime.now()
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = UserSession(user=user)
                    token.create_session_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'
                    note='Incorrect Password! Please try again!'
                    return render(request, 'login.html', response_data, {'message': note})


    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data ,{'abhi_ka_time' : date})


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts' : posts})
    else:
        return redirect('/login/')


def post_view(request):
    user = check_validation(request)
    try:
        if user:
          #if request.method=='GET':
          #  form =PostForm()
            if request.method == 'POST':
                form = PostForm(request.POST, request.FILES)
                if form.is_valid():
                    image = form.cleaned_data.get('image')
                    caption = form.cleaned_data.get('caption')
                    if image:
                        post = PostModel(user=user, image=image, caption=caption)
                        post.save()
                        path=str(BASE_DIR + "\\" + post.image.url)
                        client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
                        post.image_url = client.upload_from_path(path, anon=True)['link']#rhs gives url of pic on imgur.
                        post.save()
                        points = win_points(user, post.image_url, caption)
                        return render(request, 'post.html', {'form': form, 'user': user, 'error': points})

                    else:
                        message= "select a image"
                        return render(request, 'post.html', {'message': message})

            else:
                form = PostForm()
            return render(request, 'post.html', {'form' : form})
        else:
            return redirect('/login')
    except:
        ValueError

def logout_view(request):
    user = check_validation(request)
    if user is not None:
        latest_session = UserSession.objects.filter(user=user).last()
        if latest_session:
            latest_session.delete()

    return redirect("/login/")


def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = UserSession.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None

def like_view(request):
  user = check_validation(request)
  if user and request.method == 'POST':
    form=LikeForm(request.POST)
    if form.is_valid():
        post_id=form.cleaned_data.get('post').id
        existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
        if not existing_like:
            LikeModel.objects.create(post_id=post_id, user=user)
            postget = PostModel.objects.filter(id=post_id).first()
            userid = postget.user_id
            user = UserModel.objects.filter(id=userid).first()
            email = user.email
            sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
            from_email = Email("help@instaclone.com")
            to_email = Email(email)
            subject = "InstaClone : SomeOne liked your post!"
            content = Content("text/plain", "You got a like on your post! check it out:)")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())

        else:
            existing_like.delete()
        return redirect('/feed/')
  else:
    return redirect('/login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            postget=PostModel.objects.filter(id=post_id).first()
            userid=postget.user_id
            user=UserModel.objects.filter(id=userid).first()
            email=user.email
            sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
            from_email = Email("help@instaclone.com")
            to_email = Email(email)
            subject = "InstaClone : New comment on your post!"
            content = Content("text/plain", "Someone just commented on your post! check it out:)")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())

            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')

# method to create upvote for comments
def upvote_view(request):
    user = check_validation(request)
    comment = None
    print "upvote view"
    if user and request.method == 'POST':

        form = UpvoteForm(request.POST)
        if form.is_valid():
            print form.cleaned_data

            comment_id = int(form.cleaned_data.get('id'))

            comment = CommentModel.objects.filter(id=comment_id).first()
            print "upvoted not yet"

            if comment is not None:
                # print ' unliking post'
                print "upvoted"
                comment.upvote_num += 1
                comment.save()
                print comment.upvote_num
            else:
                print 'stupid mistake'
                #liked_msg = 'Unliked!'

        return redirect('/login_success/')
    else:
        return redirect('/login/')


def win_points(user, image_url, caption):
    brands_in_caption = 0
    brand_selected = ""
    points = 0;
    brands = BrandModel.objects.all()

    for brand in brands:
        if caption.__contains__(brand.name):
            brand_selected = brand.name
            brands_in_caption += 1
    image_caption = verify_image(image_url)
    if brands_in_caption == 1:
        points += 50
        if image_caption.__contains__(brand_selected):
            points += 50
    else:
        if image_caption != "":
            if BrandModel.objects.filter(name=image_caption):
                points += 50
    if points >= 50:
        brand = BrandModel.objects.filter(name=brand_selected).first()
        PointsModel.objects.create(user=user, brand=brand)
        return "Post Added with 1 points"
    else:
        return "Post Added"



def verify_image(image_url):
    app = ClarifaiApp(api_key=API_KEY)
    model = app.models.get("logo")
    responce = model.predict_by_url(url=image_url)
    if responce["status"]["code"] == 10000:
        if responce["outputs"][0]["data"]:
            return responce["outputs"][0]["data"]["regions"][0]["data"]["concepts"][0]["name"].lower()
    return ""


def points_view(request):
    user = check_validation(request)
    if user:

        points_model = PointsModel.objects.filter(user=user).order_by('-created_on')
        points_model.total_points = len(PointsModel.objects.filter(user=user))
        brands = BrandModel.objects.all()
        return render(request, 'points.html', {'points_model': points_model, 'brands': brands, 'user': user})
    else:
        return redirect('/login/')
