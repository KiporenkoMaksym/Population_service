import sys
import asyncio
from src.app import PopulationService

async def main():
    if len(sys.argv) < 2:
        print("Usage: main.py [get_data|print_data]")
        sys.exit(1)

    command = sys.argv[1]
    service = PopulationService()

    if command == "get_data":
        await service.fetch_and_save()
    elif command == "print_data":
        await service.print_aggregated_data()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
