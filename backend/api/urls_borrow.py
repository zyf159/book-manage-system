from django.urls import path
from .views import BorrowRecordListCreateView, BorrowRecordDetailView, ReturnBookView, SystemStatusView, RenewBookView, OverdueBooksView, BorrowingRankingView, BookRecommendationView, AvailableBooksView, ReservableBooksView

urlpatterns = [
    path('', BorrowRecordListCreateView.as_view(), name='borrow-record-list'),
    path('<int:pk>/', BorrowRecordDetailView.as_view(), name='borrow-record-detail'),
    path('<int:pk>/return/', ReturnBookView.as_view(), name='return-book'),
    path('<int:pk>/renew/', RenewBookView.as_view(), name='renew-book'),
    path('status/', SystemStatusView.as_view(), name='system-status'),
    path('available/', AvailableBooksView.as_view(), name='available-books'),
    path('reservable/', ReservableBooksView.as_view(), name='reservable-books'),
    path('overdue/', OverdueBooksView.as_view(), name='overdue-books'),
    path('ranking/', BorrowingRankingView.as_view(), name='borrowing-ranking'),
    path('recommendations/', BookRecommendationView.as_view(), name='book-recommendations'),
]
