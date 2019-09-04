import sys
from os.path import exists, isfile
from pywren_ibm_cloud.utils import version_str
from pywren_ibm_cloud import config

RUNTIME_TIMEOUT_DEFAULT = 540 # 540 s == 9 min
RUNTIME_MEMORY_DEFAULT = 2048 # 2048 MB

def load_config(config_data=None):
    if 'runtime_memory' not in config_data['pywren']:
        config_data['pywren']['runtime_memory'] = RUNTIME_MEMORY_DEFAULT
    if 'runtime_timeout' not in config_data['pywren']:
        config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_DEFAULT
    if 'runtime' not in config_data['pywren']:
        config_data['pywren']['runtime'] = 'python'+version_str(sys.version_info)

    if 'gcp' not in config_data:
        raise Exception("'gcp' section is mandatory in the configuration")
    
    config_data['gcp']['retries'] = config_data['pywren']['retries']
    config_data['gcp']['retry_sleeps'] = config_data['pywren']['retry_sleeps']

    # Put storage data into compute backend config dict entry
    storage_config = dict()
    storage_config['pywren'] = config_data['pywren'].copy()
    storage_config['gcp_storage'] = config_data['gcp'].copy()
    config_data['gcp']['storage'] = config.extract_storage_config(storage_config)
        
    required_parameters_0 = (
        'project_name', 
        'service_account',
        'credentials_path',
        'region')
    if not set(required_parameters_0) <= set(config_data['gcp']):
        raise Exception("'project_name', 'service_account', 'credentials_path' and 'region' \
        are mandatory under 'gcp' section")

    if not exists(config_data['gcp']['credentials_path']) or not isfile(config_data['gcp']['credentials_path']):
        raise Exception("Path {} must be credentials JSON file.".format(config_data['gcp']['credentials_path']))
    
    config_data['gcp_functions'] = config_data['gcp'].copy()