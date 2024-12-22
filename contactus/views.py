from django.shortcuts import render

# Create your views here.
def contactusPage(request):
    return render(request, 'contactusPage.html')