const BUCKET_NAME = 'bank-statement-parser-dev-user-data';

async function generateV4ReadSignedUrl(fileName) {
  // Imports the Google Cloud client library
  const { Storage } = require('@google-cloud/storage');

  // Creates a client
  const storage = new Storage({
    // projectId: 'bankstatementparser-dev',
    keyFilename: './bankstatementparser-dev-06dfb339fb0e.credentials.json'
  });

  // These options will allow temporary write access to the file
  const options = {
      version: 'v4',
      action: 'write',
      expires: Date.now() + 15 * 60 * 1000, // 15 minutes
      contentType: 'application/pdf',
  };

  // Get a v4 signed URL for writing the file
  const [url] = await storage
      .bucket(BUCKET_NAME)
      .file(fileName)
      .getSignedUrl(options);

  console.log('Generated PUT signed URL:');
  console.log(url);

  return {
    url,
  };
}

/**
 * Create a signed url to upload a file
 * @param {Object} uploadBody
 * @returns {Promise<User>}
 */
const uploadRequest = async (uploadBody) => {
  const destFileName = 'test';
  return await generateV4ReadSignedUrl(destFileName)
};

module.exports = {
  uploadRequest,
};
