from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from .forms import SimpleSearchForm

def home(request):
    return render(request,'news/home.html')

def article_list(request, category_slug=None):
    latest_articles = Article.objects.all().order_by('-publish')[:5]
    featured_articles = Article.objects.filter(featured=True).order_by('-publish')

    articles = Article.published.all()
    categories =Category.objects.filter(is_active=True)

    article_views=Article.objects.filter(views__gte=1).order_by('-views')[:5]

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=current_category)

    search_query = request.GET.get('q')
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    articles = articles.order_by('-publish')

    paginator = Paginator(articles, 10)  # 10 مقالات per page
    page = request.GET.get('page')

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)



    context = {
        'articles': articles,
        'categories ': categories,
        'read_views':article_views,
        'current_category': current_category,
        'search_query': search_query,
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,

    }
    return render(request, 'news/articles/list.html',context)

#====================================
#end article_list
#====================================

#====================================
#start article_detial
#====================================

@login_required

def article_detail(request, slug):
    """
    عرض صفحة تفاصيل المقال مع أزرار الحفظ والإعجاب فقط
    """
    article = get_object_or_404(Article,slug=slug)
    latest_articles = Article.objects.filter().order_by('-publish')[:5]
    related_articles = Article.published.filter(category=article.category).exclude(id=article.id)[:5]
    like_count=article.reactions.filter(reaction_type='like').count()
    dislike_count=article.reactions.filter(reaction_type='dislike').count()
    si_saved=SavedArticle.objects.filter(user=request.user,article=article).exists()if request.user.is_authenticated else False
    # حالة المستخدم (للأزرار)
    user_reaction = None
    user_has_saved = False

    article.views +=1
    article.save()


    if request.user.is_authenticated:

        user_reaction = Reaction.objects.filter(article=article,user=request.user).first()
        user_has_saved = SavedArticle.objects.filter(article=article,user=request.user).exists()
    context = {
        'article': article,
        'related_articles':related_articles,
        'latest_articles':latest_articles,
        'user_reaction': user_reaction, # الحالة الحالية للإعجاب
        'like_count': like_count,
        'dislike_count':dislike_count ,
        'si_saved' : si_saved ,
        'save_count': user_has_saved,
    }

    return render(request, 'news/articles/article_detail.html', context)

#====================================
#end article_detial
#====================================


#====================================
#start catigory_article
#====================================
@login_required
def category_articles(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    article = Article.published.filter(category=category)

    paginator = Paginator(article, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(category)

    context = {
        'category': category,
        'page_obj': page_obj,
        'articles': page_obj,
    }
    return render(request,'news/articles/article_category.html',context)

#====================================
#end category_article
#====================================

#====================================
#start contact
#====================================
@login_required
def contact(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            send_mail(
                f'رسالة جديدة من {name}: {subject}',
                f'الاسم: {name}\nالبريد الإلكتروني: {email}\nالرسالة: {message}',
                email,  # من
                [settings.DEFAULT_FROM_EMAIL],  # إلى
                fail_silently=False,
            )
            messages.success(request, 'تم إرسال رسالتك بنجاح! سنرد عليك قريباً.')
        except Exception as e:
            messages.error(request, 'حدث خطأ في إرسال الرسالة. يرجى المحاولة مرة أخرى.')

        return redirect('news:contact')

    return render(request,'news/articles/contact.html')


#====================================
#end contact
#====================================


#====================================
#start search
#====================================
def search(request):
    """
    دالة البحث البسيطة - تعمل بشكل صحيح
    """
    # الحصول على كلمة البحث من الرابط
    query = request.GET.get('q', '').strip()

    # البيانات الأساسية للصفحة
    breaking_news = Article.published.filter(breaking_news=True)[:6]
    featured_articles = Article.published.filter(featured=True)[:6]
    categories = Category.objects.filter(is_active=True)

    # البحث
    articles = Article.objects.none()

    if query:

        articles = Article.published.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        ).order_by('-publish')

    # الترقيم
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'query': query,
        'articles': page_obj,
        'page_obj': page_obj,
        'breaking_news': breaking_news,
        'featured_articles': featured_articles,
        'categories': categories,
    }

    return render(request, 'news/articles/search.html', context)


#====================================
#end search
#====================================

#====================================
#start my_saved_articles
#====================================
@login_required
def my_saved_articles(request):
    save_articles=SavedArticle.objects.filter(user=request.user).select_related(
        'article',
        'article__category'
    ).order_by('-saved_at')
    category=Category.objects.all()

    context={
        'saved_articles':save_articles,
        'page_title':'articles saved',
        'categories':category,

    }
    return render(request,'news/articles/saved_article.html',context)


#====================================
#end my_saved_artciles
#====================================

#====================================
#start unsave_artcile
#====================================
@login_required
def unsave_artcile(request,slug):
    if request.method=='POST':
        article=get_object_or_404(Article,slug=slug)
        saved_article=get_object_or_404(SavedArticle,user=request.user,article=article)
        saved_article.delete()
        messages.success(request,"deleted article sausccessfuly")
    return redirect('news:saved_articles')

#====================================
#end unsave_artcile
#====================================

#====================================
#start handle_reaction
#====================================
def handle_reaction(request, slug):
    if request.method == 'POST':
        article = get_object_or_404(Article, slug=slug)
        reaction_type = request.POST.get('reaction_type')

        if reaction_type in ['like', 'dislike']:
            # معالجة الإعجاب/عدم الإعجاب
            reaction, created = Reaction.objects.get_or_create(
                user=request.user,
                article=article
            )

            if not created and reaction.reaction_type == reaction_type:
                # إذا كان نفس التفاعل، نزيله
                reaction.delete()
                messages.info(request, f'تم إزالة  الأعجاب')
            else:
                # إذا كان مختلفاً أو جديداً، نضيفه/نعدله
                reaction.reaction_type = reaction_type
                reaction.save()
                messages.success(request, f'تم الأعجاب ')

        elif reaction_type == 'save':
            # معالجة الحفظ
            saved, created = SavedArticle.objects.get_or_create(
                user=request.user,
                article=article
            )
            if not created:
                saved.delete()
                messages.info(request, 'تم إزالة المقال من المحفوظات')
            else:
                messages.success(request, 'تم حفظ المقال بنجاح')

    return redirect('news:article_detail', slug=slug)

#====================================
#end handle_reaction
#====================================

def about(request):
    return render(request,'news/articles/about.html')
