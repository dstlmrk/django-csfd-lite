from django.shortcuts import render
from django.views import generic

from .models import Actor, Movie
from .utils import search


def index(request):
    query = request.GET.get("q", "")
    movies, actors = search(query)
    return render(
        request,
        "core/index.html",
        context=dict(query=query, movies=movies, actors=actors),
    )


class MovieView(generic.DetailView):
    model = Movie


class ActorView(generic.DetailView):
    model = Actor
