# inference_component.py
from kfp.v2.dsl import component, Input, Artifact

@component(
    base_image="python:3.9",  # kserve on python 3.10 comes with a dependency that fails to get installed
    packages_to_install=["kserve==0.11.0", "scikit-learn~=1.0.2"],
    output_component_file='src/components_yaml/inference_component.yaml',
)
def inference(
    model_name: str,
    scaler_in: Input[Artifact]
):
    """
    Test inference.
    """
    from kserve import KServeClient
    import requests
    import pickle
    import logging
    from kserve import utils
    from urllib.parse import urlsplit
    import re
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def get_istio_auth_session(url: str, username: str, password: str) -> dict:
        """
        Determine if the specified URL is secured by Dex and try to obtain a session cookie.
        WARNING: only Dex `staticPasswords` and `LDAP` authentication are currently supported
                 (we default default to using `staticPasswords` if both are enabled)
    
        :param url: Kubeflow server URL, including protocol
        :param username: Dex `staticPasswords` or `LDAP` username
        :param password: Dex `staticPasswords` or `LDAP` password
        :return: auth session information
        """
        # define the default return object
        auth_session = {
            "endpoint_url": url,    # KF endpoint URL
            "redirect_url": None,   # KF redirect URL, if applicable
            "dex_login_url": None,  # Dex login URL (for POST of credentials)
            "is_secured": None,     # True if KF endpoint is secured
            "session_cookie": None  # Resulting session cookies in the form "key1=value1; key2=value2"
        }
    
        # use a persistent session (for cookies)
        with requests.Session() as s:
    
            ################
            # Determine if Endpoint is Secured
            ################
            resp = s.get(url, allow_redirects=True)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"HTTP status code '{resp.status_code}' for GET against: {url}"
                )
    
            auth_session["redirect_url"] = resp.url
    
            # if we were NOT redirected, then the endpoint is UNSECURED
            if len(resp.history) == 0:
                auth_session["is_secured"] = False
                return auth_session
            else:
                auth_session["is_secured"] = True
    
            ################
            # Get Dex Login URL
            ################
            redirect_url_obj = urlsplit(auth_session["redirect_url"])
    
            # if we are at `/auth?=xxxx` path, we need to select an auth type
            if re.search(r"/auth$", redirect_url_obj.path):
    
                #######
                # TIP: choose the default auth type by including ONE of the following
                #######
    
                # OPTION 1: set "staticPasswords" as default auth type
                redirect_url_obj = redirect_url_obj._replace(
                    path=re.sub(r"/auth$", "/auth/local", redirect_url_obj.path)
                )
                # OPTION 2: set "ldap" as default auth type
                # redirect_url_obj = redirect_url_obj._replace(
                #     path=re.sub(r"/auth$", "/auth/ldap", redirect_url_obj.path)
                # )
    
            # if we are at `/auth/xxxx/login` path, then no further action is needed (we can use it for login POST)
            if re.search(r"/auth/.*/login$", redirect_url_obj.path):
                auth_session["dex_login_url"] = redirect_url_obj.geturl()
    
            # else, we need to be redirected to the actual login page
            else:
                # this GET should redirect us to the `/auth/xxxx/login` path
                resp = s.get(redirect_url_obj.geturl(), allow_redirects=True)
                if resp.status_code != 200:
                    raise RuntimeError(
                        f"HTTP status code '{resp.status_code}' for GET against: {redirect_url_obj.geturl()}"
                    )
    
                # set the login url
                auth_session["dex_login_url"] = resp.url
    
            ################
            # Attempt Dex Login
            ################
            resp = s.post(
                auth_session["dex_login_url"],
                data={"login": username, "password": password},
                allow_redirects=True
            )
            if len(resp.history) == 0:
                raise RuntimeError(
                    f"Login credentials were probably invalid - "
                    f"No redirect after POST to: {auth_session['dex_login_url']}"
                )
    
            # store the session cookies in a "key1=value1; key2=value2" string
            auth_session["session_cookie"] = "; ".join([f"{c.name}={c.value}" for c in s.cookies])
    
        return auth_session
    
    KUBEFLOW_ENDPOINT = "http://istio-ingressgateway.istio-system.svc.cluster.local:80"
    KUBEFLOW_USERNAME = "user@example.com"
    KUBEFLOW_PASSWORD = "12341234"
    
    auth_session = get_istio_auth_session(
    url=KUBEFLOW_ENDPOINT,
    username=KUBEFLOW_USERNAME,
    password=KUBEFLOW_PASSWORD,
    )
    TOKEN = auth_session["session_cookie"].replace("authservice_session=", "")
    print("Token:", TOKEN)

    namespace = utils.get_default_target_namespace()

    input_sample = [[5.6, 0.54, 0.04, 1.7, 0.049, 5, 13, 0.9942, 3.72, 0.58, 11.4],
                    [11.3, 0.34, 0.45, 2, 0.082, 6, 15, 0.9988, 2.94, 0.66, 9.2]]

    logger.info(f"Loading standard scaler from: {scaler_in.path}")
    with open(scaler_in.path, 'rb') as fp:
        scaler = pickle.load(fp)

    logger.info(f"Standardizing sample: {scaler_in.path}")
    input_sample = scaler.transform(input_sample)

    # get inference service
    KServe = KServeClient()

    # wait for deployment to be ready
    KServe.get(model_name, namespace=namespace, watch=True, timeout_seconds=120)

    inference_service = KServe.get(model_name, namespace=namespace)
    logger.info(f"inference_service: {inference_service}")

    is_url = f"http://istio-ingressgateway.istio-system.svc.cluster.local:80/v1/models/{model_name}:predict"
    header = {"Host": f"{model_name}.{namespace}.example.com"}
    
    logger.info(f"\nInference service status:\n{inference_service['status']}")
    logger.info(f"\nInference service URL:\n{is_url}\n")

    inference_input = {
        'instances': input_sample.tolist()
    }
    response = requests.post(
        is_url,
        json=inference_input,
        headers=header,
        cookies={"authservice_session": TOKEN}
        
    )
    if response.status_code != 200:
        raise RuntimeError(f"HTTP status code '{response.status_code}': {response.json()}")
    
    logger.info(f"\nPrediction response:\n{response.json()}\n")