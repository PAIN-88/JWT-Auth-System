from django.urls import path
from .views import FileListView, FileDetailView, FileDownloadView

urlpatterns = [
    path("files", FileListView.as_view()),
    path("files/<uuid:id>", FileDetailView.as_view()),
    path("files/<uuid:id>/download", FileDownloadView.as_view()),
]