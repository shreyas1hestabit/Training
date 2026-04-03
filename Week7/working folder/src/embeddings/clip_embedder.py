from transformers import CLIPProcessor, CLIPModel
import torch
import numpy as np
from PIL import Image

class CLIPEmbedder:
    def __init__(self):
        self.device = "cpu" #this tells model that we would be using cpu and not gpu. agar hmare paas gpu hota toh hm woh use krte.
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device) #clipmodel is the actual brain that knows how to see and read 
        #Working: 1.  from_pretrained: Python goes to the internet (Hugging Face) and downloads the math weights that OpenAI spent millions of dollars to calculate.
                  #2.  CLIPModel: This specific brain is multimodal. It actually contains two encoders inside it: one for images and one for text.
                  #3.  .to(self.device): It physically moves that math data to your CPU so it's ready to calculate.
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32") #clip processor is the pre-processing station which resizes images to the correct sqaure size and turns text into the number format model expects.
        self.model.eval() #this is used to save memory and ensure consistency as it tells model we are just using you for searching and not training you.

    def _normalize(self, x):
        return x / x.norm(p=2, dim=-1, keepdim=True) #we are normalizing with the purpose that the length or brightness of the image does not affect the score and it depends only on the direction of the vector. so we convert vectors to unit vectors.
        #p=2 is the L2 norm also known as euclidean normalization.  
        #dim =-1 tells the python which direction to look when calculating length
        # x/ -> divide the orginal value with length so that every vector has a total length of 1. this is called as unit normaization

    def encode_image(self, image: Image.Image):
        image = image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt") #it resizes the image (usually to 224x224) and turns colours into numbers
        #return_tensors="pt" tells processor to retun pytorch tensors instead of python lists or arrays.
        pixel_values = inputs["pixel_values"].to(self.device)

        with torch.no_grad():
            features = self.model.get_image_features(pixel_values=pixel_values)
            # print(type(features))
            if not isinstance(features,torch.Tensor):
                features=features.pooler_output
        
        features = self._normalize(features)
        return features.cpu().numpy() #again converting pytorch to numpy because faiss and most data-science tools are built on numpy. this makes the data universal.

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