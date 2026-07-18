from src.database import DatabaseManager
from src.parsers import ParserFactory
from src.config import settings


class PopulationService:
    def __init__(self):
        self.db = DatabaseManager()
        self.source = settings.DATA_SOURCE

    async def fetch_and_save(self):
        print(f"Initializing database and tables...")
        await self.db.create_tables()

        print(f"Starting parsing from source: {self.source}...")
        parser = ParserFactory.get_parser(self.source)
        data = await parser.parse()

        if not data:
            print("No data parsed! Check source or selectors.")
            return

        print(f"Successfully parsed {len(data)} countries. Saving to DB...")
        conn = await self.db.get_connection()
        try:
            async with conn.transaction():
                await conn.executemany("""
                                       INSERT INTO country_population (country, region, population, source)
                                       VALUES ($1, $2, $3, $4) ON CONFLICT (country, source) 
                                       DO UPDATE SET region = EXCLUDED.region, population = EXCLUDED.population;
                                       """, [(d['country'], d['region'], d['population'], self.source) for d in data])
            print("Data saved successfully.")
        finally:
            await conn.close()

    async def print_aggregated_data(self):
        conn = await self.db.get_connection()

        query = """
                WITH ranked_countries AS (
                    SELECT 
                        region,
                        country,
                        population,
                        ROW_NUMBER() OVER(PARTITION BY region ORDER BY population DESC) as max_rank,
                        ROW_NUMBER() OVER(PARTITION BY region ORDER BY population ASC) as min_rank,
                        SUM(population) OVER(PARTITION BY region) as total_region_pop
                    FROM country_population
                    WHERE source = $1
                )
                SELECT 
                    region,
                    total_region_pop,
                    MAX(CASE WHEN max_rank = 1 THEN country END) as max_country,
                    MAX(CASE WHEN max_rank = 1 THEN population END) as max_pop,
                    MAX(CASE WHEN min_rank = 1 THEN country END) as min_country,
                    MAX(CASE WHEN min_rank = 1 THEN population END) as min_pop
                FROM ranked_countries
                GROUP BY region, total_region_pop
                ORDER BY total_region_pop DESC;
                """

        try:
            rows = await conn.fetch(query, self.source)
            if not rows:
                print(f"No data found in DB for source '{self.source}'. Run get_data first.")
                return

            for row in rows:
                print(row['region'] or "Unknown")
                print(f"{row['total_region_pop']:,}")
                print(row['max_country'])
                print(f"{row['max_pop']:,}")
                print(row['min_country'])
                print(f"{row['min_pop']:,}")
                print("-" * 30)

        finally:
            await conn.close()
