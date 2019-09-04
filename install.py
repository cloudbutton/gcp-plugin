import pywren_ibm_cloud
import os
import shutil

base_path = os.path.dirname(pywren_ibm_cloud.__file__)
source_path = os.path.dirname(__file__)

gcp_functions_backend_path = os.path.join(os.path.join(base_path, 'compute', 'backends'), 'gcp_functions')
gcp_storage_backend_path = os.path.join(os.path.join(base_path, 'storage', 'backends'), 'gcp_storage')

try:
    if os.path.exists(gcp_functions_backend_path) and os.path.isfile(gcp_functions_backend_path):
        os.remove(gcp_functions_backend_path)
    if os.path.exists(gcp_storage_backend_path) and os.path.isfile(gcp_storage_backend_path):
        os.remove(gcp_storage_backend_path)

    if os.path.exists(gcp_functions_backend_path) and os.path.isdir(gcp_functions_backend_path):
        shutil.rmtree(gcp_functions_backend_path)
    if os.path.exists(gcp_storage_backend_path) and os.path.isdir(gcp_storage_backend_path):
        shutil.rmtree(gcp_storage_backend_path)

    if not os.path.exists(gcp_functions_backend_path):
        shutil.copytree(os.path.join(source_path, 'compute_backend'), gcp_functions_backend_path)
    if not os.path.exists(gcp_storage_backend_path):
        shutil.copytree(os.path.join(source_path, 'storage_backend'), gcp_storage_backend_path)

    print('Done')
except Exception as e:
    print('Installation failed: {}'.format(e))
