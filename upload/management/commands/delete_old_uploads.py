import os
import shutil
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from upload.models import ProjectUpload
from django.conf import settings

class Command(BaseCommand):
    help = 'Deletes uploaded projects older than 3 days'

    def handle(self, *args, **kwargs):
        threshold = timezone.now() - timedelta(days=3)
        old_uploads = ProjectUpload.objects.filter(uploaded_at__lt=threshold)

        for upload in old_uploads:
            path = os.path.join(settings.MEDIA_ROOT, 'uploads', upload.session_id)
            if os.path.exists(path):
                shutil.rmtree(path)
                self.stdout.write(f'Deleted: {path}')
            else:
                self.stdout.write(f'Path not found: {path}')
            upload.delete()

        self.stdout.write(self.style.SUCCESS('Old uploads cleanup complete.'))
