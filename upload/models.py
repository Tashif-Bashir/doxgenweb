# upload/models.py
from django.db import models
from django.conf import settings


class ProjectUpload(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=100)
    session_id = models.CharField(max_length=100, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def docs_url(self):
        return f'/media/uploads/{self.session_id}/docs/html/index.html'
