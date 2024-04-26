import numpy as np
import glob
from typing import List
from typing import Optional

import vertexai
from vertexai.vision_models import (
    Image,
    MultiModalEmbeddingModel,
    MultiModalEmbeddingResponse,
)
from google.cloud import storage


def get_image_embeddings(image_path):
    """Generate embeddings for a given image.

    Args:
        image_path: Path to the image file.

    Returns:
        The image embedding as a numpy array.
    """
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
    # image = Image.load_from_file(image_path)
    embeddings = model.get_embeddings(image=image_path)
    return embeddings
    # Assuming embeddings.image_embedding is a format that can be directly converted to np.ndarray
    # embedding_np = np.array(embeddings.image_embedding)
    # return embedding_np


gcs_image_path = "dbg-images-heikohotz"
storage_client = storage.Client()
bucket = storage_client.get_bucket(gcs_image_path)
files = bucket.list_blobs()

for file in files:
    # print(file.name)
    # Assuming you want to retrieve the embeddings for each image
    # with file.open("rb") as image_file:
    #     image_file_contents = image_file.read()
    # embeddings = get_image_embeddings(image_file_contents)
    file_name = file.name.encode(encoding="UTF-8", errors="strict")

    # get GCS URI
    gcs_uri = f"gs://{gcs_image_path}/{file.name}"
    print(gcs_uri)
    img = Image(gcs_uri=gcs_uri)
    embeddings = get_image_embeddings(img)
    # print(f"Image Embedding: {embeddings.image_embedding}")

    with open("indexData.json", "a") as f:
        f.write('{"id":"' + str(file_name) + '",')
        f.write(
            '"embedding":['
            + ",".join(str(x) for x in embeddings.image_embedding)
            + "]}"
        )
        f.write("\n")
