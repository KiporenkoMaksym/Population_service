# Population Aggregator Service

An asynchronous service based on Python and Docker for collecting and analyzing demographic data from various sources.

## Technologies

- Python 3.12+
- PostgreSQL
- Docker
- Docker Compose
- asyncpg
- httpx
- BeautifulSoup4

## Features

- Fetches country population data from Wikipedia or StatisticsTimes
- Stores non-aggregated country data in PostgreSQL
- Aggregates data by region using a single SQL query
- Runs entirely with Docker Compose

## Installation and Usage

```bash
git clone https://github.com/KiporenkoMaksym/Population_service.git
cd Population_service
docker compose up get_data
docker compose up print_data
```

## Data Source

The data source is configured using the `DATA_SOURCE` environment variable.

Available values:

- `wikipedia`
- `statstimes`

## Output example
````
Asia
4,753,082,503
India
1,428,627,663
Brunei
452,524
```