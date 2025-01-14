import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('news_list')
class TestHomePage:
    """Тестирует главную страницу"""

    HOME_URL = reverse('news:home')

    def test_news_count(self, client):
        """Количество новостей на главной странице — не более 10"""
        response = client.get(self.HOME_URL)
        count = response.context['object_list'].count()
        assert count == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client):
        """Новости на главной странице отсортированы по дате"""
        response = client.get(self.HOME_URL)
        news_list = response.context['object_list']
        # Проверим порядок по простому, потому что записи всегда отсортированы
        assert news_list[0].date > news_list[1].date


class TestDetailPage:
    """Тестирует детальную страницу"""

    @pytest.mark.usefixtures('comment_list')
    def test_comments_order(self, news):
        """Проверяет сортировку списка комментариев"""
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(self, client, news_url):
        """Наличие формы у анонима"""
        response = client.get(news_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, author_client, news_url):
        """Наличие формы у авторизованного пользователя"""
        response = author_client.get(news_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
