from time import sleep
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from tqdm import tqdm

from core.models import Actor, Movie
from core.utils import normalize

URL = "https://www.csfd.cz{}"


class Command(BaseCommand):
    help = (
        "Remove all data in the DB, download TOP 300 movies and"
        " related actors from csfd.cz and store them in the database."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "User-Agent": (  # resource rejects request without user agent
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
            )
        }

    def get_soap(self, url: str) -> BeautifulSoup:
        r = requests.get(url, headers=self.headers)
        sleep(0.5)  # act responsibly
        return BeautifulSoup(r.text, "html.parser")

    @staticmethod
    def clear_database() -> None:
        Movie.objects.all().delete()
        Actor.objects.all().delete()

    @staticmethod
    def parse_movies(list_soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Return list of tuples with movies names and their path url
        """
        links = list_soup.select(".film-title-name")
        return [(link.text.strip(), link["href"]) for link in links]

    @staticmethod
    def parse_actors(detail_soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Returns list of actors names and their CSFD identifier
        """
        links = detail_soup.find("h4", string="Hrají:").parent.select("a[href*=tvurce]")
        return [
            (link.text, link["href"].removeprefix("/tvurce/").split("-")[0])
            for link in links
        ]

    def handle(self, *args, **options):
        self.clear_database()

        movie_id = actor_id = 0
        movies = {}
        actors = {}

        with tqdm(total=299) as pbar:
            for page in ["", "?from=100", "?from=200"]:
                # scrape the web
                list_soup = self.get_soap(
                    URL.format("/zebricky/filmy/nejlepsi{}".format(page))
                )
                for movie_name, url_path in self.parse_movies(list_soup):
                    detail_soup = self.get_soap(URL.format(url_path))
                    actors_in_movie = []
                    for actor_name, actor_csfd_id in self.parse_actors(detail_soup):
                        if actor_csfd_id in actors.keys():
                            actors_in_movie.append(actors[actor_csfd_id]["id"])
                        else:
                            actor_id += 1
                            actors[actor_csfd_id] = {"id": actor_id, "name": actor_name}
                            actors_in_movie.append(actor_id)
                    movie_id += 1
                    movies[movie_id] = {"name": movie_name, "actors": actors_in_movie}
                    pbar.update(1)

            # bulk create for movies and actors
            Movie.objects.bulk_create(
                [
                    Movie(
                        id=id_,
                        name=movie["name"],
                        normalized_name=normalize(movie["name"]),
                    )
                    for id_, movie in movies.items()
                ]
            )
            Actor.objects.bulk_create(
                [
                    Actor(
                        id=actor["id"],
                        csfd_id=csfd_id,
                        name=actor["name"],
                        normalized_name=normalize(actor["name"]),
                    )
                    for csfd_id, actor in actors.items()
                ],
            )

            # prepare m2m table
            m2m = []
            for movie_id, movie in movies.items():
                for actor_id in movie["actors"]:
                    m2m.append(
                        Movie.actors.through(movie_id=movie_id, actor_id=actor_id)
                    )

            # bulk create for m2m relation
            Movie.actors.through.objects.bulk_create(m2m)

        self.stdout.write(self.style.SUCCESS("Successfully downloaded"))
