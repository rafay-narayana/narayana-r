import os
import yaml
import json
import requests
import warnings
warnings.filterwarnings('ignore')

def convert_json_to_yaml_and_store(json_data, target_folder, filename="output.yaml"):
    """
    Converts JSON data to YAML format and stores it in a file within the specified target folder.

    Args:
        json_data (dict or str): The JSON data to convert. Can be a Python dictionary
                                  or a JSON formatted string.
        target_folder (str): The path to the folder where the YAML file will be saved.
        filename (str, optional): The name of the YAML file. Defaults to "output.yaml".
    """
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        elif isinstance(json_data, dict):
            data = json_data
        else:
            raise ValueError("Input json_data must be a dictionary or a JSON formatted string.")

        os.makedirs(target_folder, exist_ok=True)  # Create the target folder if it doesn't exist
        filepath = os.path.join(target_folder, filename)

        with open(filepath, 'w') as yaml_file:
            yaml.dump(data, yaml_file, sort_keys=False)  # Dump to YAML, preserving order

        print(f"JSON data successfully converted to YAML and stored in: {filepath}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except OSError as e:
        print(f"Error creating directory or writing file: {e}")
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def make_v1_api(method, url, params, data):
    headers = {
        "Content-Type": "application/yaml",
        "X-RAFAY-API-KEYID": config["API_KEY"],
        "X-ORGANIZATION-ID": config["ORG_HASH"],
    }
    response = make_rest_api_call(method, url, headers, params, data)
    return response


def load_all_orgs():
    print("Loading all orgs")
    response = make_v1_api("GET", config["urls"]["GET_ORGS_V1"], params=None, data=None)
    org_list = []
    has_default_org = False
    default_org_id = None

    try:
        while True:
            data = yaml.safe_load(response.content)
            for k in data["results"]:
                if k['active'] == True and k['approved'] == True and k['name'] != "RafayOperations" and k['name'] != "RafayCommunity":
                    if k['is_default_org'] == True:
                        has_default_org = True
                        default_org_id = k['id']
                    print(f"checking org: {k['name']} with id {k['id']}")    
                    org_list.append(k['id'])
            if data['next'] == None:
                break
            response = make_v1_api("GET", data['next'], params=None, data=None)                 
        if has_default_org:
            org_list= []
            org_list.append(default_org_id)
        print(f"Total organizations found: {len(org_list)},{org_list}")
        return org_list
    except yaml.YAMLError as e:
        print(f"Error parsing YAML response: {e}")
        return org_list  # Return None on parsing error
    

def read_values(partner_api_key, values_file):
    with open(values_file, "r") as f:
        data = yaml.safe_load(f)
        HOST_ENV = data["hostenv"]
        OPS_ENV = data["opsenv"]

        BASE_URL = f"https://{HOST_ENV}"
        OPS_URL = f"https://{OPS_ENV}"

        global config
        config = {
            "urls": {
                "BASE_URL": BASE_URL,
                "OPS_URL": OPS_URL,
                "URL_ENVIRONMENT": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/$PROJECT_NAME$/environmenttemplates",
                "URL_RESOURCE": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/$PROJECT_NAME$/resourcetemplates",
                "URL_CONFIGCONTEXT": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/$PROJECT_NAME$/configcontexts",
                "URL_DRIVER": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/$PROJECT_NAME$/drivers",
                "URL_WRKFLW": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/$PROJECT_NAME$/workflowhandlers",
                "URL_CPROFILE":f"{BASE_URL}/apis/paas.envmgmt.io/v1/projects/$PROJECT_NAME$/computeprofiles",
                "URL_SPROFILE":f"{BASE_URL}/apis/paas.envmgmt.io/v1/projects/$PROJECT_NAME$/serviceprofiles",
                "GET_ORGS_V1": f"{OPS_URL}/auth/v1/organizations/?limit=200&offset=0",

            },
            "FOLDER": data["folder_to_store"],
            "HOST_ENV": data["hostenv"],
            "API_KEY": data["apikey"],
            "ORG_HASH": data["org_hash"],
            "PROJECT_NAME": data["projectname"],
            "DEBUG": data["debug"],
            "CPROFILES": data["compute-profiles"],
            "SPROFILES": data["service-profiles"],
            "TEMPLATES": data["templates"],
            "RESTEMPLATES": data["res-templates"],
            "WORKFLOW_HANDLERS": data["workflow-handlers"],
            "CONTEXTS": data["context"],
            "DELETEALLORGS": data["delete_from_all_orgs"],
        }
        org_list = []
        if config["DELETEALLORGS"] is True:
            org_list = load_all_orgs()
        else:
            if config["ORG_HASH"] is None:
                print("Nothing to delete from, as org list is empty")
                return
            org_list = config["ORG_HASH"].split(",")
        
        for i1 in org_list:
            config["ORG_HASH"] = i1.split(" ")[0]
            print("Processing Org:", config["ORG_HASH"], "\n")
            print("---------------------------------------------------------------------------\n")  
            if  data["service-profiles"] is not None: 
                for i in data["service-profiles"]:
                    print('\nTrying to delete serviceprofile ',  i)  
                    delete_service_profile(i)
            if  data["compute-profiles"] is not None: 
                for i in data["compute-profiles"]:
                    print('\nTrying to delete computeprofile ',  i)  
                    delete_compute_profile(i)
            if  data["templates"] is not None: 
                for i in data["templates"]:
                    print('\nTrying to delete environmenttemplate ',  i)  
                    delete_environment_templates(i)
            if  data["res-templates"] is not None: 
                for i in data["res-templates"]:
                    print('\nTrying to delete resourcetemplate ',  i)  
                    delete_resource_templates(i)
            if  data["workflow-handlers"] is not None: 
                for i in data["workflow-handlers"]:
                    print('\nTrying to delete workflowhandlers ',  i)  
                    delete_workflow_handlers(i)
            if  data["context"] is not None: 
                for i in data["context"]:
                    print('\nTrying to delete config-context ',  i)  
                    delete_config_context(i)

def make_rest_api_call(method, url, headers, params, data):
    try:
        response = requests.request(
            method, url, headers=headers, params=params, data=data, verify=False
        )
    except requests.exceptions.RequestException as e:
        if response is not None and response.content:
            print(f"{e}\n\033[31m{response.content.decode()}\033[0m")
        raise
    return response
        
def make_v3_api(method, url, params, data):
    headers = {
        "Content-Type": "application/yaml",
        "X-API-KEY": config["API_KEY"],
        "X-ORGANIZATION-ID": config["ORG_HASH"],
    }
    try:
        response = make_rest_api_call(method, url, headers, params, data)
        return response
    except:
        return print("could not delete ", url, " ", response)

def delete_environment_templates(templatefile,project_name=None):
    env_url = config["urls"]["URL_ENVIRONMENT"].replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    name = templatefile.split('/')[-1].split('.')[0]
    ver = templatefile.split('/')[-2]
    deleteurl = f"{env_url}/{name}/versions/{ver}"
    print("Delete env template url ", deleteurl)
    response = make_v3_api("GET", deleteurl, None, None)
    if not response.status_code == 200:
        print("Nothing to do for ", templatefile, response.status_code)
    else:
        try:
            data = yaml.safe_load(response.content)
        except yaml.YAMLError as e:
            print(f"Error parsing get environment template response: {e}")
            return None  # Return None on parsing error
        #save the file 
        tmp_path = config["FOLDER"] + "/" + config["ORG_HASH"]+"/" + config["PROJECT_NAME"] + "/" + "env-templates" + "/" + name + "/" + ver
        tmp_filename = name +  ".yaml" 
        convert_json_to_yaml_and_store(data, tmp_path, tmp_filename)
        response = make_v3_api("DELETE", deleteurl, None, None)
        if not response.status_code == 200:
            print("Cannot delete environment template ", name, " version:",ver , " response code: ", response.status_code )
            return
        else:
            print(f"Deleted environment template {name}", " version:",ver," response code: ", response.status_code )
    # now check if the env template is empty if yes try to delete it as well
    deleteurl = env_url + '/' + name
    deleteurl = deleteurl.replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    posturl = config["urls"]["URL_RESOURCE"].replace("$PROJECT_NAME$", config["PROJECT_NAME"]) 
    print("Delete env template url ", deleteurl)
    response = make_v3_api("GET", deleteurl, None, None)
    if response.status_code == 200:
        try:
            data = yaml.safe_load(response.content)
        except yaml.YAMLError as e:
            print(f"Error parsing get environment template response: {e}")
            return None  # Return None on parsing error
        if "items" in data: 
            print("Other version still in environment template ", name, " will delete later")
        else:
            if (data.get("spec", {}).get("sharing", {}).get("enabled", {})):
                data['spec']['sharing'] = {}
                data['spec']['sharing']['enabled'] = False
                yaml_string = yaml.dump(data)
                response = make_v3_api("POST", posturl, None, yaml_string)
                if not response.status_code == 200:
                    print("Cannot unshare for ", name, response)
                    
            response = make_v3_api("DELETE", deleteurl, None, None)
            if response.status_code == 200:
                print(f"Deleted em template {name} , response code {response.status_code}")
            else:
                print(f"Not able to delete em template {name} , response code {response.status_code}")

def delete_resource_templates(templatefile,project_name=None):
    env_url = config["urls"]["URL_RESOURCE"].replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    print(env_url)
    name = templatefile.split('/')[-1].split('.')[0]
    ver = templatefile.split('/')[-2]
    deleteurl = f"{env_url}/{name}/versions/{ver}"
    response = make_v3_api("GET", deleteurl, None, None)
    if not response.status_code == 200:
        print("Nothing to do for ", templatefile, response)
    else:
        try:
            data = yaml.safe_load(response.content)
        except yaml.YAMLError as e:
            print(f"Error parsing get resource template response: {e}")
            return None  # Return None on parsing error
        tmp_path = config["FOLDER"] + "/" + config["ORG_HASH"]+"/" + config["PROJECT_NAME"] + "/" + "res-templates" + "/" + name + "/" + ver
        tmp_filename = name +  ".yaml" 
        convert_json_to_yaml_and_store(data, tmp_path, tmp_filename)
        response = make_v3_api("DELETE", deleteurl, None, None)
        if not response.status_code == 200:
            print("Cannot delete resourcetemplate ", name, " version:",ver , " response code: ", response.status_code )
            return
        else:
            print(f"Deleted resource template {name}", " version:",ver," response code: ", response.status_code )
    deleteurl = config["urls"]["URL_RESOURCE"] + '/' + name
    deleteurl = deleteurl.replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    posturl = config["urls"]["URL_RESOURCE"].replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    print(deleteurl)
    response = make_v3_api("GET", deleteurl, None, None)
    if response.status_code == 200:
        try:
            data = yaml.safe_load(response.content)
        except yaml.YAMLError as e:
            print(f"Error parsing get resource template response: {e}")
            return None  # Return None on parsing error
        if "items" in data: 
            print("Other version still in resource template ", name, " will delete later")
        else:
            #print(data)
            if (data.get("spec", {}).get("sharing", {}).get("enabled", {})):
                data['spec']['sharing'] = {}
                data['spec']['sharing']['enabled'] = False
                # del data['spec']['sharing']
                # update the sharing in the controller
                yaml_string = yaml.dump(data)
                response = make_v3_api("POST", posturl, None, yaml_string)
                if not response.status_code == 200:
                    print("Cannot unshare for ", name, response)
                    
            response = make_v3_api("DELETE", deleteurl, None, None)
            if response.status_code == 200:
                print(f"Deleted resource template {name} , response code {response.status_code}")
            else:
                print(f"Not able to delete resource template {name}  response code {response.status_code}")
    else:
        print("Nothing to do for ", templatefile, response)

def delete_workflow_handlers(templatefile):
    print("into delete workflowhandlers.. ")
    env_url = config["urls"]["URL_WRKFLW"].replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    name = templatefile.split('/')[-1].split('.')[0]
    deleteurl = f"{env_url}/{name}"
    response = make_v3_api("GET", deleteurl, None, None)
    if not response.status_code == 200:
        print("Nothing to do for ", name, response)
    else:
        try:
            data = yaml.safe_load(response.content)
            #print(data)
        except yaml.YAMLError as e:
            print(f"Error parsing get workflow handler response: {e}")
            return None  # Return None on parsing error
        tmp_path = config["FOLDER"] + "/" + config["ORG_HASH"]+"/" + config["PROJECT_NAME"] + "/" + "workflow-handlers" 
        tmp_filename = name +  ".yaml" 
        convert_json_to_yaml_and_store(data, tmp_path, tmp_filename)
        
        # disable sharing before delete
        if (data.get("spec", {}).get("sharing", {}).get("enabled", {})):
            data['spec']['sharing']['enabled'] = False
            del data['spec']['sharing']['projects']
            # update the sharing in the controller
            yaml_string = yaml.dump(data)
            response = make_v3_api("POST", env_url, None, yaml_string)
            if not response.status_code == 200:
                print("Cannot unshare for ", name, "\n")

        # delete the resource
        response = make_v3_api("DELETE", deleteurl, None, None)
        if not response.status_code == 200:
            print("Cannot delete workflowhandler ", name, " response code: ", response.status_code )
        else:
            print(f"Deleted workflowhandler {name}"," response code: ", response.status_code )

def delete_service_profile(templatefile):
    env_url = config["urls"]["URL_SPROFILE"].replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    name = templatefile.split('/')[-1].split('.')[0]
    deleteurl = f"{env_url}/{name}"
    print(deleteurl)
    response = make_v3_api("GET", deleteurl, None, None)
    if not response.status_code == 200:
        print("Nothing to do for ", templatefile, response)
    else:
        try:
            data = yaml.safe_load(response.content)
        except yaml.YAMLError as e:
            print(f"Error parsing get service profile response: {e}")
            return None  # Return None on parsing error
        tmp_path = config["FOLDER"] + "/" + config["ORG_HASH"]+"/" + config["PROJECT_NAME"] + "/" + "service-profiles" 
        tmp_filename = name +  ".yaml" 
        convert_json_to_yaml_and_store(data, tmp_path, tmp_filename)

        response = make_v3_api("DELETE", deleteurl, None, None)
        if not response.status_code == 200:
            print("Cannot delete service profile ", name, " response code: ", response.status_code )           
        else:
            print(f"Deleted service profile  {name}", " response code: ", response.status_code )

def delete_compute_profile(templatefile):
    env_url = config["urls"]["URL_CPROFILE"].replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    name = templatefile.split('/')[-1].split('.')[0]
    deleteurl = f"{env_url}/{name}"
    response = make_v3_api("GET", deleteurl, None, None)
    if not response.status_code == 200:
        print("Nothing to do for ", templatefile, response)
    else:
        try:
            data = yaml.safe_load(response.content)
        except yaml.YAMLError as e:
            print(f"Error parsing get compute profile response: {e}")
            return None  # Return None on parsing error
        tmp_path = config["FOLDER"] + "/" + config["ORG_HASH"]+"/" + config["PROJECT_NAME"] + "/" + "compute-profiles" 
        tmp_filename = name +  ".yaml" 
        convert_json_to_yaml_and_store(data, tmp_path, tmp_filename)

        response = make_v3_api("DELETE", deleteurl, None, None)
        if not response.status_code == 200:
            print("Cannot delete compute profile ", name,  " response code: ", response.status_code )
            
        else:
            print(f"Deleted compute profile  {name}", " response code: ", response.status_code )

def delete_config_context(templatefile):
    print("into delete config-context.. ")
    env_url = config["urls"]["URL_CONTEXT"].replace("$PROJECT_NAME$", config["PROJECT_NAME"])
    name = templatefile.split('/')[-1].split('.')[0]
    deleteurl = f"{env_url}/{name}"
    response = make_v3_api("GET", deleteurl, None, None)
    if not response.status_code == 200:
        print("Nothing to do for ", name, response)
    else:
        try:
            data = yaml.safe_load(response.content)
            #print(data)
        except yaml.YAMLError as e:
            print(f"Error parsing get workflow handler response: {e}")
            return None  # Return None on parsing error
        tmp_path = config["FOLDER"] + "/" + config["ORG_HASH"]+"/" + config["PROJECT_NAME"] + "/" + "config-context" 
        tmp_filename = name +  ".yaml" 
        convert_json_to_yaml_and_store(data, tmp_path, tmp_filename)
        
        # disable sharing before delete
        if (data.get("spec", {}).get("sharing", {}).get("enabled", {})):
            data['spec']['sharing']['enabled'] = False
            del data['spec']['sharing']['projects']
            # update the sharing in the controller
            yaml_string = yaml.dump(data)
            response = make_v3_api("POST", env_url, None, yaml_string)
            if not response.status_code == 200:
                print("Cannot unshare for ", name, "\n")

        # delete the resource
        response = make_v3_api("DELETE", deleteurl, None, None)
        if not response.status_code == 200:
            print("Cannot delete config context ", name, " response code: ", response.status_code )
        else:
            print(f"Deleted config-context {name}"," response code: ", response.status_code )


if __name__ == "__main__":
    read_values(partner_api_key=None, values_file="values-del.yaml")


     