import numpy as np
from PIL import Image
import os

from src.vectorstore.multimodel_index import MultiModalIndex
from src.embeddings.clip_embedder import CLIPEmbedder
from src.embeddings.text_embedder import TextEmbedder
from src.utils.pdf_utils import pdf_to_images


class ImageSearch:
    def __init__(self):
        print("Loading index...")
        self.index = MultiModalIndex()
        self.index.load()

        self.clip = CLIPEmbedder()
        self.text_embedder = TextEmbedder()
        print("System ready.\n")

    # -----------------------------
    # TEXT → IMAGE
    # -----------------------------
    def text_query(self, query, k=3):
        vector = self.text_embedder.encode(query)
        scores, indices = self.index.text_index.search(
            vector.astype(np.float32), k
        )

        results = []
        for score, idx in zip(scores[0], indices[0]):
            item = self.index.metadata[idx]
            results.append({
                "score": float(score),
                "image_path": item["image_path"],
                "caption": item.get("caption", ""),
                "ocr_text": item.get("ocr_text", "")
            })
        return results

    # -----------------------------
    # IMAGE → IMAGE
    # -----------------------------
    # def image_query(self, image_path, k=3):
    #     image = Image.open(image_path).convert("RGB")
    #     vector = self.clip.encode_image(image)

    #     scores, indices = self.index.image_index.search(
    #         vector.astype(np.float32), k
    #     )

    #     results = []
    #     for score, idx in zip(scores[0], indices[0]):
    #         item = self.index.metadata[idx]
    #         results.append({
    #             "score": float(score),
    #             "image_path": item["image_path"],
    #             "caption": item.get("caption", ""),
    #             "ocr_text": item.get("ocr_text", "")
    #         })
    #     return results

    def image_query(self, image_path, k=3):
        results = []

        # If PDF → convert to images
        if image_path.lower().endswith(".pdf"):
            pages = pdf_to_images(image_path)

            for page_num, page in enumerate(pages):
                vector = self.clip.encode_image(page)

                scores, indices = self.index.image_index.search(
                    vector.astype(np.float32), k
                )

                for score, idx in zip(scores[0], indices[0]):
                    item = self.index.metadata[idx]
                    results.append({
                        "score": float(score),
                        "image_path": item.get("image_path"),
                        "caption": item.get("caption", ""),
                        "ocr_text": item.get("ocr_text", ""),
                        "source_page": page_num
                    })

        else:
            # Normal image file
            image = Image.open(image_path).convert("RGB")
            vector = self.clip.encode_image(image)

            scores, indices = self.index.image_index.search(
                vector.astype(np.float32), k
            )

            for score, idx in zip(scores[0], indices[0]):
                item = self.index.metadata[idx]
                results.append({
                    "score": float(score),
                    "image_path": item.get("image_path"),
                    "caption": item.get("caption", ""),
                    "ocr_text": item.get("ocr_text", "")
                })

        return results

    # -----------------------------
    # IMAGE → TEXT ANSWER
    # -----------------------------
    def image_to_text(self, image_path, k=3):
        results = self.image_query(image_path, k)

        combined_text = ""
        for r in results:
            combined_text += f"\nImage: {r['image_path']}\n"
            combined_text += f"Caption: {r['caption']}\n"
            combined_text += f"OCR: {r['ocr_text']}\n"

        return combined_text


# =====================================================
# CLI Interface
# =====================================================

if __name__ == "__main__":
    search_system = ImageSearch()

    while True:
        print("\nSelect Query Mode:")
        print("1. Text -> Image")
        print("2. Image -> Image")
        print("3. Image -> Text Answer")
        print("4. Exit")

        choice = input("Enter choice (1/2/3/4): ").strip()

        if choice == "1":
            query = input("Enter your text query: ")
            results = search_system.text_query(query)

            print("\nTop Results:\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['image_path']}")
                print(f"   Score: {r['score']:.4f}")
                print(f"   Caption: {r['caption']}")
                print(f"   OCR: {r['ocr_text']}")
                print("-" * 50)

        elif choice == "2":
            image_path = input("Enter image path: ")

            if not os.path.exists(image_path):
                print("Invalid image path!")
                continue

            results = search_system.image_query(image_path)

            print("\nTop Similar Images:\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['image_path']}")
                print(f"   Score: {r['score']:.4f}")
                print(f"   Caption: {r['caption']}")
                print(f"   OCR: {r['ocr_text']}")
                print("-" * 50)

        elif choice == "3":
            image_path = input("Enter image path: ")

            if not os.path.exists(image_path):
                print("Invalid image path!")
                continue

            answer = search_system.image_to_text(image_path)

            print("\nGenerated Contextual Answer:")
            print(answer)

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")