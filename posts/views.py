from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Post, Group, User


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10) 

    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
       )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    return render(request, "group.html", {"group": group, "posts": posts})

def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post(**form.cleaned_data, author=request.user)
            post.save()
            return redirect('/')
    else:
        form = PostForm()
    return render(request, "new_post.html", {"form": form})

def profile(request, username):
        user = get_object_or_404(User, username = username)
        name = user.get_full_name()
        user_name = user.get_username()
        posts = user.posts.count()
        all_posts = user.posts.order_by('-pub_date').all()[:12]
        return render(request, 'profile.html', {'user': user, 'name': name, 'username': user_name, "posts": posts, 'all_posts': all_posts})
 
 
#def post_view(request, username, post_id):
        # тут тело функции
#        return render(request, 'post.html', {})


#def post_edit(request, username, post_id):
        # тут тело функции. Не забудьте проверить, 
        # что текущий пользователь — это автор записи.
        # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
        # который вы создали раньше (вы могли назвать шаблон иначе)
  #      return render(request, 'post_new.html', {})