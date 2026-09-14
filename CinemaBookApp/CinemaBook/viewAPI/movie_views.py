from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Movie, Category, MovieFormat, Cinema
from ..serializers import MovieSerializer, CategorySerializer, MovieFormatSerializer, CinemaSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """API Danh sách & Chi tiết Phim"""
    queryset = Movie.objects.all().prefetch_related('categories')
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.GET
        kw = p.get('kw')
        cate_id = p.get('cateId') or p.get('category_id')
        cinema_id = p.get('cinemaId') or p.get('cinema_id')
        show_date = p.get('showDate') or p.get('show_date')
        format_id = p.get('formatId') or p.get('format_id')

        if kw:
            qs = qs.filter(movie_name__icontains=kw)
        if cate_id:
            qs = qs.filter(categories__id=cate_id)
        if cinema_id:
            qs = qs.filter(showtimes__room__cinema_id=cinema_id)
        if show_date:
            qs = qs.filter(showtimes__show_date=show_date)
        if format_id:
            qs = qs.filter(showtimes__room__format_id=format_id)
        return qs.distinct()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API Thể loại phim"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class MovieFormatViewSet(viewsets.ReadOnlyModelViewSet):
    """API Định dạng phim 2D, 3D, IMAX"""
    queryset = MovieFormat.objects.all()
    serializer_class = MovieFormatSerializer
    permission_classes = [permissions.AllowAny]


class CinemaViewSet(viewsets.ReadOnlyModelViewSet):
    """API Chi nhánh Rạp"""
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer
    permission_classes = [permissions.AllowAny]


class MovieListApi(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(MovieSerializer(Movie.objects.all(), many=True).data, status=status.HTTP_200_OK)


class CategoryListApi(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(CategorySerializer(Category.objects.all(), many=True).data, status=status.HTTP_200_OK)
