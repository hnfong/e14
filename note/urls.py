from django.urls import path
from . import views

app_name = 'note'

urlpatterns = [
    path("", views.note_list, name="note_list"),
    path("create/", views.create_note, name="create_note"),
    path("delete/<int:note_id>/", views.delete_note, name="delete_note"),
    path("public/<int:note_id>/", views.public_note, name="public_note"),
]
