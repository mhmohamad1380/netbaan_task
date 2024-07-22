from .serializers import RegisterSerializer, LoginSerializer, BooksSerializer, ReviewSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from book.models import Review
from django.db.models import F, Q
from .utils import BookUtils
from .pagination import BasicPaginator
from django.conf import settings
from collections import Counter
from rest_framework.permissions import AllowAny



class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": str(token.key),
                    "user": serializer.data
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "token": str(token.key),
                    }
                )
            return Response(
                {
                    "error": "Invalid Credentials!" 
                }, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BooksAPIView(APIView):
    serializer_class = BooksSerializer
    pagination_class = BasicPaginator

    def get(self, request):
        books = BookUtils()
        books = books.basic_book_query(request)

        paginate = self.pagination_class()
        paginate_queryset = paginate.paginate_queryset(books, request)
        serializer = self.serializer_class(paginate_queryset, many=True)
        return paginate.get_paginated_response(serializer.data)

class BookFilterAPIView(APIView):
    serializer_class = BooksSerializer
    pagination_class = BasicPaginator

    def get(self, request):
        if not "genre" in request.GET:
            return Response(
                {
                    "error": "please provide genre id!"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        books = BookUtils()
        books = books.basic_book_query(request).filter(Q(genre_id=request.GET.get("genre")))

        paginate = self.pagination_class()
        paginate_queryset = paginate.paginate_queryset(books, request)
        serializer = self.serializer_class(paginate_queryset, many=True)
        return paginate.get_paginated_response(serializer.data)
    

class ReviewAddAPIView(APIView):
    serializer_class = ReviewSerializer
    required_fields = ['book_id', 'rate',]

    def post(self, request):
        if not all(fields in request.data for fields in self.required_fields):
            return Response(
                {
                    "error": f"please provide following fields: {self.required_fields}!"
                }
            )
        
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            review = serializer.save()
            return Response(
                {
                    "message": "Successfully created!",
                    "review": review.pk
                }, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewUpdateAPIView(APIView):
    serializer_class = ReviewSerializer
    required_fields = ['book_id', 'rate']

    def put(self, request):
        if not all(field in request.data for field in self.required_fields):
            return Response(
                {
                    "error": f"please provide following fields: {self.required_fields}!"
                }
            )
        
        book_id = request.data.get("book_id")
        review = Review.objects.select_related("user", "book").filter(book_id=book_id, user_id=self.request.user.id)
        if not review.exists():
            return Response(
                {
                    "error": "this review does not exist!"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        review = review.first()

        serializer = self.serializer_class(review, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "message": "Updated successfully!",
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDeleteAPIView(APIView):
    required_fields = ["book_id"]

    def delete(self, request):
        if not all(field in request.data for field in self.required_fields):
            return Response(
                {
                    "error": f"please provide following fields: {self.required_fields}!"
                }
            )

        book_id = request.data.get("book_id")
        review = Review.objects.select_related("user", "book").filter(book_id=book_id, user_id=self.request.user.id)
        if not review.exists():
            return Response(
                {
                    "error": "this review does not exist!"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SuggestionScenarioByGenre(APIView):
    serializer_class = BooksSerializer
    pagination_class = BasicPaginator

    def get(self, request):
        print(request.user.id)
        reviews = Review.objects.select_related("user", "book").filter(user_id=request.user.id, rating__gte=settings.MINIMUM_RATE_FOR_SUGGESTION).annotate(
            genre_id=F("book__genre_id"),
        ).values("genre_id")

        genres = [genre['genre_id'] for genre in reviews]
        counter = Counter(genres)
        most_common = counter.most_common(1)

        if most_common:
            genre_id, count = most_common[0]
            books = BookUtils()
            books = books.basic_book_query(request).filter(genre_id=genre_id)

            paginate = self.pagination_class()
            paginate_queryset = paginate.paginate_queryset(books, request)
            serializer = self.serializer_class(paginate_queryset, many=True)
            return paginate.get_paginated_response(serializer.data)
        else:
            return Response(
                {
                    "error": "there is not enough data about you!"
                }, status=status.HTTP_404_NOT_FOUND
            )

