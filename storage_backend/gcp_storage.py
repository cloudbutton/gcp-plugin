#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import google.auth
import google.oauth2.service_account
import re
import io
import time
from requests.exceptions import SSLError as TooManyConnectionsError
from io import BytesIO
from urllib.parse import urlparse
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.api_core.exceptions import GoogleAPICallError, AlreadyExists, RetryError
from ...utils import StorageNoSuchKeyError

class StorageBackend():
    def __init__(self, gcp_storage_config):
        self.credentials_path = gcp_storage_config['credentials_path']
        try:
            self.client = storage.Client.from_service_account_json(self.credentials_path)
        except FileNotFoundError:
            self.client = storage.Client()

    def get_client(self):
        """
        Get ibm_boto3 client.
        :return: ibm_boto3 client
        """
        return self.client

    def put_object(self, bucket_name, key, data):
        """
        Put an object in COS. Override the object if the key already exists.
        :param key: key of the object.
        :param data: data of the object
        :type data: str/bytes
        :return: None
        """
        done = False
        while not done:
            try:
                bucket = self.client.get_bucket(bucket_name)
                blob = bucket.blob(blob_name=key)
                blob.upload_from_string(data=data)
                done = True
            except TooManyConnectionsError:
                time.sleep(0.25)

    def get_object(self, bucket_name, key, stream=False, extra_get_args={}):
        """
        Get object from COS with a key. Throws StorageNoSuchKeyError if the given key does not exist.
        :param key: key of the object
        :return: Data of the object
        :rtype: str/bytes
        """

        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name=key)
        
        if not blob.exists():
            raise StorageNoSuchKeyError(key)
        
        if extra_get_args and 'range' in extra_get_args:
            start, end = re.findall(r'\d+', extra_get_args['range'])
            start = int(start)
            end = int(end)
        else:
            start, end = None, None
        
        if stream:
            stream = BytesIO()
            # Download object to bytes buffer
            blob.download_to_file(stream, start=start, end=end)
            stream.seek(0) # Retrun to the initial buffer position
            return stream
        else:
            return blob.download_as_string(start=start, end=end)
        
    def head_object(self, bucket_name, key):
        """
        Head object from COS with a key. Throws StorageNoSuchKeyError if the given key does not exist.
        :param key: key of the object
        :return: Data of the object
        :rtype: str/bytes
        """
        try:
            client = self.client
            bucket = client.get_bucket(bucket_name)
            blob = bucket.get_blob(blob_name=key)
            response = {
                'LastModified' : blob.updated,
                'ETag' : blob.etag, 
                'content-type' : blob.content_type,
                'content-length' : blob.size  
            }
            return response
        except google.api_core.exceptions.ClientError as e:
            if NotFound:
                raise StorageNoSuchKeyError(key)
            else:
                raise e

    def delete_object(self, bucket_name, key):
        """
        Delete an object from storage.
        :param bucket: bucket name
        :param key: data key
        """
        
        try:
            client = self.client
            bucket = client.get_bucket(bucket_name)
            bucket.delete_blob(key)
        except google.api_core.exceptions.ClientError as e:
            if NotFound:
                raise StorageNoSuchKeyError(key)
            else:
                raise e

    def delete_objects(self, bucket_name, key_list):
        """
        Delete a list of objects from storage.
        :param bucket: bucket name
        :param key_list: list of keys
        """
        #TODO: exceptions
        result = []
        for key in key_list:
            self.delete_object(bucket_name, key)
        return result
        #! result.append(self.delete...)

    def bucket_exists(self, bucket_name):
        try:
            client = self.client
            client.get_bucket(bucket_name)
        except google.api_core.exceptions.ClientError as e:
            if NotFound:
                raise StorageNoSuchKeyError(bucket_name)
            else:
                raise e

    def list_objects(self, bucket_name, prefix=None):
        
        try:
            page_iterator = self.client.get_bucket(bucket_name).list_blobs(prefix=prefix)
            object_list = []
            for page in page_iterator:
                object_list.append({
                    'Key' : page.name, 
                    'LastModified' : page.updated,
                    'ETag' : page.etag,
                    'Size' : page.size, 
                    'StorageClass' : page.storage_class})
            return object_list
        except google.api_core.exceptions.ClientError as e:
            if NotFound:
                raise StorageNoSuchKeyError(bucket_name)
            else:
                raise e
    
    def list_keys_with_prefix(self, bucket_name, prefix):
        """
        Return a list of keys for the given prefix.
        :param prefix: Prefix to filter object names.
        :return: List of keys in bucket that match the given prefix.
        :rtype: list of str
        """

        try:
            page_iterator = self.client.get_bucket(bucket_name).list_blobs(prefix=prefix)
            key_list = []
            for page in page_iterator:
                key_list.append(page.name)
            return key_list
        except google.api_core.exceptions.ClientError as e:
            if NotFound:
                raise StorageNoSuchKeyError(bucket_name)
            else:
                raise e