from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'event_date', 'event_day', 'tag')
    list_filter = ('tag', 'event_date')
    search_fields = ('title', 'description')
