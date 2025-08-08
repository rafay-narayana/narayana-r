import os
import yaml
import requests
import base64


def read_template(path):
    resources = []
    contexts = []

    with open(path, "r") as f:
        data = yaml.safe_load(f)
        if "spec" in data and "resources" in data["spec"]:
            resources = data["spec"]["resources"]
        if "spec" in data and "contexts" in data["spec"]:
            contexts = data["spec"]["contexts"]

    # Print resources
    print("==== resources ======")
    for resource in resources:
        print(resource["name"] + "-" + resource["resourceOptions"]["version"])

    print("==== context ======")
    for context in contexts:
        print(context["name"])

    driver_names = []
    print("==== drivers ======")
    hooks = data.get("spec", {}).get("hooks", {})
    for _, hook_data in hooks.items():
        for hook in hook_data:
            driver = hook.get("driver", {})
            driver_name = driver.get("name")
            if driver_name:
                print(driver_name)


def get_files_in_specific_folders(root_dir, specific_folders):

    files = []
    for folder in specific_folders:
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path):
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    file_size = os.path.getsize(file_path)
                    if file_size > 0:
                        files.append(file_path)

    #  for f in files:
    #     print(f)

    return files


def get_yaml_files(directory):
    yaml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                yaml_files.append(os.path.join(root, file))

    # for f in yaml_files:
    #    print(" --- " + f)

    return yaml_files


def validate_templates(directory_path):
    files = get_yaml_files(directory_path)
    for f in files:
        if validate_template_file(f, directory_path) is False:
            return False

    return True


def validate_template_file(template_file_path, root_dir):
    print(f"Validating file.. {template_file_path}")
    resources = []
    contexts = []

    with open(template_file_path, "r") as f:
        data = yaml.safe_load(f)
        if "spec" in data and "resources" in data["spec"]:
            resources = data["spec"]["resources"]
        if "spec" in data and "contexts" in data["spec"]:
            contexts = data["spec"]["contexts"]

    for resource in resources:
        print(resource["name"] + "-" + resource["resourceOptions"]["version"])
        res_path = f"{root_dir}/res-templates/{resource['name']}/{resource['resourceOptions']['version']}/{resource['name']}.yaml"
        if os.path.isfile(res_path) is False:
            print(
                f"\033[31m Resource file {res_path} does not exist, failed to create {template_file_path}\033[0m"
            )
            return False

    for context in contexts:
        if "data" not in context:
            print(context["name"])
            context_path = f"{root_dir}/context/{context['name']}.yaml"
            if os.path.isfile(context_path) is False:
                print(
                    f"\033[31m Context file {context_path} does not exist, failed to create {template_file_path}\033[0m"
                )
                return False

    driver_names = []
    hooks = data.get("spec", {}).get("hooks", {})
    for _, hook_data in hooks.items():
        for hook in hook_data:
            driver = hook.get("driver", {})
            driver_name = driver.get("name")
            if driver_name:
                driver_names.append(driver_name)

    for driver in driver_names:
        print(driver)
        context_path = f"{root_dir}/workflow-handlers/{driver}.yaml"
        if os.path.isfile(context_path) is False:
            print(
                f"\033[31m Driver file {context_path} does not exist, failed to create {template_file_path}\033[0m"
            )
            return False

    return True


def make_rest_api_call(method, url, headers, params, data):
    try:
        response = requests.request(
            method, url, headers=headers, params=params, data=data
        )
        #response.raise_for_status()  # Raise an exception for error status codes
    except requests.exceptions.RequestException as e:
        print(f"Error making API call method {method}: {e}")
        if response is not None and response.content:
            print(f"{e}\n\033[31m{response.content.decode()}\033[0m")
        raise 
    return response


def make_v1_api(method, url, params, data):
    headers = {
        "Content-Type": "application/yaml",
        "X-RAFAY-API-KEYID": config["API_KEY"],
        "X-ORGANIZATION-ID": config["ORG_HASH"],
    }
    response = make_rest_api_call(method, url, headers, params, data)
    return response


def make_v3_api(method, url, params, data):
    headers = {
        "Content-Type": "application/yaml",
        "X-API-KEY": config["API_KEY"],
        "X-ORGANIZATION-ID": config["ORG_HASH"],
    }
    response = make_rest_api_call(method, url, headers, params, data)
    return response


def create_entity(file_path,shr=False):
    with open(file_path, "r") as entity:
        data = yaml.safe_load(entity)

        if "kind" not in data:
            print("Failed to get type kind of the template")
            return False

        kind = data["kind"]
        # special check to update config context from env variable
        if kind == "ConfigContext" and data["metadata"]["name"] == "system-dns-config" :
            spl_config_context = os.environ.get("CONFIG_CONTEXT_SPL")
            if spl_config_context is not None:
                yaml_bytes = base64.b64decode(spl_config_context)
                yaml_string = yaml_bytes.decode('utf-8')
                yaml_data = yaml.safe_load(yaml_string)
                data = yaml_data
        data["metadata"]["project"] = config["PROJECT_NAME"]

        # add version to annotation
        if not "annotations" in  data["metadata"]:
            data["metadata"]["annotations"] = {}
        data["metadata"]["annotations"]["eaas.envmgmt.io/releaseversion"] = config["VERSION"]
        
        # change controller endpoint for ..may not be needed in future as we take it from system
        if kind == "EnvironmentTemplate":
            ii = 0
            if "spec" in data and "contexts" in data["spec"]:
                while ii < len(data["spec"]["contexts"]):
                    if "data" in data["spec"]["contexts"][ii]:
                        kk = 0
                        while kk < len(data["spec"]["contexts"][ii]["data"]["envs"]):
                            print(data["spec"]["contexts"][ii]["data"]["envs"][kk]["key"])
                            if data["spec"]["contexts"][ii]["data"]["envs"][kk]["key"] == "Controller Endpoint" :
                                data["spec"]["contexts"][ii]["data"]["envs"][kk]["value"] = config["HOST_ENV"]
                            kk += 1
                    ii += 1
        if kind == "ComputeProfile":
            ii = 0
            if "spec" in data and "envVars" in data["spec"]:
                while ii < len(data["spec"]["envVars"]):
                    if data["spec"]["envVars"][ii]["key"] == "Controller Endpoint" :
                        data["spec"]["envVars"][ii]["value"] = config["HOST_ENV"]
                    ii += 1
        if kind == "ServiceProfile":
            ii = 0
            if "spec" in data and "envVars" in data["spec"]:
                while ii < len(data["spec"]["envVars"]):
                    if data["spec"]["envVars"][ii]["key"] == "Controller Endpoint" :
                        data["spec"]["envVars"][ii]["value"] = config["HOST_ENV"]
                    ii += 1


        yaml_data = yaml.dump(data, default_flow_style=False)
        template_name = data["metadata"]["name"]

        if kind == "SecretSealer":
            print("Creating SecretSealer")
            response = make_v3_api(
                "POST", config["urls"]["ADD_SECRETSEALER"], None, yaml_data
            )

        elif kind == "Agent":
            print(f"Creating Agent --> {template_name}")
            response = make_v3_api("POST", config["urls"]["ADD_AGENT"], None, yaml_data)

        elif kind == "Repository":
            print(f"Creating Repository --> {template_name}")
            response = make_v3_api("POST", config["urls"]["ADD_REPO"], None, yaml_data)

        elif kind == "ConfigContext":
            print(f"Creating Context --> {template_name}")
            response = create_config_context(data["metadata"]["name"], data, yaml_data)

        elif kind == "ResourceTemplate":
            print(f"Creating ResourceTemplate --> {template_name}")
            response = create_resource_template(data["metadata"]["name"], data, "")

        elif kind == "EnvironmentTemplate":
            print(f"Creating EnvironmentTemplate --> {template_name}")
            if shr:
                print(f"Creating EnvironmentTemplate --> {template_name} with sharing")
                data["spec"]["sharing"] = {"enabled": True, "projects": [{"name": "*"}]}
                yaml_data = yaml.dump(data, default_flow_style=False)
            response = create_environment_template(
                data["metadata"]["name"], data, yaml_data
            )

        elif kind == "Driver":
            print(f"Creating Driver/Workflow handler --> {template_name}")
            response = make_v3_api(
                "POST", config["urls"]["ADD_DRIVER"], None, yaml_data
            )
        elif kind == "WorkflowHandler":
            print(f"Creating Driver/Workflow handler --> {template_name}")
            response = make_v3_api(
                "POST", config["urls"]["ADD_WRKFLW"], None, yaml_data
            )

        elif kind == "ComputeProfile":
            print(f"Creating Compute Profile --> {template_name}")
            response = make_v3_api(
                "POST", config["urls"]["ADD_CPROFILE"], None, yaml_data
            )
        elif kind == "ServiceProfile":
            print(f"Creating Service Profile --> {template_name}")
            response = make_v3_api(
                "POST", config["urls"]["ADD_SPROFILE"], None, yaml_data
            )

        else:
            print("Invalid type")
            return

    if config["DEBUG"]:
        print("------------------ Response ------------------ ")
        print(response.status_code)
        print(response.content)


def validate_config_context_data(data):
    if "metadata" not in data or "name" not in data["metadata"]:
        print("Invalid ConfigContext: Missing 'name' in metadata.")
        return False

    return True


def create_environment_template(em_name, data, yaml_data):
    try:
        print(f"Creating  Environment Template '{em_name}'")
        response = make_v3_api(
            "POST", config["urls"]["ADD_ENVIRONMENT"], None, yaml_data
        )

        if (response.status_code == 201 or response.status_code == 200 ):  # Assuming 200/201 means successfully created
            print(f"Environment Template '{em_name}' created successfully.")
        else:
            print(f"Failed to create Environment Template '{em_name}'. Response: {response.status_code}")
        
        return response

    except Exception as e:
        print(f"Error creating environment template {em_name}: {e}")
        return None


def create_resource_template(em_name, data, yaml_data):
    if config["SHARING"]:
        data["spec"]["sharing"] = {"enabled": True, "projects": [{"name": "*"}]}

    if config["ARTIFACT_DRIVER"]:
        # "artifactWorkflowHandler" exists as a sub-key of "spec"
        if "artifactWorkflowHandler" in data["spec"]:
            data["spec"]["artifactWorkflowHandler"]["data"]["config"]["container"]["image"] = config["ARTIFACT_DRIVER"]
        
        # artifactDriver exists as sub-key of "spec"
        if "artifactDriver" in data["spec"]:
            data["spec"]["artifactDriver"]["data"]["config"]["container"]["image"] = config["ARTIFACT_DRIVER"]

    yaml_data = yaml.dump(data, default_flow_style=False)
    response = make_v3_api("POST", config["urls"]["ADD_RESOURCE"], None, yaml_data)

    return response

def create_config_context(config_context_name, data, yaml_data):
    print(f"Creating / Updating ConfigContext '{config_context_name}'")
    return make_v3_api("POST", config["urls"]["ADD_CONFIGCONTEXT"], None, yaml_data)


def create_resource(source_path, resource_type):
    directory_path = source_path + resource_type
    print(f"Creating resources of type --> {resource_type}")
    # print(f"Reading files from --> {directory_path}")
    files = get_yaml_files(directory_path)
    for f in files:
        print(f"{resource_type} --> {f}")
        if validate_template_file(f, source_path) is False:
            return False

        create_entity(f)
    return True

def create_resource_cprofile(source_path, resource_type):
    directory_path = source_path + resource_type
    if config["LOAD_ALL_TEMPLATES"]:
        print(f"Load all not done for resources of type --> {resource_type}")
    else:
        print(f"Loading Compute Profiles")
        templates = config["CPROFILES"]
        if templates is None:
            return True
        for t in templates:            
            if os.path.isfile(t):
                print(f"Loading compute profile {t}")
                if validate_template_file(t, source_path) is False:
                    print(f"Not a valid compute profile {t}")
                else:
                    create_entity(t)
            else:
                print(f"Not a valid compute profile {t}")
    return True

def create_resource_sprofile(source_path, resource_type):
    directory_path = source_path + resource_type
    if config["LOAD_ALL_TEMPLATES"]:
        print(f"Load all not done for resources of type --> {resource_type}")
    else:
        print(f"Loading Service Profiles")
        templates = config["SPROFILES"]
        if templates is None:
            return True
        for t in templates:            
            if os.path.isfile(t):
                print(f"Loading service profile {t}")
                if validate_template_file(t, source_path) is False:
                    print(f"Not a valid service profile {t}")
                else:
                    create_entity(t)
            else:
                print(f"Not a valid service profile {t}")
    return True

def create_resource_context(source_path, resource_type):
    directory_path = source_path + resource_type
    if config["LOAD_ALL_TEMPLATES"]:
        print(f"Load all not done for resources of type --> {resource_type}")
    else:
        print(f"Loading Config context")
        templates = config["CONTEXTS"]
        if templates is None:
            return True
        for t in templates:            
            if os.path.isfile(t):
                print(f"Loading service profile {t}")
                if validate_template_file(t, source_path) is False:
                    print(f"Not a valid service profile {t}")
                else:
                    create_entity(t)
            else:
                print(f"Not a valid service profile {t}")
    return True

def create_resource_res(source_path, resource_type):
    directory_path = source_path + resource_type

    if config["LOAD_ALL_TEMPLATES"]:
        print(f"Creating resources of type --> {resource_type}")
        files = get_yaml_files(directory_path)
        for f in files:
            print(f"{resource_type} --> {f}")
            if validate_template_file(f, source_path) is False:
                return False
            create_entity(f)
    else:
        print(f"Loading specific resource templates")
        templates = config["RESTEMPLATES"]
        if templates is None:
            return True
        for t in templates:            
            if os.path.isfile(t):
                print(f"Loading resource template {t}")
                if validate_template_file(t, source_path) is False:
                    print(f"Not a valid template {t}")
                else:
                    create_entity(t)
            else:
                print(f"Not a valid template {t}")
    return True

def create_environment_resource(source_path, resource_type):
    directory_path = source_path + resource_type
    # print(f"Reading files from --> {directory_path}")

    if config["LOAD_ALL_TEMPLATES"]:
        print(f"Loading all environment templates")
        files = get_yaml_files(directory_path)
        for f in files:
            print(f"{resource_type} --> {f}")
            validate_create_em_template(f, source_path)
    else:
        print(f"Loading specific environment templates")
        templates = config["TEMPLATES"]
        # handle empty
        if templates is None:
            return True
        for t in templates:            
            if os.path.isdir(t):
                print(f"Loading templates from directory {t}")
                files = get_yaml_files(t)  # Pass `t` here as a template path or directory
                for file in files:
                    validate_create_em_template(file, source_path)
            elif os.path.isfile(t):
                print(f"Loading environment template {t}")
                validate_create_em_template(t, source_path)
            else:
                print(f"Not a valid template {t}")
    return True
def create_shrenvironment_resource(source_path, resource_type):
    directory_path = source_path + resource_type
    # print(f"Reading files from --> {directory_path}")

    if config["LOAD_ALL_TEMPLATES"]:
        print(f"Loading all environment templates")
        files = get_yaml_files(directory_path)
        for f in files:
            print(f"{resource_type} --> {f}")
            validate_create_em_template(f, source_path)
    else:
        print(f"Loading specific environment templates to share")
        templates = config["SHRTEMPLATES"]
        # handle empty
        if templates is None:
            return True
        for t in templates:            
            if os.path.isdir(t):
                print(f"Loading templates from directory {t}")
                files = get_yaml_files(t)  # Pass `t` here as a template path or directory
                for file in files:
                    validate_create_em_template_shr(file, source_path)
            elif os.path.isfile(t):
                print(f"Loading environment template {t}")
                validate_create_em_template_shr(t, source_path)
            else:
                print(f"Not a valid template {t}")
    return True


def validate_create_em_template(file, source_path):
    if validate_template_file(file, source_path) is False:
        return False
    create_entity(file) 

def validate_create_em_template_shr(file, source_path):
    if validate_template_file(file, source_path) is False:
        return False
    create_entity(file,shr=True) 

def create_resource_workflow_handlers(source_path, resource_type):
    directory_path = source_path + resource_type
    if config["LOAD_ALL_TEMPLATES"]:
        print(f"Load all not done for resources of type --> {resource_type}")
    else:
        print(f"Loading Workflow Handlers")
        templates = config["WRKFLW"]
        if templates is None:
            return True
        for t in templates:            
            if os.path.isfile(t):
                print(f"Loading workflow handler {t}")
                if validate_template_file(t, source_path) is False:
                    print(f"Not a valid workflow handler {t}")
                else:
                    create_entity(t)
            else:
                print(f"Not a workflow handler {t}")
    return True

def get_project_hash():
    response = make_v3_api("GET", config["GET_PROJECT_DETAIL"], params=None, data=None)
    try:
        data = yaml.safe_load(response.content)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML response: {e}")
        return None  # Return None on parsing error

    project_hash = data.get("status", {}).get("extra", {}).get("data", {}).get("id")

    return project_hash


def load_all_resources():
    current_directory = os.getcwd()
    tRoot = current_directory + "/../"

    # create_resource(tRoot, "sealer")
    # create_resource(tRoot, "agent")

    create_resource(tRoot, "repository")
    create_resource_context(tRoot, "context")
    #create_resource(tRoot, "workflow-handlers")
    create_resource_workflow_handlers(tRoot, "workflow-handlers")
    create_resource_res(tRoot, "res-templates")
    create_environment_resource(tRoot, "env-templates")
    create_shrenvironment_resource(tRoot, "env-templates")
    create_resource_cprofile(tRoot, "compute-profiles")
    create_resource_sprofile(tRoot, "service-profiles")


def create_project():
    proj = config["PROJECT_NAME"]
    try:
        response = make_v3_api("GET", config["urls"]["GET_PROJECT_DETAIL"], None, None)
        print(f"Project {proj} found, doing nothing")
    except Exception as e:
        print(f"Project not found.. creating project {proj}")
        project_spec = f"""
      apiVersion: system.k8smgmt.io/v3
      kind: Project
      metadata:
         name: {proj}
      spec:
         default: false
         driftWebhook:
            enable: true
      """
        response = make_v3_api(
            "POST", config["urls"]["CREATE_PROJECT"], None, project_spec
        )


def read_values(partner_api_key, values_file):
     

    with open(values_file, "r") as f:
        data = yaml.safe_load(f)
        HOST_ENV = data["hostenv"]
        PROJECT_NAME = data["projectname"]
        BASE_URL = f"https://{HOST_ENV}"
        OPS_ENV = data["opsenv"]
        OPS_URL = f"https://{OPS_ENV}"
        if "templates" not in data:
            data["templates"] = []
        if "shr-templates" not in data:    
            data["shr-templates"] = []
        if "service-profiles" not in data:
            data["service-profiles"] = []
        if "compute-profiles" not in data:
            data["compute-profiles"] = []
        if "res-templates" not in data:
            data["res-templates"] = []
        if "context" not in data:
            data["context"] = []
        if "workflow-handlers" not in data:
            data["workflow-handlers"] = []
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
                "GET_ORGS_V1": f"{OPS_URL}/auth/v1/organizations/?limit=200&offset=0",
                "ADD_CPROFILE":f"{BASE_URL}/apis/paas.envmgmt.io/v1/projects/{PROJECT_NAME}/computeprofiles",
                "ADD_SPROFILE":f"{BASE_URL}/apis/paas.envmgmt.io/v1/projects/{PROJECT_NAME}/serviceprofiles",
                "ADD_WRKFLW": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/{PROJECT_NAME}/workflowhandlers",

            },
            "HOST_ENV": data["hostenv"],
            "API_KEY": partner_api_key,
            "ORG_HASH": data["org_hash"],
            "LOAD_ALL_TEMPLATES": data["load_all_templates"],
            "LOAD_ALL_ORGS": data["load_all_orgs"],
            "PROJECT_NAME": data["projectname"],
            "DEBUG": data["debug"],
            "SHARING": data["sharing"],
            "TEMPLATES": data["templates"],
            "SHRTEMPLATES": data["shr-templates"],
            "ARTIFACT_DRIVER": data["artifact_driver"],
            "VERSION": data["version"],
            "CPROFILES": data["compute-profiles"],
            "SPROFILES": data["service-profiles"],
            "RESTEMPLATES": data["res-templates"],
            "CONTEXTS": data["context"],
            "WRKFLW": data["workflow-handlers"]
        }


def load_templates():
    if config["LOAD_ALL_ORGS"]:
        load_all_orgs()
    else:
        load_specific_orgs()


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
        # Not needed for Action based loaded as it is for Rafay as a Partner 
        # if has_default_org:
        #     org_list= []
        #     org_list.append(default_org_id)
        print("Orgs to be processed:", org_list)
        for id in org_list:
            print(f"loading: {id}")
            load_for_org(id)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML response: {e}")
        return None  # Return None on parsing error




def load_specific_orgs():
    if config["ORG_HASH"] is None:
        print("Nothing to load as org list is empty")
        return
    print("Loading specific orgs")
    org_list = config["ORG_HASH"].split(",")

    for org_hash in org_list:
        load_for_org(org_hash)

def load_for_org(org_hash):
    print(f"======= Loading templates for org {org_hash} =======")
    config["ORG_HASH"] = org_hash
    # create_project() assume projects are always present - except check for default-catalog
    if config["PROJECT_NAME"] == "default-catalog":
        create_project() 
    load_all_resources()
    print(f"======= Completed loading templates for org {org_hash} =======")


if __name__ == "__main__":
    partner_api_key = os.environ.get("PARTNER_API_KEY")
    values_file = os.environ.get("VALUES_FILE")
    missing_envs = []
    if partner_api_key is None:
        missing_envs.append("PARTNER_API_KEY")
    if values_file is None:
        missing_envs.append("VALUES_FILE")
    if len(missing_envs) > 0:
        print("\nThe following environment variables are missing:- ")
        for env in missing_envs:
            print("  -",env)
        exit(255)
    print("Using values file:- ",values_file)
    read_values(partner_api_key=partner_api_key, values_file=values_file)
    load_templates()

