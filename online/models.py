from django.db import models
#weatherId class store stationid of particular station
class WeatherId(models.Model):
    stationId = models.CharField(max_length=30, blank=True, null=True)
    #city_id = models.CharField(max_length=30, blank=True, null=True)
    #class Meta:
    #    ordering = ('city_name')
