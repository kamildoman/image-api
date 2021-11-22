from django.contrib import admin
from .models import *

class ImageAdmin(admin.ModelAdmin):
    list_display = ('owner','photo', 'thumbnail', 'thumbnail400')
    fieldsets = (
        (None, {
            'fields': ('owner', 'photo', 'custom_thumbnail')
        }),
        
    )

admin.site.register(User)
admin.site.register(ImageModel, ImageAdmin)
admin.site.register(FetchLink)