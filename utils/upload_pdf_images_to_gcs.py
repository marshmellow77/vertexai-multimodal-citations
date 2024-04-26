from pdf2image import convert_from_path
import os
from google.cloud import storage
from PIL import Image
import io


def save_to_gcs(bucket_name, image, file_name):
    """Saves a PIL Image to Google Cloud Storage.

    Args:
        bucket_name (str): Name of the bucket.
        image (PIL.Image.Image): Image to be saved.
        file_name (str): Name of the file in the bucket.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format="PNG")
    image_byte_arr = image_byte_arr.getvalue()

    blob.upload_from_file(io.BytesIO(image_byte_arr))


def pdf_to_pngs(pdf_path, dpi=300):
    """Converts each page of a PDF to a PNG image and uploads them to Google Cloud Storage.

    Args:
        pdf_path (str): Path to the PDF file.
        dpi (int, optional): Resolution for the PNG images. Defaults to 300.
    """

    pages = convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=r"/opt/homebrew/Cellar/poppler/24.04.0/bin",
    )  # Adjust poppler path if needed

    for page_num, page in enumerate(pages):
        filename = f"page_{page_num}.png"
        save_to_gcs(
            "dbg-images-heikohotz", page, filename
        )  # replace 'your-bucket-name' with your actual bucket name

pdf_to_pngs("current-investor-presentation_en.pdf")