from django.contrib import admin
from .models import CustomUser, IssueSubmissionModel, ForwardingHistoryModel

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(IssueSubmissionModel)
admin.site.register(ForwardingHistoryModel)