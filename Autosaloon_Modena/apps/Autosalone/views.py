from django.shortcuts import render

# Create your views here.
def home(request):
    """
    Render the home page of the Autosalone application.
    """
    return render(request, 'Autosalone/home.html')