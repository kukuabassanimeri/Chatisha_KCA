from django.contrib import admin
from .models import CustomUser, IssueSubmissionModel, ForwardingHistoryModel, FAQModel

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(IssueSubmissionModel)
admin.site.register(ForwardingHistoryModel)
admin.site.register(FAQModel)