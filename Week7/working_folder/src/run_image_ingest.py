from src.pipelines.image_ingest import ImageIngestPipeline

if __name__ == "__main__":
    pipeline = ImageIngestPipeline()
    pipeline.run()