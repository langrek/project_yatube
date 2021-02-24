from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post


def autorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')

    return check_user


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator})


@autorized_only
def new_post(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page,
                                          'paginator': paginator
                                          })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page'),
    page = paginator.get_page(page_number)
    count = author_posts.count()
    if request.user.is_authenticated and author.following.filter(
        user=request.user
    ).exists():
        following = True
    else:
        following = False
    count = author_posts.count()
    return render(request, 'profile.html', {
        'author': author,
        'author_posts': author_posts,
        'page': page,
        'count': count,
        'paginator': paginator,
        'following': following}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    count = author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(request, 'post.html', {
        'post': post,
        'author': author,
        'post_id': post_id,
        'count': count,
        'form': form,
        'comments': comments
    })


@autorized_only
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'new_post.html', context)


@autorized_only
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            text=request.POST['text']
        )
        comment.save()
    return redirect('post', username, post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@autorized_only
def follow_index(request):
    user = get_object_or_404(User, username=request.user.username)
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html',
        {'user': user, 'page': page, 'paginator': paginator}
    )


@autorized_only
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=author)


@autorized_only
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    wire = Follow.objects.filter(user=request.user, author=author)
    if Follow.objects.filter(user=request.user, author=author).exists():
        wire.delete()
        return redirect('profile', username=username)
    return redirect('profile', username=username)


def delete_post(request, username, post_id):
    post = Post.objects.filter(author=username, post_id=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    else:
        post.delete()
        return redirect('index')
