from django.shortcuts import render

def home(request):
    context = {
        'title': 'Welcome to CRM System',
        # Add any additional context data here
    }
    return render(request, 'home.html', context)