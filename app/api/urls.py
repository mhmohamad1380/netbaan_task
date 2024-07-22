from django.urls import path
from .views import BooksAPIView, LoginAPIView, RegisterAPIView, BookFilterAPIView, ReviewAddAPIView, ReviewUpdateAPIView, ReviewDeleteAPIView, SuggestionScenarioByGenre


urlpatterns = [
    path("book/list/", BooksAPIView.as_view()),
    path("book/", BookFilterAPIView.as_view()),
    path("suggest/", SuggestionScenarioByGenre.as_view()),
    path("login/", LoginAPIView.as_view()),
    path("register/", RegisterAPIView.as_view()),
    path("review/add/", ReviewAddAPIView.as_view()),
    path("review/update/", ReviewUpdateAPIView.as_view()),
    path("review/delete/", ReviewDeleteAPIView.as_view()),
]
