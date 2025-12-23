from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from . import models


from . import dj

def entry_list(request, typ):
    assert typ in models.Entry.ENTRY_TYPES_KEYS
    entries = models.Entry.list(viewer=request.user).filter(entry_type=typ)
    entries = dj.paginate(entries, 10, request)
    return render(request, f'journal/list.html', {
        'entries': entries,
        'active_tab': typ
    })

def blog_list(request):
    return entry_list(request, 'blog')
def topic_list(request):
    return entry_list(request, 'topic')
def archive_list(request):
    return entry_list(request, 'archive')

def tagged_entries(request, tag):
    entries = models.Entry.list(viewer=request.user).filter(tags__icontains=f"t:{tag}")
    entries = dj.paginate(entries, 10, request)
    return render(request, 'journal/list.html', {
        'entries': entries,
        'tag': tag
    })

def search(request):
    query = request.GET.get("q")
    entries = models.Entry.list(viewer=request.user).filter(Q(tags__icontains=query) | Q(content__icontains=query) | Q(title__icontains=query))
    entries = dj.paginate(entries, 10, request)
    return render(request, 'journal/list.html', {
        'entries': entries,
        'orig_query': query,
    })

def entry_slug(request, slug):
    entry = models.Entry.list(viewer=request.user).get(slug=slug)
    if not entry.is_public and (not request.user.is_authenticated or request.user != entry.author):
        return render(request, 'journal/entry_not_found.html', {}, status=403)
    return render(request, 'journal/entry_detail.html', {'entry': entry})

def entry_id(request, entry_id):
    entry = models.Entry.list(viewer=request.user).get(pk=entry_id)
    if not entry.is_public and (not request.user.is_authenticated or request.user != entry.author):
        return render(request, 'journal/entry_not_found.html', {}, status=403)
    return render(request, 'journal/entry_detail.html', {'entry': entry})
