from h2ogpte import H2OGPTE
import os


# Set variables
connect = {
    "address": os.getenv("H2OGPTE_ADDRESS"),
    "api_key": os.getenv("H2OGPTE_API_KEY"),
}
name = "Safety Events"
document_pdf = "Classification_of_patient_safety_incidents.pdf"
collection_id = None


# Instantiate h2ogpte client
h2ogpte = H2OGPTE(address=connect["address"], api_key=connect["api_key"])


# Check for existing collection
recent_collections = client.list_recent_collections(0, 1000)
for c in recent_collections:
    if c.name == name and c.document_count:
        collection_id = c.id
        break
# Create Collection if not found
if collection_id is None:
    collection_id = client.create_collection(
        name=name,
        description="Healthcare Safety Events Classification",
    )


# Upload file into collection
with open(document_pdf, "rb") as f:
    upload_id = client.upload(document_pdf, f)
client.ingest_uploads(collection_id, [upload_id])


for c in h2ogpte.list_recent_collections(0, 1000):
    print(c.id, c.name, c.document_count)
