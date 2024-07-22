from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Review, Book
from django.db.models import Sum

@receiver(post_save, sender=Review)
def calculate_rating(sender, instance, created, **kwargs):
    count = Review.objects.select_related("user", "book").filter(book_id=instance.book_id).count()
    rating = Review.objects.filter(book_id=instance.book_id).aggregate(total_rate=Sum("rating"))['total_rate']
    total = rating / count if rating is not None else 0
    book = instance.book
    book.rate = total
    book.save()

@receiver(post_delete, sender=Review)
def calculate_rating(sender, instance, **kwargs):
    count = Review.objects.select_related("user", "book").filter(book_id=instance.book_id).count()
    rating = Review.objects.filter(book_id=instance.book_id).aggregate(total_rate=Sum("rating"))['total_rate']
    total = rating / count if rating is not None else 0
    book = instance.book
    book.rate = total
    book.save()