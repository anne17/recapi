"""General parser class (abstract)."""

import requests

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class GeneralParser(ABC):
    """Abstract parser class."""

    base_url = ""

    def make_soup(self):
        """Get HTML and create BeautifulSoup object."""
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.text, "html.parser")

    @abstractmethod
    def get_title(self):
        """Get recipe title."""
        pass

    @abstractmethod
    def get_image(self):
        """Get recipe main image."""
        pass

    @abstractmethod
    def get_ingredients(self):
        """Get recipe ingredients list."""
        pass

    @abstractmethod
    def get_contents(self):
        """Get recipe description."""
        pass
