import asyncio

async def main():
    await asyncio.sleep(1)
    print("Hello")

with asyncio.Runner() as runner:
    runner.run(main())