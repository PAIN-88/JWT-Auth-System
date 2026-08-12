from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404

from .models import UserFile
from .serializers import UserFileSerializer


class FileListView(generics.ListAPIView):
    serializer_class = UserFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
       
        return UserFile.objects.filter(owner=self.request.user)


class FileDetailView(generics.RetrieveAPIView):
    serializer_class = UserFileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return UserFile.objects.filter(owner=self.request.user)



class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user_file = UserFile.objects.get(owner=request.user, id=id)
        except UserFile.DoesNotExist:
            raise Http404

        return FileResponse(
            user_file.file.open("rb"),
            as_attachment=True,
            filename=user_file.file_name,
        )