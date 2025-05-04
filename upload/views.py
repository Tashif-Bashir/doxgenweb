import os
import uuid
import zipfile
import subprocess

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import ProjectUpload

BASE_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')


def home(request):
    """
    Home page:
    - Shows dashboard if user is authenticated
    - Shows hero CTA if user is not
    """
    uploads = ProjectUpload.objects.filter(user=request.user).order_by('-uploaded_at') if request.user.is_authenticated else []
    return render(request, 'upload/home.html', {'uploads': uploads})


@login_required
def upload_cpp_project(request):
    """
    Handles uploading and processing of a C++ ZIP project using Doxygen.
    """
    if request.method == 'POST':
        uploaded_zip = request.FILES['project_zip']
        project_name = uploaded_zip.name
        session_id = str(uuid.uuid4())

        session_path = os.path.join(BASE_UPLOAD_DIR, session_id)
        code_dir = os.path.join(session_path, 'code')
        doc_dir = os.path.join(session_path, 'docs')

        os.makedirs(code_dir, exist_ok=True)
        os.makedirs(doc_dir, exist_ok=True)

        # Save and unzip
        zip_path = os.path.join(code_dir, 'project.zip')
        with open(zip_path, 'wb') as f:
            for chunk in uploaded_zip.chunks():
                f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(code_dir)

        # Create Doxyfile
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

        # Save to DB
        ProjectUpload.objects.create(
            user=request.user,
            project_name=project_name,
            session_id=session_id
        )

        return render(request, 'upload/open_docs.html', {
            'docs_url': f'/media/uploads/{session_id}/docs/html/index.html'
        })

    return render(request, 'upload/upload.html')


@login_required
def user_dashboard(request):
    """
    Legacy dashboard view — may no longer be used if shown in home.html.
    """
    uploads = ProjectUpload.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'upload/dashboard.html', {'uploads': uploads})


@login_required
def serve_docs(request, folder):
    """
    Redirects to generated documentation static HTML.
    """
    return redirect(f'/media/uploads/{folder}/docs/html/index.html')
