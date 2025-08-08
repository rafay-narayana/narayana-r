import os
import yaml
import requests
import warnings
warnings.filterwarnings('ignore')

def make_v1_api(method, url, params, data):
    headers = {
        "Content-Type": "application/yaml",
        "X-RAFAY-API-KEYID": config["API_KEY"],
    }
    response = make_rest_api_call(method, url, headers, params, data)
    return response
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
def make_v3_api_org(method, url, org):
    headers = {
        "Content-Type": "application/yaml",
        "X-API-KEY": config["API_KEY"],
        "X-ORGANIZATION-ID": org,
    }
    response = make_rest_api_call(method, url, headers, None, None)
    return response

def read_values():
    

    with open("values.yaml", "r") as f:
        data = yaml.safe_load(f)
        HOST_ENV = data["hostenv"]
        PROJECT_NAME = data["projectname"]
        BASE_URL = f"https://{HOST_ENV}"
        OPS_ENV = data["opsenv"]
        OPS_URL = f"https://{OPS_ENV}"

        global config
        config = {
            "urls": {
                "BASE_URL": BASE_URL,
                "ADD_ENVIRONMENT": f"{BASE_URL}/apis/eaas.envmgmt.io/v1/projects/{PROJECT_NAME}/environmenttemplates",
                "GET_ORGS_V1": f"{OPS_URL}/auth/v1/organizations/?limit=100&offset=0"
            },
                "HOST_ENV": data["hostenv"],
                "API_KEY": data["apikey"],
                "PROJECT_NAME": data["projectname"],
                "DEBUG": data["debug"],
                "SHARING": data["sharing"],
                "VERSION": data["version"],
            
        }
         

 

def get_orgs():
    response = make_v1_api("GET", config["urls"]["GET_ORGS_V1"], params=None, data=None)
    orglist = ''
    totorglist = ''
    ntotorglist = ''
    norglist= ''
    print("Orgs processed:")
    while True:
        data = yaml.safe_load(response.content)
        for k in data["results"]:
            if k['active'] == True and k['approved'] == True:
                print (k['partner']['name'],k['id'], k['name'])
                chk1 = True
                if True:
                    totorglist = totorglist + k['id'] + '-'+ k['name'] + ","
                    ntotorglist = ntotorglist + k['id'] + ","
                    tt = make_v3_api_org("GET", config["urls"]["ADD_ENVIRONMENT"], k['id'])
                    if (len(tt.content) < 100):
                        print (k['partner']['name'],k['id'], k['name'])
                        orglist = orglist + k['id'] + ","
                    else:
                        getd = yaml.safe_load(tt.content)
                        if "items" in getd:
                            for k1 in getd["items"]:
                                if k1["metadata"]["name"][:7] == 'system-' and "eaas.envmgmt.io/releaseversion" in k1["metadata"]["annotations"]: 
                                    if k1["metadata"]["annotations"]["eaas.envmgmt.io/releaseversion"] == config["VERSION"]:
                                        chk1 = False
                                        break
                        if chk1 == True:
                            norglist = norglist + k['id'] + ","
        if data['next'] == None:
            break
        response = make_v1_api("GET", data['next'], params=None, data=None)
   
    print("--------------")
    print("All Org list:")
    print(ntotorglist[:-1])
    print("--------------")
    print("Org with no templates:")
    print(orglist[:-1])
    print("Org with not matching version:")
    print(norglist[:-1])

if __name__ == "__main__":
    read_values()
    get_orgs()