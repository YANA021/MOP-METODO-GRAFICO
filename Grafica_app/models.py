from django.db import models

class ProblemaPL(models.Model):
    OBJETIVO_CHOICES = [
        ('max', 'Maximizar'),
        ('min', 'Minimizar'),
    ]

    objetivo = models.CharField(max_length=3, choices=OBJETIVO_CHOICES)
    coef_x1 = models.FloatField()
    coef_x2 = models.FloatField()
    restricciones = models.JSONField()

    def __str__(self):
        return f"PL {self.get_objetivo_display()}"
