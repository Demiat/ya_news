import pytest
from datetime import datetime, timedelta

from django.utils import timezone
from django.test import Client
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def news():
    """Создает 1 новость"""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture()
def news_list():
    """Создает список новостей"""
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def author(django_user_model):
    """Создает автора"""
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    """Создает читателя"""
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def comment(news, author):
    """Создает комментарий"""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def author_client(author):
    """Логинит автора"""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Логинит читателя"""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture()
def comment_list(news, author):
    """Создает список комментариев"""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
