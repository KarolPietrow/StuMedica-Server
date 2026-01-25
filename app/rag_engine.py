import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

KNOWLEDGE_DIR = "app/knowledge"
MODEL_NAME = "all-MiniLM-L6-v2"

class MiniRAG:
    def __init__(self):
        print("RAG: Ładowanie modelu embeddingów...")
        self.encoder = SentenceTransformer(MODEL_NAME)
        self.chunks: List[Dict[str, Any]] = []
        self.index = None
        self._build_index()

    def _build_index(self):
        """Wczytuje pliki z folderu knowledge."""
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

        print(f"RAG: Znaleziono pliki: {files}")

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
        embeddings = self.encoder.encode(contents)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        print(f"RAG: Gotowy. Zaindeksowano {len(self.chunks)} fragmentów.")

    def search(self, query: str, k: int = 3):
        """Wyszukuje k fragmentów."""
        if not self.index or not self.chunks:
            return ""

        query_vector = self.encoder.encode([query])
        distances, indices = self.index.search(query_vector, k)

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