from django.shortcuts import render
from .models import CourseModel
from django.http import FileResponse
from django.contrib.auth.decorators import login_required

@login_required
def courseListPage(request):
    data = CourseModel.objects.all().order_by("-pk")
    return render(request, 'coursePage.html',{"data":data})

def downloadFile(requese, pk):
    pdf_file = CourseModel.objects.get(pk=pk)
    resp = FileResponse(pdf_file.file)
    resp['Content-Disposition'] = f'attachment; filename="{pdf_file.file.name}"'
    return resp
    