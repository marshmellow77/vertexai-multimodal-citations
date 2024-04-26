# Instructions to set up multimodal (i.e. image) references
## Split PDF, create images, and uplaod to GCS
The script `upload_pdf_images_to_gcs.py` will
- Split a PDF into single pages
- Upload each page as a separate .png file to GCS
## Create image embeddings
The script `image_embeddings.py` will
- create a multimodal embedding for each image
- save all embeddings in `indexData.json`, together with the corresponding filenames
## Create Vector Search Index
- First, create the configuration for the index as in `index_metadata.json` (see also https://cloud.google.com/vertex-ai/docs/vector-search/configuring-indexes)
- Then create the index via CLI
```
gcloud ai indexes create \
  --metadata-file=index_metadata.json \
  --display-name=MultiModal-Embeddings \
  --project=<PROJECT_ID> \
  --region=<REGION>
  ```
## Create Index Endpoint
This can be done in the console via the `Deploy` button
## Image search
Once the index endpoint is deployed the application will be able to pull the most relevant image from GCS. To do it will
- Identify if the user wants to see an image (slide, chart, etc)
- If yes, create an embedding for the query
- Finds the image that matches the query the best
- Downloads the corresponding image from GCS
- Displays it in the UI
