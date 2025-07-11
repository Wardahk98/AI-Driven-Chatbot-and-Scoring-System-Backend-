# from django.contrib import admin
# from .models import Question
#
# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'competencies','text', 'type', 'is_open_ended')
from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'competencies', 'text', 'type', 'is_open_ended', 'is_active')
    list_filter = ('type', 'competencies', 'is_open_ended', 'is_active')
    search_fields = ('text', 'competencies')
    list_editable = ('is_active',)
    ordering = ('id',)
