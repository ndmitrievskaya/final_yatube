from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, reverse

from .forms import CommentForm, PostForm
from .models import Comment, Post, Group, User, Follow


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
    form = PostForm(request.POST or None, files=request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            if request.user.is_authenticated:
                post = Post(**form.cleaned_data, author=request.user)
                post.save()
                return redirect('/')
            return redirect('/auth/login')

    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    requested_user = get_object_or_404(User, username=username)
    posts = requested_user.posts.count()
    all_posts = requested_user.posts.all()
    paginator = Paginator(all_posts, 10)

    is_following = request.user.is_authenticated and Follow.objects.filter(author=requested_user,
                                                                           user=request.user).count()

    follower_count = Follow.objects.filter(author=requested_user).count()
    follows_count = Follow.objects.filter(user=requested_user).count()

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'profile.html', {
            'following': is_following,
            'follower_count': follower_count,
            'follows_count': follows_count,
            'profile': requested_user,
            "post_count": posts,
            'page': page,
            'paginator': paginator,
            'does_own_profile': request.user == requested_user,
        })


def post_view(request, username, post_id):
    post = get_object_or_404(Post,
                             id__exact=post_id,
                             author__username=username)
    author = post.author
    post_count = author.posts.count()

    comment_form = CommentForm()

    is_following = request.user.is_authenticated and Follow.objects.filter(author=author, user=request.user).count()

    follower_count = Follow.objects.filter(author=author).count()
    follows_count = Follow.objects.filter(user=author).count()

    return render(
        request,
        'post.html',
        {
            'profile': author,
            "post_count": post_count,
            'post': post,
            'comments': post.comments.all(),  # передавать `post` достаточно, но тесты требуют QuerySet в явном виде
            'comment_form': comment_form,
            'following': is_following,
            'follower_count': follower_count,
            'follows_count': follows_count,
            'does_own_profile': request.user == author,
        })


def post_edit(request, username, post_id):
    post = get_object_or_404(Post,
                             id__exact=post_id,
                             author__username=username)
    if request.user != post.author:
        return redirect(reverse('post', args=[username, post_id]))

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('post', args=[username, post_id]))

    return render(request, 'post_edit.html', {
        "form": form,
        'username': username,
        'post_id': post_id,
        'post': post
    })


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None, files=request.FILES or None)

    if not request.user.is_authenticated:
        return redirect("post", username=username, post_id=post_id)

    post = get_object_or_404(Post,
                             id__exact=post_id,
                             author__username=username)
    if form.is_valid():
        comment = Comment(**form.cleaned_data, author=request.user, post=post)
        comment.save()

    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).values('author')
    posts = Post.objects.filter(author__in=following)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, author=author, user=request.user).delete()
    return redirect('profile', username=username)
