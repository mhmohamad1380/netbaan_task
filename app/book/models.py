from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from django.core.exceptions import ValidationError


class Book(models.Model):
    title = models.CharField(max_length=128, null=True, blank=False)
    author = models.ForeignKey(to="users.User", on_delete=models.CASCADE, null=True, blank=False)
    genre = models.ForeignKey(to="Genre", on_delete=models.CASCADE, null=True, blank=False)
    rate = models.IntegerField(default=0, blank=False, validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self) -> str:
        return self.title

class Genre(models.Model):
    title = models.CharField(max_length=128, null=True, blank=False)

    def __str__(self) -> str:
        return self.title
    
class Review(models.Model):
    book = models.ForeignKey(to="Book", on_delete=models.CASCADE, null=True, blank=False)
    user = models.ForeignKey(to="users.User", on_delete=models.CASCADE, null=True, blank=False) 
    rating = models.IntegerField(blank=False, null=True, validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self) -> str:
        return f"{self.user.username} | {self.book.title} | {self.rating}"
    
    def save(self, *args, **kwargs):
        if Review.objects.select_related("user", "book").filter(Q(user_id=self.user_id) & Q(book_id=self.book_id) & ~Q(pk=self.pk)).exists():
            return ValidationError("You have already voted!") 
        return super().save(*args, **kwargs)