import os
import faiss
import numpy as np
import logging
# from transformers import logging as hf_logging
# from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

from google import genai

KNOWLEDGE_DIR = "app/knowledge"
EMBEDDING_MODEL = "gemini-embedding-001"

# MODEL_NAME = "all-MiniLM-L6-v2"
# hf_logging.set_verbosity_error()
# logging.getLogger("transformers").setLevel(logging.ERROR)
logger = logging.getLogger("StuMedica")

class MiniRAG:
    def __init__(self):
        print("RAG: Ładowanie modelu embeddingów...")
        # self.encoder = SentenceTransformer(MODEL_NAME)

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("RAG: Brak klucza GOOGLE_API_KEY!")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

        self.chunks: List[Dict[str, Any]] = []
        self.index = None
        self._build_index()

    def _get_embedding(self, text: str) -> np.ndarray:
        """Pobiera embedding z API Google."""
        try:
            result = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text
            )
            return np.array(result.embeddings[0].values, dtype='float32')
        except Exception as e:
            logger.error(f"RAG: Błąd generowania embeddingu: {e}")
            return None

    def _get_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """Pobiera embeddingi dla listy tekstów (batch)."""
        try:
            embeddings = []
            for text in texts:
                emb = self._get_embedding(text)
                if emb is not None:
                    embeddings.append(emb)

            if not embeddings:
                return None

            return np.vstack(embeddings)
        except Exception as e:
            logger.error(f"RAG: Błąd batch embedding: {e}")
            return None

    def _build_index(self):
        """Wczytuje pliki i buduje indeks FAISS."""
        if not self.client:
            return

        if not os.path.exists(KNOWLEDGE_DIR):
            os.makedirs(KNOWLEDGE_DIR)
            print(f"RAG: Nie wykryto folderu {KNOWLEDGE_DIR}, utworzono pusty folder.")
            return

        files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(('.txt', '.md'))]
        if not files:
            print("RAG: Folder wiedzy jest pusty.")
            return

        self.chunks = []
        chunk_counter = 0

        print(f"RAG: Indeksowanie plików: {files}")

        for filename in files:
            file_path = os.path.join(KNOWLEDGE_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                raw_chunks = text.split("\n\n")

                for content in raw_chunks:
                    content = content.strip()
                    if len(content) > 10:
                        self.chunks.append({
                            "chunk_id": chunk_counter,
                            "source": filename,
                            "content": content
                        })
                        chunk_counter += 1

            except Exception as e:
                print(f"RAG: Błąd odczytu pliku {filename}: {e}")

        if not self.chunks:
            return

        print(f"RAG: Tworzenie embeddingów dla {len(self.chunks)} fragmentów...")

        contents = [c["content"] for c in self.chunks]
        # embeddings = self.encoder.encode(contents)
        embeddings = self._get_batch_embeddings(contents)

        if embeddings is None:
            print("RAG: Nie udało się pobrać embeddingów.")
            return

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        print(f"RAG: Gotowy. Zaindeksowano {len(self.chunks)} fragmentów.")

    def search(self, query: str, k: int = 3):
        """Wyszukuje k fragmentów."""
        if not self.index or not self.chunks or not self.client:
            return ""

        # query_vector = self.encoder.encode([query])
        query_vector = self._get_embedding(query)
        if query_vector is None:
            return ""

        query_vector = query_vector.reshape(1, -1)
        distances, indices = self.index.search(query_vector, k)
        # distances, indices = self.index.search(query_vector, k)

        results = []
        for idx in indices[0]:
            if idx == -1 or idx >= len(self.chunks): continue

            chunk = self.chunks[idx]
            results.append(
                f"---\n[Źródło: {chunk['source']} | ID: {chunk['chunk_id']}]\n{chunk['content']}"
            )

        final_context = "\n".join(results)

        if len(final_context) > 3000:
            final_context = final_context[:3000] + "... (ucięto)"

        return final_context


rag_system = MiniRAG()