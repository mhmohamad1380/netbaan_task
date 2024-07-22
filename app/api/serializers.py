from users.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from book.models import Book, Review

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=32,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        required=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']
        if password != password2:
            raise serializers.ValidationError("Password Error: two passwords must be the same!")
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

    def to_representation(self, instance):
        data = {}
        data['id'] = instance['pk']
        data['title'] = instance['title']
        data['author_id'] = instance['author_id']
        data['genre'] = {
            "id": instance['genre_id'],
            "title": instance['genre_title']
        }
        data['rating'] = instance['rating']
        return data
    
class ReviewSerializer(serializers.ModelSerializer):
    rate = serializers.IntegerField(required=True)
    book_id = serializers.IntegerField(required=True)

    class Meta:
        model = Review
        fields = ['rate', 'book_id']

    def request(self):
        return self.context['request']

    def create(self, validated_data):
        request = self.request()
        rate = validated_data['rate']
        book_id = validated_data['book_id']
        if rate > 5 or rate < 0:
            raise serializers.ValidationError("rate must be between 0 and 5!")

        if Review.objects.select_related("user", "book").filter(book_id=book_id, user_id=request.user.id).exists():
            raise serializers.ValidationError("You already voted this book!")
        review = Review.objects.create(rating=rate, book_id=book_id, user_id=request.user.id)
        return review
    
    def update(self, instance, validated_data):
        rate = validated_data['rate']
        if rate > 5 or rate < 0:
            raise serializers.ValidationError("rate must be between 0 and 5!")
        instance.rating = rate
        instance.save()
        return instance

        
        

