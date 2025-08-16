from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from .models import Quote

staff_required = staff_member_required()
def quote_list(request):
    quotes = Quote.objects.all().order_by('-create_time')
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})

@require_POST
@staff_required
def add_quote(request):
    content = request.POST.get('content')
    source = request.POST.get('source', '')
    if content:
        Quote.objects.create(content=content, source=source)
    return redirect('quotes:quote_list')

@require_POST
@staff_required
def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    quote.delete()
    return redirect('quotes:quote_list')
