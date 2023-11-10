import re
import time

import pytest
from django.core.management import call_command

from core.models import Actor, Movie

HTML_MOVIES = """
    <a href="/film/2294-vykoupeni-z-veznice-shawshank/" class="film-title-name">
        Vykoupení z věznice Shawshank
    </a>
    <a href="/film/10135-forrest-gump/" class="film-title-name">
        Forrest Gump
    </a>
"""

HTML_ACTORS = """
    <div>
        <h4>Hrají:</h4>
            <a href="/tvurce/103-tim-robbins/">Tim Robbins</a>
        <span class="more-member-1">
            <a href="/tvurce/37545-neil-giuntoli/">Neil Giuntoli</a>
        </span>
        <span class="more-member-1">
            <a href="/tvurce/99999-neil-giuntoli/">Neil Giuntoli</a>
        </span>
    </div>
"""


@pytest.mark.django_db
def test_command(monkeypatch, requests_mock):
    monkeypatch.setattr(time, "sleep", lambda x: None)  # save time
    requests_mock.get(
        re.compile("https://www.csfd.cz/zebricky/filmy/nejlepsi"),
        text=HTML_MOVIES,
    )
    requests_mock.get(
        re.compile("https://www.csfd.cz/film/*"),
        text=HTML_ACTORS,
    )

    call_command("download_top300_movies")

    movie = Movie.objects.first()

    assert movie.name == "Vykoupení z věznice Shawshank"
    assert movie.normalized_name == "vykoupeni z veznice shawshank"
    assert {actor.csfd_id for actor in movie.actors.all()} == {"103", "37545", "99999"}
    assert Actor.objects.count() == 3
