from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
import os

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/mydatabase")

vectorstore = PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
    collection_name="items",
    use_jsonb=True
)

def index_item(item):
    text = f"{item.name}: {item.description}"
    vectorstore.add_texts(
        texts=[text],
        metadatas=[{"user_id": item.user_id}],
        ids=[str(item.id)]
    )

if __name__ == "__main__":
    vector = embeddings.embed_query("wool sweater")
    print(len(vector), vector[:5])