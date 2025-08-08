import os
import yaml
import requests


def make_rest_api_call(method, url, headers, params, data):
    try:
        response = requests.request(
            method, url, headers=headers, params=params, data=data
        )
        response.raise_for_status()  # Raise an exception for error status codes
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
    response = make_rest_api_call(method, url, headers, params, data)
    return response


def read_values():
    print("Reading values")

    with open("values.yaml", "r") as f:
        data = yaml.safe_load(f)
        HOST_ENV = data["hostenv"]
        PROJECT_NAME = data["projectname"]
        BASE_URL = f"https://{HOST_ENV}"

        global config
        config = {
            "urls": {
                "BASE_URL": BASE_URL,
                "GET_PROJECTS": f"{BASE_URL}/v1/auth/projects",
                "CREATE_PROJECT": f"{BASE_URL}/apis/system.k8smgmt.io/v3/projects",
                "GET_USERS": f"{BASE_URL}/auth/v1/users/-/current/",
                "GET_PROJECT_DETAIL": f"{BASE_URL}/apis/system.k8smgmt.io/v3/projects/{PROJECT_NAME}",
                "ADD_SECRETSEALER": f"{BASE_URL}/apis/integrations.k8smgmt.io/v3/projects/{PROJECT_NAME}/secretsealers",
                "ADD_AGENT": f"{BASE_URL}/apis/gitops.k8smgmt.io/v3/projects/{PROJECT_NAME}/agents",
                "ADD_REPO": f"{BASE_URL}/apis/integrations.k8smgmt.io/v3/projects/{PROJECT_NAME}/repositories",
                "ADD_CONFIGCONTEXT": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/{PROJECT_NAME}/configcontexts",
                "ADD_RESOURCE": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/{PROJECT_NAME}/resourcetemplates",
                "ADD_ENVIRONMENT": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/{PROJECT_NAME}/environmenttemplates",
                "ADD_DRIVER": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/{PROJECT_NAME}/drivers",
            },
            "HOST_ENV": data["hostenv"],
            "API_KEY": data["apikey"],
            "ORG_HASH": data["org_hash"],
            "PROJECT_NAME": data["projectname"],
            "DEBUG": data["debug"],
        }


def delete_environment_templates():
    response = make_v3_api("GET", config["urls"]["ADD_ENVIRONMENT"], None, None)
    try:
        data = yaml.safe_load(response.content)
    except yaml.YAMLError as e:
        print(f"Error parsing get environment template response: {e}")
        return None  # Return None on parsing error

    if "items" in data:
        items = data["items"]
        env_url = config["urls"]["ADD_ENVIRONMENT"]
        for item in items:
            name = item['metadata']['name']
            deleteurl = f"{env_url}/{name}"
            print(deleteurl)
            response = make_v3_api("DELETE", deleteurl, None, None)
            status = response.status_code
            print(f"Delete em template {name} , response code {status}")
    else:
        print("no environment templates to delete")

def delete_resource_templates():
    response = make_v3_api("GET", config["urls"]["ADD_RESOURCE"], None, None)
    try:
        data = yaml.safe_load(response.content)
    except yaml.YAMLError as e:
        print(f"Error parsing get resource template response: {e}")
        return None  # Return None on parsing error

    if "items" in data:
        items = data["items"]
        env_url = config["urls"]["ADD_RESOURCE"]
        for item in items:
            name = item['metadata']['name']
            deleteurl = f"{env_url}/{name}"
            print(deleteurl)

            response = make_v3_api("GET", deleteurl, None, None)
            try:
                data = yaml.safe_load(response.content)
            except yaml.YAMLError as e:
                print(f"Error parsing response: {e}")
                return None  # Return None on parsing error

            # disable sharing before delete
            if (data.get("spec", {}).get("sharing", {}).get("enabled", {})):
                data['spec']['sharing']['enabled'] = False
                del data['spec']['sharing']['projects']

            # update the sharing in the controller
            yaml_string = yaml.dump(data)
            response = make_v3_api("POST", env_url, None, yaml_string)

            # delete the resource
            response = make_v3_api("DELETE", deleteurl, None, None)
            status_code = response.status_code
            print(f"Delete resource template {name} , response code {status_code}")
    else:
        print("no resource templates to delete")

def delete_config_contexts():
    response = make_v3_api("GET", config["urls"]["ADD_CONFIGCONTEXT"], None, None)
    try:
        data = yaml.safe_load(response.content)
    except yaml.YAMLError as e:
        print(f"Error parsing get config context response: {e}")
        return None  # Return None on parsing error

    if "items" in data:
        items = data["items"]
        env_url = config["urls"]["ADD_CONFIGCONTEXT"]
        for item in items:
            name = item['metadata']['name']
            deleteurl = f"{env_url}/{name}"
            print(deleteurl)
            response = make_v3_api("DELETE", deleteurl, None, None)
            status_code = response.status_code
            print(f"Delete config context {name} , response code {status_code}")
    else:
        print("no config context to delete")

def delete_workflow_handlers():
    response = make_v3_api("GET", config["urls"]["ADD_DRIVER"], None, None)
    try:
        data = yaml.safe_load(response.content)
    except yaml.YAMLError as e:
        print(f"Error parsing get config context response: {e}")
        return None  # Return None on parsing error

    if "items" in data:
        items = data["items"]
        env_url = config["urls"]["ADD_DRIVER"]
        for item in items:
            name = item['metadata']['name']
            deleteurl = f"{env_url}/{name}"
            print(deleteurl)
            response = make_v3_api("DELETE", deleteurl, None, None)
            status_code = response.status_code
            print(f"Delete driver {name} , response code {status_code}")
    else:
        print("no workflow handlers to delete")


def delete_repository():
    repourl = config["urls"]["ADD_REPO"]
    reponame = f"{repourl}/catalog-code"
    
    try:
        response = make_v3_api("DELETE", reponame, None, None)
    except Exception as e:
        print(f"Failed to delete repository: {e}")
        return None  # Return None on parsing error

def delete_resources_in_orgs():
    delete_environment_templates()
    delete_resource_templates()
    delete_config_contexts()
    delete_workflow_handlers()
    delete_repository()

read_values()
delete_resources_in_orgs()