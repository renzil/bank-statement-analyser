import functions_framework
from google.cloud import storage

def process_bank_statement_pdf(event, context):
    """Background Cloud Function to be triggered by Cloud Storage.
       This generic function logs relevant data when a file is changed,
       and works for all Cloud Storage CRUD operations.
    Args:
        event (dict):  The dictionary with data specific to this type of event.
                       The `data` field contains a description of the event in
                       the Cloud Storage `object` format described here:
                       https://cloud.google.com/storage/docs/json_api/v1/objects#resource
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Cloud Logging
    """

    print('Event ID: {}'.format(context.event_id))
    print('Event type: {}'.format(context.event_type))
    print('Bucket: {}'.format(event['bucket']))
    print('File: {}'.format(event['name']))
    print('Metageneration: {}'.format(event['metageneration']))
    print('Created: {}'.format(event['timeCreated']))
    print('Updated: {}'.format(event['updated']))

    bucket_name = event['bucket']
    source_blob_name = event['name']

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    destination_file_name = '/tmp/doc_to_process.pdf'

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    user_data = source_blob_name.split("_")
    user_id = user_data[0]
    timestamp = user_data[1]

    print('User id: {}'.format(user_id))
    print('Timestamp: {}'.format(timestamp))

    from pymongo import MongoClient
    import os
    client = MongoClient(f"mongodb+srv://admin:{os.environ['MONGODB_PWD']}@cluster0.xclm49x.mongodb.net/?retryWrites=true&w=majority")
    db = client.test

    imports_collection = db["imports"]
    imports_collection.insert_one({
        "user_id": user_id,
        "timestamp": timestamp
    })
