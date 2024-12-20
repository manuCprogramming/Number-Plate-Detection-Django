from django.db import models

class LicensePlate(models.Model):
    plate_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    rc_number = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    age = models.IntegerField()
    vehicle_type = models.CharField(max_length=50)
    vehicle_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    aadhar_number = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='license_images/', null=True, blank=True)

    def __str__(self):
        return self.plate_number
