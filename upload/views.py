import os
import uuid
import zipfile
import subprocess
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from urllib.parse import unquote
from django.http import FileResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import ProjectUpload
from django.contrib.auth.decorators import login_required

BASE_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')

def home(request):
    return render(request, 'upload/home.html')

import os
import uuid
import zipfile
import subprocess
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import ProjectUpload

BASE_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')

@login_required
def upload_cpp_project(request):
    if request.method == 'POST':
        uploaded_zip = request.FILES['project_zip']
        project_name = uploaded_zip.name
        session_id = str(uuid.uuid4())

        session_path = os.path.join(BASE_UPLOAD_DIR, session_id)
        code_dir = os.path.join(session_path, 'code')
        doc_dir = os.path.join(session_path, 'docs')

        os.makedirs(code_dir, exist_ok=True)
        os.makedirs(doc_dir, exist_ok=True)

        # Save and unzip the uploaded file
        zip_path = os.path.join(code_dir, 'project.zip')
        with open(zip_path, 'wb') as f:
            for chunk in uploaded_zip.chunks():
                f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(code_dir)

        # Create a Doxyfile dynamically
        doxyfile_path = os.path.join(session_path, 'Doxyfile')
        with open(doxyfile_path, 'w') as f:
            f.write(f"""
PROJECT_NAME = "{project_name}"
OUTPUT_DIRECTORY = {doc_dir}
INPUT = {code_dir}
RECURSIVE = YES
GENERATE_HTML = YES
GENERATE_LATEX = NO
EXTRACT_ALL = YES
QUIET = YES
""")

        # Run Doxygen
        subprocess.run(['doxygen', doxyfile_path])

        # Save project metadata in DB
        ProjectUpload.objects.create(
            user=request.user,
            project_name=project_name,
            session_id=session_id
        )

        # Redirect to the generated documentation
        # return redirect(f'/media/uploads/{session_id}/docs/html/index.html')
        return render(request, 'upload/open_docs.html', {
              'docs_url': f'/media/uploads/{session_id}/docs/html/index.html'
          })

    return render(request, 'upload/upload.html')

def user_dashboard(request):
    uploads = ProjectUpload.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'upload/dashboard.html', {'uploads': uploads})

def serve_docs(request, folder):
    # No longer used for direct HTML streaming; handled via static path
    return redirect(f'/media/uploads/{folder}/docs/html/index.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'upload/register.html', {'form': form})