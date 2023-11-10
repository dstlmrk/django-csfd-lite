from django.db import models


class Actor(models.Model):
    csfd_id = models.CharField(
        max_length=200,
        null=False,
        unique=True,
    )
    name = models.CharField(
        max_length=200,
        null=False,
        unique=False,
    )
    normalized_name = models.CharField(
        max_length=200,
        null=False,
        unique=False,
    )

    class Meta:
        indexes = [models.Index(fields=["normalized_name"])]

    def __str__(self):
        return self.name


class Movie(models.Model):
    name = models.CharField(
        max_length=200,
        null=False,
        unique=False,
    )
    normalized_name = models.CharField(
        max_length=200,
        null=False,
        unique=False,
    )
    actors = models.ManyToManyField(
        Actor,
        related_name="movies",
        related_query_name="movie",
    )

    class Meta:
        indexes = [models.Index(fields=["normalized_name"])]

    def __str__(self):
        return self.name
