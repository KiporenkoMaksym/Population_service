import abc
import httpx
from bs4 import BeautifulSoup
import re


class BaseParser(abc.ABC):
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def fetch_html(self) -> str:
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            response = await client.get(self.url, timeout=30)
            response.raise_for_status()
            return response.text

    @abc.abstractmethod
    async def parse(self) -> list[dict]:
        """Повертає список словників: [{'country': ..., 'region': ..., 'population': ...}]"""
        pass


class WikipediaParser(BaseParser):
    def __init__(self):
        super().__init__(
            "https://en.wikipedia.org/w/index.php?title=List_of_countries_by_population_(United_Nations)&oldid=1215058959")

    async def parse(self) -> list[dict]:
        html = await self.fetch_html()
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", {"class": "wikitable"})

        results = []
        if not table:
            return results

        for row in table.find_all("tr")[2:]:
            cols = row.find_all(["td", "th"])
            if len(cols) < 5:
                continue

            for sup in cols[0].find_all("sup"):
                sup.decompose()

            link = cols[0].find("a")
            if link:
                country = link.get_text(strip=True)
            else:
                country = cols[0].get_text(" ", strip=True)

            country = re.sub(r"\[.*?\]", "", country).strip()

            region = cols[4].get_text(strip=True)
            pop_text = cols[2].get_text(strip=True).replace(",", "").replace("\xa0", "")

            try:
                population = int(pop_text)
            except ValueError:
                continue

            if country.lower() == "world":
                continue

            results.append({
                "country": country,
                "region": region,
                "population": population
            })

        return results


class StatsTimesParser(BaseParser):
    def __init__(self):
        super().__init__("https://statisticstimes.com/demographics/countries-by-population.php")

    async def parse(self) -> list[dict]:
        html = await self.fetch_html()
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", {"id": "table_id"})

        results = []
        if not table:
            return results

        for row in table.find("tbody").find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            country = cols[1].get_text(strip=True)
            pop_text = cols[2].get_text(strip=True).replace(",", "")
            region = cols[4].get_text(strip=True)

            try:
                population = int(pop_text)
            except ValueError:
                continue

            if country.lower() == "world":
                continue

            results.append({
                "country": country,
                "region": region,
                "population": population
            })
        return results


class ParserFactory:
    @staticmethod
    def get_parser(source_name: str) -> BaseParser:
        if source_name == "wikipedia":
            return WikipediaParser()
        elif source_name == "statstimes":
            return StatsTimesParser()
        else:
            raise ValueError(f"Unknown data source: {source_name}")
