from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import News, Comment

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

    def test_pages_availability(self):
        urls = (
            ('news:home', None),
            ('news:detail', (self.news.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        # Итерируемся по внешнему кортежу
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_pages(self):
        urls = (
            ('news:detail', (self.comment.id,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
