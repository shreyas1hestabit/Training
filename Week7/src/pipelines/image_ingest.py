import os
from PIL import Image

from src.embeddings.clip_embedder import CLIPEmbedder
from src.embeddings.text_embedder import TextEmbedder
from src.utils.ocr_engine import extract_text
from src.utils.blip_captioner import BLIPCaptioner
from src.vectorstore.multimodel_index import MultiModalIndex
from src.utils.pdf_utils import pdf_to_images


class ImageIngestPipeline:
    def __init__(self, data_path="src/data/raw/images"):
        self.data_path = data_path
        self.clip = CLIPEmbedder()
        self.text_embedder = TextEmbedder()
        self.captioner = BLIPCaptioner()
        self.index = MultiModalIndex()

    def process_image(self, image, image_path, page=None):
        print(f"Processing: {image_path} Page: {page}")

        # Image embedding (CLIP)
        image_vector = self.clip.encode_image(image)

        # OCR
        ocr_text = extract_text(image)

        #  Caption
        caption = self.captioner.generate_caption(image)

        # Combine text for text embedding
        combined_text = (caption or "") + " " + (ocr_text or "")
        text_vector = self.text_embedder.encode(combined_text)

        # Standardized metadata schema
        meta = {
            "image_path": image_path,   # full path for retrieval
            "page": page,               # None for images, page number for PDFs
            "caption": caption,
            "ocr_text": ocr_text
        }

        self.index.add(image_vector, text_vector, meta)

    def run(self):
        print("Starting ingestion...")

        for file in os.listdir(self.data_path):
            path = os.path.join(self.data_path, file)

            # ----------------------
            # IMAGE FILES
            # ----------------------
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                try:
                    image = Image.open(path).convert("RGB")
                    self.process_image(image, path)
                except Exception as e:
                    print(f"Error processing {file}: {e}")

            # ----------------------
            # PDF FILES
            # ----------------------
            elif file.lower().endswith(".pdf"):
                try:
                    pages = pdf_to_images(path)
                    for i, page in enumerate(pages):
                        self.process_image(page, path, page=i)
                except Exception as e:
                    print(f"Error processing PDF {file}: {e}")

        self.index.save()
        print("Ingestion complete.")