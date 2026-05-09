from django.shortcuts import render
from .core_logic import get_trends_briefing
from .forms import InterestForm

def homepage(request):
    form = InterestForm()
    trends_data = get_trends_briefing()
    return render(request, 'trends/index.html', {'trends': trends_data, 'form': form})
