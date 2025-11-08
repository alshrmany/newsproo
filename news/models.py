from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    slug = models.SlugField(max_length=250, unique=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Article.Status.PUBLISHED)

class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'مسودة'
        PUBLISHED = 'PB', 'منشور'
        ARCHIVED = 'AR', 'مؤرشف'
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250,unique_for_date='publish',null=True)
    content = models.TextField()
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    publish = models.DateTimeField(default=timezone.now, verbose_name="تاريخ النشر")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='articles/%Y/%m/%d/', null=True,)
    breaking_news = models.BooleanField(default=False, verbose_name="خبر عاجل")

    featured = models.BooleanField(default=False,blank=True, verbose_name="مميز")
    views=models.PositiveIntegerField(default=0)


    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name="الحالة")

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name="مقال"
        verbose_name_plural="المقالات"
        ordering = ['-publish']

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    article = models.ForeignKey(Article, on_delete=models.CASCADE,related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.reaction_type} to {self.article.title}"

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': Article.slug})


class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_articles', verbose_name="المستخدم")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='saved_by', verbose_name="المقال")
    saved_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = "مقال محفوظ"
        verbose_name_plural = "المقالات المحفوظة"
        unique_together = ('user', 'article')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} حفظ {self.article.title}"

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': Article.slug})

#=======================================
