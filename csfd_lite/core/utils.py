from typing import List, Tuple

from unidecode import unidecode

from .models import Actor, Movie


def normalize(text: str) -> str:
    return unidecode(text).lower().strip()


def search(query: str) -> Tuple[List[Movie], List[Actor]]:
    """
    Return movies and actors with name that contain entered query.
    The search is case-insensitive and doesn't care accent.
    """
    if normalized_query := normalize(query):
        return (
            Movie.objects.filter(normalized_name__contains=normalized_query),
            Actor.objects.filter(normalized_name__contains=normalized_query),
        )
    else:
        return [], []
