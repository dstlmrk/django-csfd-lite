from collections import defaultdict
from time import sleep
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from core.models import Actor, Movie
from core.utils import normalize
from django.core.management.base import BaseCommand
from tqdm import tqdm

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
    def parse_actors(detail_soup: BeautifulSoup) -> List[str]:
        """
        Returns list of actors names
        """
        links = detail_soup.find("h4", string="Hrají:").parent.select("a[href*=tvurce]")
        return [link.text for link in links]

    def handle(self, *args, **options):
        self.clear_database()
        actors_ids = {}

        with tqdm(total=299) as pbar:
            for page in ["", "?from=100", "?from=200"]:
                # clear for every page
                actors_set = set()
                actors_in_movies = defaultdict(list)

                # scrape the web
                list_soup = self.get_soap(
                    URL.format("/zebricky/filmy/nejlepsi{}".format(page))
                )
                for movie_name, url_path in self.parse_movies(list_soup):
                    detail_soup = self.get_soap(URL.format(url_path))
                    for actor_name in self.parse_actors(detail_soup):
                        actors_in_movies[movie_name].append(actor_name)
                        if actor_name not in actors_ids:
                            actors_set.add(actor_name)
                    pbar.update(1)

                # bulk create for movies and actors
                db_movies = Movie.objects.bulk_create(
                    objs=[
                        Movie(name=movie, normalized_name=normalize(movie))
                        for movie in actors_in_movies.keys()
                    ]
                )
                db_actors = Actor.objects.bulk_create(
                    objs=[
                        Actor(name=actor, normalized_name=normalize(actor))
                        for actor in actors_set
                    ],
                )

                # save ids from actors (dict because of fast access)
                actors_ids.update({actor.name: actor.id for actor in db_actors})

                # prepare m2m table
                m2m = []
                for movie in db_movies:
                    for actor_in_movie in actors_in_movies[movie.name]:
                        m2m.append((movie.id, actors_ids[actor_in_movie]))

                # bulk create for m2m relation
                Movie.actors.through.objects.bulk_create(
                    objs=[
                        Movie.actors.through(movie_id=pair[0], actor_id=pair[1])
                        for pair in m2m  # pair = (movie_id, actor_id)
                    ],
                )

        self.stdout.write(self.style.SUCCESS("Successfully downloaded"))
