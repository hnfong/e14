from django.shortcuts import render
from django.views.generic import ListView
from .models import Entry

from . import dj

# Specific views for each tab
def blog_list(request):
    entries = Entry.list().filter(entry_type='blog')
    return render(request, 'journal/blog_list.html', {
        'entries': entries,
        'active_tab': 'journal'
    })

def topic_list(request):
    entries = Entry.list().filter(entry_type='topic')
    return render(request, 'journal/topic_list.html', {
        'entries': entries,
        'active_tab': 'topic'
    })

def archive_list(request):
    entries = Entry.list().filter(entry_type='archive')
    return render(request, 'journal/archive_list.html', {
        'entries': entries,
        'active_tab': 'archive'
    })

def tagged_entries(request, tag):
    entries = Entry.list().filter(tags__icontains=f"t:{tag}")
    return render(request, 'journal/tagged_list.html', {
        'entries': entries,
        'tag': tag
    })
