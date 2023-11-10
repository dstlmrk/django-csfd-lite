import pytest

from core.models import Actor, Movie
from core.utils import normalize, search


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Mlčení jehňátek", "mlceni jehnatek"),
        ("汉字", "yi zi"),
        ("„Marečku, podejte mi pero!“", ',,marecku, podejte mi pero!"'),
        ("🐍", ""),
    ],
)
def test_normalize(value, expected):
    assert normalize(value) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name,should_find",
    [("Vetřelci", True), ("Vetřelec", False), ("12 opic", False)],
)
def test_search_movies(name, should_find):
    Movie.objects.create(name=name, normalized_name=normalize(name))
    assert bool(search("relci")[0]) == should_find


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name,should_find",
    [("Čafúrin", True), ("Vlastimil Čaněk", True), ("12 opic", False)],
)
def test_search_actors(name, should_find):
    Actor.objects.create(name=name, normalized_name=normalize(name))
    assert bool(search("ČA")[1]) == should_find
