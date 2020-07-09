from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import CreateView
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Post, Group, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
        'paginator': paginator
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
        "group": group,
        'page': page,
        'paginator': paginator
    })


def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                post = Post(**form.cleaned_data, author=request.user)
                post.save()
                return redirect('/')
            return redirect('/auth/login')
    else:
        form = PostForm()
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    requested_user = get_object_or_404(User, username=username)
    name = requested_user.get_full_name()
    user_name = requested_user.get_username()
    posts = requested_user.posts.count()
    all_posts = requested_user.posts.all()
    paginator = Paginator(all_posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'profile.html', {
            'requested_user': requested_user,
            'full_name': name,
            'username': user_name,
            "post_count": posts,
            'page': page,
            'paginator': paginator
        })


def post_view(request, username, post_id):
    post = get_object_or_404(Post,
                             id__exact=post_id,
                             author__username=username)
    requested_user = get_object_or_404(User, username=username)
    full_name = requested_user.get_full_name()
    post_count = requested_user.posts.count()

    return render(
        request, 'post.html', {
            'full_name': full_name,
            'username': username,
            "post_count": post_count,
            'post': post
        })


def post_edit(request, username, post_id):
    post = get_object_or_404(Post,
                             id__exact=post_id,
                             author__username=username)
    if request.user != post.author:
        return redirect(reverse('post', args=[username, post_id]))
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('post', args=[username, post_id]))
    else:
        form = PostForm(instance=post)

    return render(request, 'post_edit.html', {
        "form": form,
        'username': username,
        'post_id': post_id,
        'post': post
    })
