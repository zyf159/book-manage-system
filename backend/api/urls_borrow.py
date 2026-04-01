from django.urls import path
from .views import BorrowRecordListCreateView, BorrowRecordDetailView, ReturnBookView, SystemStatusView

urlpatterns = [
    path('', BorrowRecordListCreateView.as_view(), name='borrow-record-list'),
    path('<int:pk>/', BorrowRecordDetailView.as_view(), name='borrow-record-detail'),
    path('<int:pk>/return/', ReturnBookView.as_view(), name='return-book'),
    path('status/', SystemStatusView.as_view(), name='system-status'),
]
