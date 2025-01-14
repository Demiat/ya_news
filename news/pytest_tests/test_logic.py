from http import HTTPStatus

from pytest import mark
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import (
    COMMENT_TEXT,
    COMMENT_FORM_DATA,
    NEW_COMMENT_TEXT,
)

pytestmark = mark.django_db

def test_anonymous_user_cant_create_comment(client, news_url):
    """Аноним комментарий создать не может"""
    client.post(news_url, data=COMMENT_FORM_DATA)
    assert Comment.objects.count() == 0

def test_user_can_create_comment(author_client, author, news, news_url):
    """Пользователь может создать комментарий"""
    response = author_client.post(news_url, data=COMMENT_FORM_DATA)
    # Проверим переход к якорю комментариев
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == 1  # Комментарий создан?
    # Тогда проверим атрибуты
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author

def test_user_cant_use_bad_words(author_client, news_url):
    """Отказывает публиковать комментарий со словами из стоп-листа"""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(response, 'form', 'text', errors=WARNING)
    # Дополнительно убедимся, что комментарий не был создан.
    assert Comment.objects.count() == 0

def test_author_can_delete_comment(author_client, delete_url, news_url):
    """Автор может удалить свой комментарий"""
    response = author_client.delete(delete_url)
    # Проверим переход к якорю комментариев
    assertRedirects(response, f'{news_url}#comments')
    # Ожидаем ноль комментариев в системе.
    assert  Comment.objects.count() == 0

def test_reader_cant_delete_comment_of_another_user(reader_client, delete_url):
    """Пользователь не может удалить чужой комментарий"""
    response = reader_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    assert Comment.objects.count() == 1

def test_author_can_edit_comment(author_client, news_url, edit_url):
    """Автор может редактировать свой комментарий"""
    # Установим новый текст комментария
    response = author_client.post(edit_url, data={'text': NEW_COMMENT_TEXT})
    # Проверяем, что сработал редирект.
    assertRedirects(response, f'{news_url}#comments')
    # Проверим новое значение
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT

def test_reader_cant_edit_comment_of_another_user(reader_client, edit_url):
    """Пользователь не может редактировать чужой комментарий"""
    response = reader_client.post(edit_url, data={'text': NEW_COMMENT_TEXT})
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Проверим значение
    comment = Comment.objects.get()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == COMMENT_TEXT