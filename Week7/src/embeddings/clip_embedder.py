from transformers import CLIPProcessor, CLIPModel
import torch
import numpy as np
from PIL import Image

class CLIPEmbedder:
    def __init__(self):
        self.device = "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model.eval()

    def _normalize(self, x):
        return x / x.norm(p=2, dim=-1, keepdim=True)

    def encode_image(self, image: Image.Image):
        image = image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        pixel_values = inputs["pixel_values"].to(self.device)

        with torch.no_grad():
            features = self.model.get_image_features(pixel_values=pixel_values)
            # print(type(features))
            if not isinstance(features,torch.Tensor):
                features=features.pooler_output
        
        features = self._normalize(features)
        return features.cpu().numpy()

    def encode_text(self, text: str):
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)

        with torch.no_grad():
            features = self.model.get_text_features(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

        features = self._normalize(features)
        return features.cpu().numpy()