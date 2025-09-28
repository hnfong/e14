from django.shortcuts import render
from django.views.generic import ListView
from .models import Entry

class EntryListView(ListView):
    model = Entry
    template_name = 'journal/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        entries = Entry.objects.filter(entry_type=self.kwargs['entry_type'])
        return entries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entry_type'] = self.kwargs['entry_type']
        context['active_tab'] = self.kwargs['entry_type']
        return context

# Specific views for each tab
def blog_list(request):
    entries = Entry.objects.filter(entry_type='journal')
    return render(request, 'journal/blog_list.html', {
        'entries': entries,
        'active_tab': 'journal'
    })

def comment_list(request):
    entries = Entry.objects.filter(entry_type='comment')
    return render(request, 'journal/comment_list.html', {
        'entries': entries,
        'active_tab': 'comment'
    })

def archival_list(request):
    entries = Entry.objects.filter(entry_type='archival')
    return render(request, 'journal/archival_list.html', {
        'entries': entries,
        'active_tab': 'archival'
    })
