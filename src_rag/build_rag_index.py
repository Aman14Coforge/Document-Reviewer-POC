import json
import logging
from pathlib import Path

import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_index(json_path: str = "rules.json", collection_name: str = "rules_index"):
    """Embed rule JSON data into ChromaDB using sentence-transformers."""
    base_dir = Path(__file__).resolve().parent
    json_file = Path(json_path)
    if not json_file.exists():
        json_file = base_dir / json_path

    with json_file.open("r", encoding="utf-8") as fh:
        rules = json.load(fh)

    logger.info("Loaded %d rules from %s", len(rules), json_file)

    db_dir = base_dir / "chroma_db"
    db_dir.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_dir))
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(name=collection_name)

    documents = []
    ids = []
    metadatas = []

    for rule in rules:
        embedding_text = f"""
Rule ID: {rule['rule_id']}
Title: {rule['title']}
Category: {rule['category']}
Criteria: {rule['verifiable_criteria']}
""".strip()

        documents.append(embedding_text)
        ids.append(rule['rule_id'])
        metadatas.append({
            "rule_id": rule['rule_id'],
            "title": rule['title'],
            "category": rule['category'],
            "severity": rule.get("severity", ""),
            "recommendation": rule.get("recommendation", ""),
        })

    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(documents, convert_to_numpy=True).tolist()
        logger.info("Used sentence-transformers embeddings for %d rules", len(documents))
    except Exception as exc:
        logger.warning("Falling back to TF-IDF embeddings because sentence-transformers failed: %s", exc)
        vectorizer = TfidfVectorizer(stop_words="english")
        embeddings = vectorizer.fit_transform(documents).toarray().tolist()

    collection.add(documents=documents, embeddings=embeddings, ids=ids, metadatas=metadatas)

    logger.info("Indexed %d rules into ChromaDB collection '%s'", len(rules), collection_name)
    return {"collection": collection_name, "count": len(rules)}


if __name__ == "__main__":
    build_index()
