import trades

async def main():
    await trades.fetch_data_periodically()

if __name__ == "__main__":
    asyncio.run(main())
