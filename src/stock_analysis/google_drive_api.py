# import the required libraries
import os
import io
import shutil
from mimetypes import MimeTypes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
  
class GoogleDriveAPI:
    def __init__(self):
        
        # Determine credentials
        info = {
            "type": os.environ["GOOGLECREDENTIALS_TYPE"],
            "project_id": os.environ["GOOGLECREDENTIALS_PROJECT_ID"],
            "private_key_id": os.environ["GOOGLECREDENTIALS_PRIVATE_KEY_ID"],
            "private_key": os.environ["GOOGLECREDENTIALS_PRIVATE_KEY"],
            "client_email": os.environ["GOOGLECREDENTIALS_CLIENT_EMAIL"],
            "client_id": os.environ["GOOGLECREDENTIALS_CLIENT_ID"],
            "auth_uri": os.environ["GOOGLECREDENTIALS_AUTH_URI"],
            "token_uri": os.environ["GOOGLECREDENTIALS_TOKEN_URI"],
            "auth_provider_x509_cert_url": os.environ["GOOGLECREDENTIALS_AUTH_PROVIDER_X509_CERT_URL"],
            "client_x509_cert_url": os.environ["GOOGLECREDENTIALS_CLIENT_X509_CERT_URL"],
            }
        self.creds = service_account.Credentials.from_service_account_info(info)
        self.creds = self.creds.with_scopes(['https://www.googleapis.com/auth/drive'])

        # Connect to the API service
        self.service = build('drive', 'v3', credentials=self.creds)
  
    def file_list(self):
        page_token = None
        files = []
        while True:
            response = self.service.files().list(spaces='drive', fields='nextPageToken, files(id, name)', pageToken=page_token).execute()
            for file in response.get('files', []):
                files.append(file)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return files
    
    def file_download(self, file_id, file_name):
        """Download a file.

        Args:
            file_id: id of the file to download
            file_name: name of the file to download.
        """
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
          
        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False
  
        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()
  
            fh.seek(0)
              
            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)
  
            print("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except:
            
            # Return False if something went wrong
            print("Something went wrong.")
            return False
  
    def file_upload(self, filepath, folder_id):
        """Upload a file.

        Args:
            filepath: path of the file to upload
            folder_id: id of the folder to upload the file(s).
        """
        # Extract the file name out of the file path
        name = filepath.split('/')[-1]
          
        # Find the MimeType of the file
        mimetype = MimeTypes().guess_type(name)[0]
          
        # create file metadata
        file_metadata = {'name': name, 'parents': [folder_id]}

        try:
            media = MediaFileUpload(filepath, mimetype=mimetype)
              
            # Create a new file in the Drive storage
            self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
          
        except:
            # Raise UploadError if file is not uploaded.
            print(f"Can't upload file: {name}")

    def file_delete(self, file_id):
        """Permanently delete a file, skipping the trash.

        Args:
            file_id: ID of the file to delete.
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
        except:
            print(f'An error occurred in deleting file id: {file_id}')