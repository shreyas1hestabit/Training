import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image


class BLIPCaptioner:
    def __init__(self):
        self.device = "cpu"
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        ).to(self.device)

    def generate_caption(self, image: Image.Image):
        image = image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            out = self.model.generate(**inputs)

        return self.processor.decode(out[0], skip_special_tokens=True)