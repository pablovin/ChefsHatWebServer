from django.contrib import admin
from .models import DataSet, Experiment, Rank
#
admin.site.register(Experiment)
admin.site.register(DataSet)
admin.site.register(Rank)


# Register your models here.
