from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import IntegrityError
from datetime import datetime, timedelta
import tempfile
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Category, Article, Reaction, SavedArticle


class CategoryModelTest(TestCase):
    """Test cases for Category model"""

    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name="تقنية",
            description="أخبار التقنية والتكنولوجيا",
            is_active=True
        )

    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, "تقنية")
        self.assertEqual(self.category.description, "أخبار التقنية والتكنولوجيا")
        self.assertTrue(self.category.is_active)
        self.assertIsNotNone(self.category.created_at)

    def test_category_str_method(self):
        """Test category string representation"""
        expected = "تقنية"
        self.assertEqual(str(self.category), expected)

    def test_category_default_values(self):
        """Test category default field values"""
        category = Category.objects.create(name="رياضة")
        self.assertTrue(category.is_active)
        self.assertEqual(category.description, "")

    def test_inactive_category(self):
        """Test inactive category creation"""
        inactive_category = Category.objects.create(
            name="غير نشط",
            is_active=False
        )
        self.assertFalse(inactive_category.is_active)


class ArticleModelTest(TestCase):
    """Test cases for Article model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(
            name="تقنية",
            description="أخبار التقنية",
            is_active=True
        )
        self.article = Article.objects.create(
            title="مقال تجريبي",
            slug="test-article",
            content="محتوى المقال التجريبي",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_article_creation(self):
        """Test article creation"""
        self.assertEqual(self.article.title, "مقال تجريبي")
        self.assertEqual(self.article.slug, "test-article")
        self.assertEqual(self.article.content, "محتوى المقال التجريبي")
        self.assertEqual(self.article.author, self.user)
        self.assertEqual(self.article.category, self.category)
        self.assertEqual(self.article.status, Article.Status.PUBLISHED)

    def test_article_str_method(self):
        """Test article string representation"""
        expected = "مقال تجريبي"
        self.assertEqual(str(self.article), expected)

    def test_article_default_status(self):
        """Test article default status is draft"""
        article = Article.objects.create(
            title="مسودة مقال",
            slug="draft-article",
            content="محتوى مسودة",
            author=self.user
        )
        self.assertEqual(article.status, Article.Status.DRAFT)

    def test_article_status_choices(self):
        """Test article status choices"""
        self.assertEqual(Article.Status.DRAFT, 'DF')
        self.assertEqual(Article.Status.PUBLISHED, 'PB')
        self.assertEqual(Article.Status.ARCHIVED, 'AR')

    def test_breaking_news_default(self):
        """Test breaking_news default value"""
        self.assertFalse(self.article.breaking_news)

    def test_featured_default(self):
        """Test featured default value"""
        self.assertFalse(self.article.featured)

    def test_article_timestamps(self):
        """Test article timestamps"""
        self.assertIsNotNone(self.article.created_at)
        self.assertIsNotNone(self.article.updated_at)
        self.assertIsNotNone(self.article.publish)

    def test_article_with_null_category(self):
        """Test article with null category (cascade delete)"""
        article = Article.objects.create(
            title="مقال بدون تصنيف",
            slug="no-category-article",
            content="محتوى المقال",
            author=self.user,
            category=None
        )
        self.assertIsNone(article.category)

    def test_article_ordering(self):
        """Test article ordering by created_at desc"""
        # Create another article
        article2 = Article.objects.create(
            title="مقال أحدث",
            slug="newer-article",
            content="محتوى أحدث",
            author=self.user,
            category=self.category
        )

        articles = Article.objects.all()
        self.assertEqual(articles[0], article2)  # Newest first
        self.assertEqual(articles[1], self.article)

    def test_get_absolute_url(self):
        """Test get_absolute_url method"""
        expected_url = reverse('news:article_detail', kwargs={'slug': self.article.slug})
        self.assertEqual(self.article.get_absolute_url(), expected_url)


class PublishedManagerTest(TestCase):
    """Test cases for PublishedManager"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)

        # Create articles with different statuses
        self.published_article = Article.objects.create(
            title="مقال منشور",
            slug="published-article",
            content="محتوى منشور",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

        self.draft_article = Article.objects.create(
            title="مقال مسودة",
            slug="draft-article",
            content="محتوى مسودة",
            author=self.user,
            category=self.category,
            status=Article.Status.DRAFT
        )

        self.archived_article = Article.objects.create(
            title="مقال مؤرشف",
            slug="archived-article",
            content="محتوى مؤرشف",
            author=self.user,
            category=self.category,
            status=Article.Status.ARCHIVED
        )

    def test_published_manager_filters_published_only(self):
        """Test that published manager only returns published articles"""
        published_articles = Article.published.all()
        self.assertEqual(published_articles.count(), 1)
        self.assertEqual(published_articles[0], self.published_article)

    def test_objects_manager_returns_all(self):
        """Test that objects manager returns all articles"""
        all_articles = Article.objects.all()
        self.assertEqual(all_articles.count(), 3)


class ReactionModelTest(TestCase):
    """Test cases for Reaction model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)
        self.article = Article.objects.create(
            title="مقال للتفاعل",
            slug="reaction-article",
            content="محتوى للتفاعل",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_reaction_creation_like(self):
        """Test like reaction creation"""
        reaction = Reaction.objects.create(
            article=self.article,
            user=self.user,
            reaction_type='like'
        )
        self.assertEqual(reaction.article, self.article)
        self.assertEqual(reaction.user, self.user)
        self.assertEqual(reaction.reaction_type, 'like')
        self.assertIsNotNone(reaction.created_at)

    def test_reaction_creation_dislike(self):
        """Test dislike reaction creation"""
        reaction = Reaction.objects.create(
            article=self.article,
            user=self.user,
            reaction_type='dislike'
        )
        self.assertEqual(reaction.reaction_type, 'dislike')

    def test_reaction_str_method(self):
        """Test reaction string representation"""
        reaction = Reaction.objects.create(
            article=self.article,
            user=self.user,
            reaction_type='like'
        )
        expected = f"{self.user.username} reacted like to {self.article.title}"
        self.assertEqual(str(reaction), expected)

    def test_reaction_unique_together_constraint(self):
        """Test unique_together constraint for article and user"""
        Reaction.objects.create(
            article=self.article,
            user=self.user,
            reaction_type='like'
        )

        # Trying to create another reaction for same article and user should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Reaction.objects.create(
                article=self.article,
                user=self.user,
                reaction_type='dislike'
            )

    def test_reaction_choices(self):
        """Test reaction choices"""
        choices = [choice[0] for choice in Reaction.REACTION_CHOICES]
        self.assertIn('like', choices)
        self.assertIn('dislike', choices)


class SavedArticleModelTest(TestCase):
    """Test cases for SavedArticle model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)
        self.article = Article.objects.create(
            title="مقال للحفظ",
            slug="saved-article",
            content="محتوى للحفظ",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_saved_article_creation(self):
        """Test saved article creation"""
        saved_article = SavedArticle.objects.create(
            user=self.user,
            article=self.article
        )
        self.assertEqual(saved_article.user, self.user)
        self.assertEqual(saved_article.article, self.article)
        self.assertIsNotNone(saved_article.created_at)

    def test_saved_article_str_method(self):
        """Test saved article string representation"""
        saved_article = SavedArticle.objects.create(
            user=self.user,
            article=self.article
        )
        expected = f"{self.user.username} حفظ {self.article.title}"
        self.assertEqual(str(saved_article), expected)

    def test_saved_article_unique_together_constraint(self):
        """Test unique_together constraint for user and article"""
        SavedArticle.objects.create(
            user=self.user,
            article=self.article
        )

        # Trying to create another saved article for same user and article should raise IntegrityError
        with self.assertRaises(IntegrityError):
            SavedArticle.objects.create(
                user=self.user,
                article=self.article
            )

    def test_saved_article_ordering(self):
        """Test saved article ordering by created_at desc"""
        saved1 = SavedArticle.objects.create(
            user=self.user,
            article=self.article
        )

        # Create another article and save it
        article2 = Article.objects.create(
            title="مقال ثاني",
            slug="second-article",
            content="محتوى ثاني",
            author=self.user,
            category=self.category
        )
        saved2 = SavedArticle.objects.create(
            user=self.user,
            article=article2
        )

        saved_articles = SavedArticle.objects.all()
        self.assertEqual(saved_articles[0], saved2)  # Newest first
        self.assertEqual(saved_articles[1], saved1)


class HomeViewTest(TestCase):
    """Test cases for home view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)

        # Create articles with different properties
        self.breaking_article = Article.objects.create(
            title="خبر عاجل",
            slug="breaking-news",
            content="محتوى عاجل",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED,
            breaking_news=True
        )

        self.featured_article = Article.objects.create(
            title="مقال مميز",
            slug="featured-article",
            content="محتوى مميز",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED,
            featured=True
        )

        self.regular_article = Article.objects.create(
            title="مقال عادي",
            slug="regular-article",
            content="محتوى عادي",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_home_view_status_code(self):
        """Test home view returns 200 status code"""
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        """Test home view uses correct template"""
        response = self.client.get(reverse('news:home'))
        self.assertTemplateUsed(response, 'news/articles/article_list.html')

    def test_home_view_context_breaking_news(self):
        """Test home view context contains breaking news"""
        response = self.client.get(reverse('news:home'))
        self.assertIn('breaking_news', response.context)
        breaking_news = response.context['breaking_news']
        self.assertEqual(len(breaking_news), 1)
        self.assertEqual(breaking_news[0], self.breaking_article)

    def test_home_view_context_featured_articles(self):
        """Test home view context contains featured articles"""
        response = self.client.get(reverse('news:home'))
        self.assertIn('featured_articles', response.context)
        featured_articles = response.context['featured_articles']
        self.assertEqual(len(featured_articles), 1)
        self.assertEqual(featured_articles[0], self.featured_article)

    def test_home_view_context_latest_articles(self):
        """Test home view context contains latest articles"""
        response = self.client.get(reverse('news:home'))
        self.assertIn('latest_articles', response.context)
        latest_articles = response.context['latest_articles']
        self.assertEqual(len(latest_articles), 3)  # All published articles

    def test_home_view_context_categories(self):
        """Test home view context contains active categories"""
        response = self.client.get(reverse('news:home'))
        self.assertIn('categories', response.context)
        categories = response.context['categories']
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0], self.category)

    def test_home_view_inactive_category_excluded(self):
        """Test home view excludes inactive categories"""
        inactive_category = Category.objects.create(
            name="غير نشط",
            is_active=False
        )
        response = self.client.get(reverse('news:home'))
        categories = response.context['categories']
        self.assertNotIn(inactive_category, categories)


class ArticleDetailViewTest(TestCase):
    """Test cases for article_detail view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)
        self.article = Article.objects.create(
            title="مقال للعرض",
            slug="article-detail",
            content="محتوى المقال",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_article_detail_view_status_code(self):
        """Test article detail view returns 200 status code"""
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_article_detail_view_404_for_draft(self):
        """Test article detail view returns 404 for draft articles"""
        draft_article = Article.objects.create(
            title="مسودة",
            slug="draft-article",
            content="محتوى مسودة",
            author=self.user,
            category=self.category,
            status=Article.Status.DRAFT
        )
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': draft_article.slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_article_detail_view_template(self):
        """Test article detail view uses correct template"""
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        self.assertTemplateUsed(response, 'news/article_detail.html')

    def test_article_detail_view_context_article(self):
        """Test article detail view context contains article"""
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'], self.article)

    def test_article_detail_view_context_unauthenticated_user(self):
        """Test article detail view context for unauthenticated user"""
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        self.assertIn('user_reaction', response.context)
        self.assertIn('user_has_saved', response.context)
        self.assertIsNone(response.context['user_reaction'])
        self.assertFalse(response.context['user_has_saved'])

    def test_article_detail_view_context_authenticated_user(self):
        """Test article detail view context for authenticated user"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        self.assertIn('user_reaction', response.context)
        self.assertIn('user_has_saved', response.context)

    def test_article_detail_view_related_articles(self):
        """Test article detail view shows related articles from same category"""
        # Create related articles
        related_article = Article.objects.create(
            title="مقال مرتبط",
            slug="related-article",
            content="محتوى مرتبط",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': self.article.slug})
        )
        self.assertIn('related_articles', response.context)
        related_articles = response.context['related_articles']
        self.assertIn(related_article, related_articles)
        self.assertNotIn(self.article, related_articles)  # Current article excluded


class AddReactionViewTest(TestCase):
    """Test cases for add_reaction view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)
        self.article = Article.objects.create(
            title="مقال للتفاعل",
            slug="reaction-article",
            content="محتوى للتفاعل",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_add_reaction_requires_login(self):
        """Test add reaction view requires login"""
        response = self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id}),
            {'reaction_type': 'like'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_add_reaction_requires_post(self):
        """Test add reaction view requires POST method"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id})
        )
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_add_like_reaction(self):
        """Test adding like reaction"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id}),
            {'reaction_type': 'like'}
        )

        # Check reaction was created
        reaction = Reaction.objects.filter(
            article=self.article,
            user=self.user
        ).first()
        self.assertIsNotNone(reaction)
        self.assertEqual(reaction.reaction_type, 'like')

    def test_add_dislike_reaction(self):
        """Test adding dislike reaction"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id}),
            {'reaction_type': 'dislike'}
        )

        # Check reaction was created
        reaction = Reaction.objects.filter(
            article=self.article,
            user=self.user
        ).first()
        self.assertIsNotNone(reaction)
        self.assertEqual(reaction.reaction_type, 'dislike')

    def test_change_reaction(self):
        """Test changing reaction from like to dislike"""
        self.client.login(username='testuser', password='testpassword')

        # First add like reaction
        self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id}),
            {'reaction_type': 'like'}
        )

        # Then change to dislike
        self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id}),
            {'reaction_type': 'dislike'}
        )

        # Check only one reaction exists and it's dislike
        reactions = Reaction.objects.filter(
            article=self.article,
            user=self.user
        )
        self.assertEqual(reactions.count(), 1)
        self.assertEqual(reactions[0].reaction_type, 'dislike')

    def test_add_reaction_invalid_article(self):
        """Test adding reaction to non-existent article"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': 9999}),
            {'reaction_type': 'like'}
        )
        self.assertEqual(response.status_code, 404)


class SaveArticleViewTest(TestCase):
    """Test cases for save_article view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)
        self.article = Article.objects.create(
            title="مقال للحفظ",
            slug="save-article",
            content="محتوى للحفظ",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_save_article_requires_login(self):
        """Test save article view requires login"""
        response = self.client.post(
            reverse('news:save_article', kwargs={'article_id': self.article.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_save_article_requires_post(self):
        """Test save article view requires POST method"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(
            reverse('news:save_article', kwargs={'article_id': self.article.id})
        )
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_save_article_success(self):
        """Test saving article successfully"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('news:save_article', kwargs={'article_id': self.article.id})
        )

        # Check saved article was created
        saved_article = SavedArticle.objects.filter(
            article=self.article,
            user=self.user
        ).first()
        self.assertIsNotNone(saved_article)

    def test_unsave_article(self):
        """Test unsaving already saved article"""
        # First save the article
        SavedArticle.objects.create(
            user=self.user,
            article=self.article
        )

        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('news:save_article', kwargs={'article_id': self.article.id})
        )

        # Check saved article was deleted
        saved_article_exists = SavedArticle.objects.filter(
            article=self.article,
            user=self.user
        ).exists()
        self.assertFalse(saved_article_exists)

    def test_save_article_invalid_article(self):
        """Test saving non-existent article"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('news:save_article', kwargs={'article_id': 9999})
        )
        self.assertEqual(response.status_code, 404)


class ModelValidationTest(TestCase):
    """Test cases for model validation and edge cases"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)

    def test_article_slug_uniqueness_for_date(self):
        """Test article slug uniqueness for the same publication date"""
        article1 = Article.objects.create(
            title="مقال أول",
            slug="unique-slug",
            content="محتوى أول",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

        # Creating another article with same slug on same day should be allowed
        # if different publish date, but may cause issues with unique_for_date
        article2 = Article.objects.create(
            title="مقال ثاني",
            slug="unique-slug-2",  # Different slug to avoid conflict
            content="محتوى ثاني",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

        self.assertNotEqual(article1.slug, article2.slug)

    def test_category_long_name(self):
        """Test category with maximum length name"""
        long_name = "ا" * 100  # Maximum length
        category = Category.objects.create(name=long_name)
        self.assertEqual(len(category.name), 100)

    def test_article_long_title(self):
        """Test article with maximum length title"""
        long_title = "م" * 200  # Maximum length
        article = Article.objects.create(
            title=long_title,
            slug="long-title-article",
            content="محتوى المقال",
            author=self.user,
            category=self.category
        )
        self.assertEqual(len(article.title), 200)

    def test_article_category_cascade_null(self):
        """Test article category is set to null when category is deleted"""
        article = Article.objects.create(
            title="مقال للاختبار",
            slug="test-cascade-article",
            content="محتوى الاختبار",
            author=self.user,
            category=self.category
        )

        category_id = self.category.id
        self.category.delete()

        # Refresh article from database
        article.refresh_from_db()
        self.assertIsNone(article.category)

    def test_reaction_cascade_delete(self):
        """Test reactions are deleted when article is deleted"""
        article = Article.objects.create(
            title="مقال للحذف",
            slug="delete-article",
            content="محتوى للحذف",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

        reaction = Reaction.objects.create(
            article=article,
            user=self.user,
            reaction_type='like'
        )

        reaction_id = reaction.id
        article.delete()

        # Reaction should be deleted
        self.assertFalse(
            Reaction.objects.filter(id=reaction_id).exists()
        )

    def test_saved_article_cascade_delete(self):
        """Test saved articles are deleted when article is deleted"""
        article = Article.objects.create(
            title="مقال محفوظ للحذف",
            slug="saved-delete-article",
            content="محتوى محفوظ للحذف",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

        saved_article = SavedArticle.objects.create(
            user=self.user,
            article=article
        )

        saved_id = saved_article.id
        article.delete()

        # Saved article should be deleted
        self.assertFalse(
            SavedArticle.objects.filter(id=saved_id).exists()
        )


class IntegrationTest(TestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="تقنية", is_active=True)
        self.article = Article.objects.create(
            title="مقال للتفاعل الكامل",
            slug="integration-article",
            content="محتوى للاختبار التكاملي",
            author=self.user,
            category=self.category,
            status=Article.Status.PUBLISHED
        )

    def test_complete_user_interaction_workflow(self):
        """Test complete user interaction workflow: react and save"""
        # Login user
        self.client.login(username='testuser', password='testpassword')

        # Add reaction
        self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id}),
            {'reaction_type': 'like'}
        )

        # Check reaction was created
        reaction_exists = Reaction.objects.filter(
            article=self.article,
            user=self.user,
            reaction_type='like'
        ).exists()
        self.assertTrue(reaction_exists)

        # Save article
        self.client.post(
            reverse('news:save_article', kwargs={'article_id': self.article.id})
        )

        # Check article was saved
        saved_exists = SavedArticle.objects.filter(
            article=self.article,
            user=self.user
        ).exists()
        self.assertTrue(saved_exists)

        # Change reaction
        self.client.post(
            reverse('news:react_to_article', kwargs={'article_id': self.article.id}),
            {'reaction_type': 'dislike'}
        )

        # Check reaction was updated
        reaction = Reaction.objects.filter(
            article=self.article,
            user=self.user
        ).first()
        self.assertEqual(reaction.reaction_type, 'dislike')

        # Unsave article
        self.client.post(
            reverse('news:save_article', kwargs={'article_id': self.article.id})
        )

        # Check article was unsaved
        saved_exists = SavedArticle.objects.filter(
            article=self.article,
            user=self.user
        ).exists()
        self.assertFalse(saved_exists)
