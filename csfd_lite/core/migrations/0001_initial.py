# Generated by Django 4.2.7 on 2023-11-06 11:48

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Actor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("normalized_name", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("normalized_name", models.CharField(max_length=200)),
                (
                    "actors",
                    models.ManyToManyField(
                        related_name="movies",
                        related_query_name="movie",
                        to="core.actor",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="actor",
            index=models.Index(
                fields=["normalized_name"], name="core_actor_normali_eb20db_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="movie",
            index=models.Index(
                fields=["normalized_name"], name="core_movie_normali_bfae28_idx"
            ),
        ),
    ]
