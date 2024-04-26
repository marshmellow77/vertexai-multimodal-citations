from vertexai.vision_models import MultiModalEmbeddingModel
from google.cloud import aiplatform_v1
from google.cloud import storage
from vertexai.preview.generative_models import GenerativeModel, Part
from dotenv import load_dotenv
import os

load_dotenv()


def get_query_embedding(query: str):
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
    embeddings = model.get_embeddings(contextual_text=query)
    return embeddings.text_embedding


def get_gcs_location_for_query(query: str):
    # Generate query embedding
    query_embedding = get_query_embedding(query)

    # Configure Vector Search client
    client_options = {"api_endpoint": os.getenv("API_ENDPOINT")}
    vector_search_client = aiplatform_v1.MatchServiceClient(
        client_options=client_options
    )

    # Build FindNeighborsRequest object
    datapoint = aiplatform_v1.IndexDatapoint(feature_vector=query_embedding)
    query = aiplatform_v1.FindNeighborsRequest.Query(
        datapoint=datapoint, neighbor_count=10
    )
    request = aiplatform_v1.FindNeighborsRequest(
        index_endpoint=os.getenv("INDEX_ENDPOINT"),
        deployed_index_id=os.getenv("DEPLOYED_INDEX_ID"),
        queries=[query],
        return_full_datapoint=True,
    )

    # Execute the request
    response = vector_search_client.find_neighbors(request)

    # Extract the filename from the response (only first result is used here)
    filename = response.nearest_neighbors[0].neighbors[0].datapoint.datapoint_id
    filename = filename.split("'")[1]

    gcs_path = f"{os.getenv('GS_PATH')}/{filename}"

    return gcs_path


def download_blob(full_gcs_path):
    """Downloads a blob from the bucket using a full GCS path."""
    if not full_gcs_path.startswith("gs://"):
        raise ValueError("Provided path does not look like a GCS path")

    # Parse the GCS path to extract bucket name and blob name
    parts = full_gcs_path.split("/", 3)
    bucket_name = parts[2]
    blob_name = parts[3]

    # Initialize the Google Cloud Storage client and download the blob
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def image_requested(query):
    prompt = f"""Given the user query below, decide whether the user wants to see an image:

Respond only with `True` or `False`.

<question>
{query}
</question>

Decision:"""

    model = GenerativeModel("gemini-1.0-pro")
    response = model.generate_content(prompt)

    response_text = response.candidates[0].text
    assert response_text == "True" or response_text == "False"

    return bool(response_text)


def image_requested(query):
    prompt = f"""Given the user query below, decide whether the user requested to see a chart:

Respond only with `True` or `False`.

<question>
{query}
</question>

Decision:"""

    model = GenerativeModel("gemini-1.0-pro")

    try:
        response = model.generate_content(prompt)
        response_text = response.candidates[0].text.strip()

        if response_text.lower() == "true":
            return True
        elif response_text.lower() == "false":
            return False
        else:
            raise ValueError("Model response was not 'True' or 'False'")
    except Exception as e:
        print(f"Error with model: {e}")
        return False  # Default to not showing an image if the model fails
