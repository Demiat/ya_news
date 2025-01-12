from http import HTTPStatus

from django.urls import reverse
from pytest import mark, lazy_fixture


@mark.django_db
@mark.parametrize(
    'revers_name, args',
    (
        ('news:home', None),
        ('news:detail', lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous_user(client, revers_name, args):
    """Доступ к страницам анонимным пользователем"""
    response = client.get(reverse(revers_name, args=args))
    assert response.status_code == HTTPStatus.OK


@mark.parametrize(
    'client, status',
    (
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@mark.parametrize(
    'reverse_name',
    ('news:edit', 'news:delete'),
)
def test_page_edit_and_delete_comment(client, status, reverse_name, comment):
    """Доступ к страницам редактирования и удаления комментария"""
    url = reverse(reverse_name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == status
