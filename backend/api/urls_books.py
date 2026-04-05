from django.urls import path
from .views import BookListCreateView, BookDetailView, CategoryView, CategoryDetailView, ReservationView, ReservationDetailView, NotificationView, NotificationDetailView, TagView, TagDetailView, CommentView, CollectionView

urlpatterns = [
    path('', BookListCreateView.as_view(), name='book-list'),
    path('<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('reservations/', ReservationView.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', ReservationDetailView.as_view(), name='reservation-detail'),
    path('notifications/', NotificationView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('tags/', TagView.as_view(), name='tag-list'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
    path('comments/', CommentView.as_view(), name='comment-list'),
    path('comments/<int:book_id>/', CommentView.as_view(), name='book-comments'),
    path('comments/delete/<int:pk>/', CommentView.as_view(), name='comment-delete'),
    path('collections/', CollectionView.as_view(), name='collection-list'),
    path('collections/<int:book_id>/', CollectionView.as_view(), name='collection-detail'),
]
