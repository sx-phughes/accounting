import asyncio
from pymongo import AsyncMongoClient


async def main():
    cxn_str = "mongodb+srv://phughes_db_user:Ovnj7yHorvUHHUPO@practicecluster.5v52qte.mongodb.net/?retryWrites=true&w=majority&appName=PracticeCluster"
    client = AsyncMongoClient(cxn_str)

    try:
        database = client.get_database("sample_mflix")
        movies = database.get_collection("movies")

        query = {"title": "Back to the Future"}
        movie = await movies.find_one(query)

        print(movie)

        await client.close()
    except Exception as e:
        raise Exception(
            "unable to find the document due to the following error: ", e
        )


if __name__ == "__main__":
    asyncio.run(main())
