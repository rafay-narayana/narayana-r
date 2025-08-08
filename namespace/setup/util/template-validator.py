import os
import yaml
import requests


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

    #for f in yaml_files:
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
    print(f"Validation successful for file.. {template_file_path}")
    return True


def validate_templates(source_path, resource_type):
    directory_path = source_path + resource_type
    print(f"Validating resources of type --> {resource_type}")
    files = get_yaml_files(directory_path)
    for f in files:
        if validate_template_file(f, source_path) is False:
            return False
    return True


def load_all():
    current_directory = os.getcwd()
    tRoot = current_directory + "/../"

    # validate_templates(tRoot, "sealer")
    # validate_templates(tRoot, "agent")

    validate_templates(tRoot, "repository")
    validate_templates(tRoot, "context")
    validate_templates(tRoot, "workflow-handlers")
    validate_templates(tRoot, "res-templates")
    validate_templates(tRoot, "env-templates")

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


read_values()
load_all()