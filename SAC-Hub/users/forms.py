from django import forms

class BulkUploadForm(forms.Form):
    file = forms.FileField(label="Select CSV or Excel file")
