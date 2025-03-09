from .models import Note
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
import hashlib

@require_http_methods(["POST"])
def create_note(request):
    title = request.POST.get("title")
    content = request.POST.get("content", "")
    if title == "":
        title = "[autotitle] " + hashlib.sha1(content.encode("utf-8")).hexdigest()

    if title.startswith("[EDIT] "):
        is_edit = True
        title = title[len("[EDIT] "):]
    else:
        is_edit = False

    if title:
        try:
            note = Note.objects.get(title=title)
            if is_edit:
                note.contents = content
            else:
                note.contents += "\n----\n" + content
            note.save()
        except Note.DoesNotExist:
            Note.objects.create(title=title, contents=content)

    return redirect("/note/")

def note_list(request):
    notes = Note.objects.all().order_by('-modified_time')
    return render(request, 'note/note_list.html', {'notes': notes})

@require_http_methods(["POST"])
def delete_note(request, note_id):
    # Ensure the note exists and delete it
    note = get_object_or_404(Note, id=note_id)
    note.delete()

    # Return a success response
    return JsonResponse({'status': 'success'})
