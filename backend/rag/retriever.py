import chromadb

client = chromadb.PersistentClient(
    path="./storage"
)

COLLECTION="documents"


def get_collection():

    try:
        client.delete_collection(
            COLLECTION
        )

    except:
        pass

    return client.get_or_create_collection(
        COLLECTION
    )


collection=get_collection()


def save(
chunks,
emb
):

    collection.add(

        ids=[
            str(i)

            for i in range(
                len(chunks)
            )
        ],

        documents=chunks,

        embeddings=[
            e.tolist()

            for e in emb
        ]

    )


def retrieve(
query_emb,
n=5
):

    return collection.query(

        query_embeddings=[
            query_emb.tolist()
        ],

        n_results=n

    )