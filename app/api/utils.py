from django.db.models import F, Case, When, Q
from book.models import Book

class BookUtils:
    def basic_book_query(self, request):
        return Book.objects.select_related("author").annotate(
            genre_title=F("genre__title"),
            rating=Case(
                When(
                    (
                        Q(review__user_id=request.user.id) &
                        Q(review__book_id=F("pk"))
                    ), then=F("review__rating")
                ), default=None
            ),
        ).values("title", "pk", "genre_title", "rating", "author_id", "genre_id")