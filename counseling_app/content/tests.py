from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from content.models import Category, Article

class ArticleFileUploadTests(TestCase):
    def setUp(self):
        # Create an admin user to authenticate
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin_test@aura.com',
            password='testpassword'
        )
        self.admin_user.role = 'admin'
        self.admin_user.save()
        
        self.client = Client()
        self.client.login(username='admin_test', password='testpassword')
        
        # Create a category
        self.category = Category.objects.create(name='Test Category', description='Test')
        
    def test_create_article_with_file(self):
        # Mock file
        test_file = SimpleUploadedFile("test_worksheet.pdf", b"file_content", content_type="application/pdf")
        
        # Post multipart form data
        response = self.client.post(reverse('create_article'), {
            'title': 'Test Worksheet',
            'content_type': 'exercise',
            'category_id': self.category.id,
            'body': 'Instructions for test worksheet',
            'video_url': '',
            'file': test_file
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        
        # Verify database
        article = Article.objects.get(id=data['id'])
        self.assertEqual(article.title, 'Test Worksheet')
        self.assertEqual(article.content_type, 'exercise')
        self.assertIsNotNone(article.file)
        if article.file and article.file.name:
            self.assertTrue('test_worksheet' in article.file.name)
            self.assertTrue(article.file.name.endswith('.pdf'))
        
        # Verify detail view response
        detail_response = self.client.get(reverse('article_detail', args=[article.id]))
        self.assertEqual(detail_response.status_code, 200)
        detail_data = detail_response.json()
        file_url = detail_data.get('file_url')
        self.assertIsNotNone(file_url)
        if file_url:
            self.assertTrue('test_worksheet' in file_url)
            self.assertTrue(file_url.endswith('.pdf'))

    def test_edit_article_replace_file(self):
        # Create an article
        article = Article.objects.create(
            title='Initial Article',
            content_type='article',
            category=self.category,
            author=self.admin_user
        )
        
        # Mock first file upload
        test_file1 = SimpleUploadedFile("doc1.txt", b"content1", content_type="text/plain")
        article.file = test_file1
        article.save()
        
        # Modify with new file
        test_file2 = SimpleUploadedFile("doc2.txt", b"content2", content_type="text/plain")
        response = self.client.post(reverse('edit_article', args=[article.id]), {
            'title': 'Updated Title',
            'content_type': 'article',
            'category_id': self.category.id,
            'body': 'Updated Body',
            'video_url': '',
            'file': test_file2
        })
        
        self.assertEqual(response.status_code, 200)
        article.refresh_from_db()
        self.assertEqual(article.title, 'Updated Title')
        self.assertIsNotNone(article.file)
        if article.file and article.file.name:
            self.assertTrue('doc2' in article.file.name)
            self.assertTrue(article.file.name.endswith('.txt'))

    def test_edit_article_clear_file(self):
        # Create article with file
        test_file = SimpleUploadedFile("doc.txt", b"content", content_type="text/plain")
        article = Article.objects.create(
            title='Article With File',
            content_type='article',
            category=self.category,
            file=test_file,
            author=self.admin_user
        )
        
        # Call edit view with clear_file = true
        response = self.client.post(reverse('edit_article', args=[article.id]), {
            'title': 'Article With File',
            'content_type': 'article',
            'category_id': self.category.id,
            'clear_file': 'true'
        })
        
        self.assertEqual(response.status_code, 200)
        article.refresh_from_db()
        self.assertFalse(article.file)  # Should be empty/None
