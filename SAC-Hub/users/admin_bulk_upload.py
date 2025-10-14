from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .forms import BulkUploadForm
import csv
import io

@staff_member_required
def bulk_upload_view(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            decoded_file = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
            # Example: handle user data upload
            from .models import User
            created, errors = 0, 0
            for row in reader:
                try:
                    User.objects.create(
                        username=row.get('username'),
                        email=row.get('email'),
                        roll_no=row.get('roll_no'),
                        # Add more fields as needed
                    )
                    created += 1
                except Exception as e:
                    errors += 1
            messages.success(request, f"Bulk upload complete: {created} created, {errors} errors.")
            return redirect('admin:bulk-upload')
    else:
        form = BulkUploadForm()
    return render(request, 'admin/bulk_upload.html', {'form': form})

