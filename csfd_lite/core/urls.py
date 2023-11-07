from django.urls import path

from .views import ActorView, MovieView, index

urlpatterns = [
    path("", index, name="index"),
    path("movie/<int:pk>/", MovieView.as_view(), name="movie"),
    path("actor/<int:pk>/", ActorView.as_view(), name="actor"),
]
