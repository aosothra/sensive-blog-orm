from django.db.models import Count, Prefetch
from django.shortcuts import render

from blog.models import Comment, Post, Tag


def serialize_post(post):    
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.num_comments,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_posts,
    }


def index(request):
    most_popular_posts = (
        Post.objects.popular()
            .prefetch_related('author')
            .prefetch_related(Prefetch('tags', queryset=Tag.objects.join_posts_count()))
            [:5]
            .fetch_with_comments_count()
    )

    most_fresh_posts = (
        Post.objects.annotate(num_comments=Count('comments'))
            .order_by('-published_at')
            .prefetch_related('author')
            .prefetch_related(Prefetch('tags', queryset=Tag.objects.join_posts_count()))
            [:5]
    )

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post =  Post.objects.annotate(num_likes=Count('likes')).select_related('author').get(slug=slug)
    
    comments = post.comments.select_related('author').all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.join_posts_count().all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.num_likes,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects.popular()
            .prefetch_related('author')
            .prefetch_related(Prefetch('tags', queryset=Tag.objects.join_posts_count()))
            [:5]
            .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects.popular()
            .prefetch_related('author')
            .prefetch_related(Prefetch('tags', queryset=Tag.objects.join_posts_count()))
            [:5]
            .fetch_with_comments_count()
    )

    related_posts = (
        tag.posts.annotate(num_comments=Count('comments'))
            .prefetch_related('author')
            .prefetch_related(Prefetch('tags', queryset=Tag.objects.join_posts_count()))
            [:20]
    )
    
    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
