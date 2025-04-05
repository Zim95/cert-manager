"""
This script generates certificates for SSL based communication
between GRPC Server and Client.

For any inquiries, these are the emails of the Authors:

-> Namah Shrestha: shresthanamah@gmail.com
"""
# builtins
import os
import logging
import sys
import json
import base64

# third party
import kubernetes
import click


# logging setup
logger: logging.Logger = logging.getLogger(__name__)  # create logger
stream_handler: logging.StreamHandler = logging.StreamHandler(stream=sys.stdout)  # create stream handler
formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # create formatter
stream_handler.setFormatter(formatter)  # set formatter for handler
logger.addHandler(hdlr=stream_handler)  # add handler
logger.setLevel(logging.DEBUG)  # add level


# ENV
BASE_CERT_DIRECTORY: str = os.getenv("CERT_DIRECTORY", "./cert")
TIMEOUT: int = int(os.getenv("TIMEOUT", 365*24*60*60))  # 365 days
NAMESPACE: str = os.getenv("NAMESPACE", "default")
SERVICES_LIST_JSON_FILE: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.environ.get("SERVICES_LIST_JSON_FILE", "services.list.json")))


def execute_command(command: str) -> None:
    """
    Execute the terminal command.
    :params:
        :command: str: Terminal Command.
    :returns: None

    Author: Namah Shrestha
    """
    try:
        logger.info(f"Executing command: {command}")
        os.system(command)
    except Exception as e:
        logger.error(f"Error while executing command: {e}")
        raise Exception(e)


def get_certificate_config(base_cert_directory: str, namespace: str, service_name: str) -> dict:
    """
    Get the certificate configuration from the service name.
    :params:
        :base_cert_directory: str: The base certificate directory.
        :namespace: str: The namespace of the service.
        :service_name: str: The name of ths service.
    :returns: dict: Certificate Configuration

    Author: Namah Shrestha
    """
    return {
        "cert_directory": f"{base_cert_directory}/{service_name}",
        "secret_name": f"{service_name}-certs",
        "ca_common_name": f"{service_name}-ca",
        "client_common_name": f"{service_name}-client",
        "server_common_name": f"{service_name}.{namespace}.svc.cluster.local",
        "certificate_list": [
            "ca.crt", "ca.key", "ca.srl",
            "server.csr", "server.key", "server.crt",
            "client.csr", "client.key", "client.crt",
        ],
        "certificate_cleanup_list": ["server.csr", "client.csr"],
        "certificate_expiration": 365
    }


def create_cert_directory(cert_directory: str) -> None:
    """
    Create the certificate directory if it does not exist.
    :params:
        :cert_directory: str: Certificate directory.
    :returns: None

    Author: Namah Shrestha
    """
    try:
        if not os.path.exists(cert_directory):
            os.makedirs(cert_directory)
            logger.info(f"Successfully created directory: {cert_directory}")
        logger.info(f"Directory already exists: {cert_directory}")
    except Exception as e:
        logger.error(f"Error while creating cert directory: {e}")
        raise Exception(e)


def remove_files(cert_directory: str, file_list: list) -> None:
    """
    Remove old certificates from directory.
    :params:
        :cert_directory: str: Certificate directory.
        :file_;ist: str: List of files to remove.
    :returns: None

    Author: Namah Shrestha
    """
    for file in file_list:
        fname: str = f"{cert_directory}/{file}"
        try:
            os.remove(fname)
            logger.info(f"{fname} removed!")
        except Exception:
            logger.error(f"{fname} not found!")
            continue


def create_ca(cert_directory: str, common_name: str) -> None:
    """
    Create the CA in the cert_directory.
    :params:
        :cert_directory: str: Certificate directory.
        :common_name: str: The common name for the CA.
    :returns: None

    Author: Namah Shrestha
    """
    command: str = (
        f"openssl req -new -x509 -days 365 -nodes "
        f"-out {cert_directory}/ca.crt "
        f"-keyout {cert_directory}/ca.key "
        f"-subj '/CN={common_name}'"
    )
    try:
        execute_command(command)
    except Exception as e:
        logger.error(f"Error in creating CA: {e}")
        raise Exception(e)


def create_client_csr(cert_directory: str, common_name: str) -> None:
    """
    Create the Client Certificate Signing Request in the cert_directory.
    :params:
        :cert_directory: str: Certificate directory.
        :common_name: str: Common Name and SAN DNS entry.
    :returns: None

    Author: Namah Shrestha
    """
    san: str = f"subjectAltName=DNS:{common_name}"
    command: str = (
        f"openssl req -new -nodes "
        f"-out {cert_directory}/client.csr "
        f"-keyout {cert_directory}/client.key "
        f"-subj '/CN={common_name}' "
        f"-addext \"{san}\""
    )
    try:
        execute_command(command)
    except Exception as e:
        logger.error(f"Error in creating client CSR: {e}")
        raise Exception(e)


def create_client_cert(cert_directory: str, expiration: int) -> None:
    """
    Create the Client Certificate in the cert_directory.
    :params:
        :cert_directory: str: Certificate directory.
        :expiration: int: Expiration time in days.
    :returns: None

    Author: Namah Shrestha
    """
    required_files: list = [
        f"{cert_directory}/client.csr",
        f"{cert_directory}/ca.crt",
        f"{cert_directory}/ca.key"
    ]
    for required_file in required_files:
        if not os.path.exists(required_file):
            raise Exception(f"{required_file} not found! Cannot create client cert!")
    command: str = (
        f"openssl x509 -req "
        f"-in {cert_directory}/client.csr "
        f"-CA {cert_directory}/ca.crt "
        f"-CAkey {cert_directory}/ca.key "
        f"-CAcreateserial -out {cert_directory}/client.crt "
        f"-days {expiration}"
    )
    try:
        execute_command(command)
    except Exception as e:
        logger.error(f"Error in creating client cert: {e}")
        raise Exception(e)


def create_server_csr(cert_directory: str, common_name: str) -> None:
    """
    Create the Server Certificate Signing Request in the cert_directory.
    :params:
        :cert_directory: str: Certificate directory.
        :common_name: str: Common Name for the server. The name of the k8s service for the microservice.
    :returns: None

    Author: Namah Shrestha
    """
    san: str = f"subjectAltName=DNS:{common_name}"
    command: str = (
        f"openssl req -new -nodes "
        f"-out {cert_directory}/server.csr "
        f"-keyout {cert_directory}/server.key "
        f"-subj '/CN={common_name}' "
        f"-addext \"{san}\""
    )
    try:
        execute_command(command)
    except Exception as e:
        logger.error(f"Error in creating server CSR: {e}")
        raise Exception(e)


def create_server_cert(cert_directory: str, expiration: int) -> None:
    """
    Create the Server Certificate in the cert_directory.
    :params:
        :cert_directory: str: Certificate directory.
        :expiration: int: Expiration time in days.
    :returns: None

    Author: Namah Shrestha
    """
    required_files: list = [
        f"{cert_directory}/server.csr",
        f"{cert_directory}/ca.crt",
        f"{cert_directory}/ca.key"
    ]
    for required_file in required_files:
        if not os.path.exists(required_file):
            raise Exception(f"{required_file} not found! Cannot create server cert!")
    command: str = (
        f"openssl x509 -req "
        f"-in {cert_directory}/server.csr "
        f"-CA {cert_directory}/ca.crt "
        f"-CAkey {cert_directory}/ca.key "
        f"-CAcreateserial -out {cert_directory}/server.crt "
        f"-days {expiration}"
    )
    try:
        execute_command(command)
    except Exception as e:
        logger.error(f"Error in creating server cert: {e}")
        raise Exception(e)


def create_kubernetes_secrets(
    kcli: kubernetes.client.CoreV1Api,
    cert_directory: str,
    secret_name: str,
    namespace: str
) -> None:
    """
    Create the kubernetes secrets using kubernetes client in cluster config.
    Replace the secret if it already exists.
    :params:
        :kcli: kubernetes.client.CoreV1Api: Kubernetes Client.
        :cert_directory: str: Certificate directory.
        :secret_name: str: The name of the secret.
        :namespace: str: The namespace where the secret is to be deployed.
    :returns: None

    Author: Namah Shrestha
    """
    def read_cert(cert_name: str) -> bytes:
        """
        Read certificate and return certificate in bytes.
        :params:
            :cert_name: str: The name of the certificate.
        :returns: The certificate data in bytes.

        Author: Namah Shrestha
        """
        try:
            with open(f"{cert_directory}/{cert_name}", "rb") as fr:
                data: bytes = fr.read()
            return data
        except FileNotFoundError as fnfe:
            logger.error(f"Cannot find certificate! {cert_name}")
            raise FileNotFoundError(fnfe)
    
    try:
        ca_crt: bytes = read_cert("ca.crt")
        server_crt: bytes = read_cert("server.crt")
        server_key: bytes = read_cert("server.key")
        client_crt: bytes = read_cert("client.crt")
        client_key: bytes = read_cert("client.key")
        secret: kubernetes.client.V1Secret = kubernetes.client.V1Secret(
            metadata=kubernetes.client.V1ObjectMeta(name=secret_name),
            data={
                "ca.crt": base64.b64encode(ca_crt).decode('utf-8'),
                "server.crt": base64.b64encode(server_crt).decode('utf-8'),
                "server.key": base64.b64encode(server_key).decode('utf-8'),
                "client.crt": base64.b64encode(client_crt).decode('utf-8'),
                "client.key": base64.b64encode(client_key).decode('utf-8')
            }
        )
        kcli.create_namespaced_secret(namespace=namespace, body=secret)
        logger.info(f"Secret {secret_name} created successfully.")
    except FileNotFoundError as fnfe:
        raise FileNotFoundError(fnfe)
    except kubernetes.client.rest.ApiException as kcrae:
        if kcrae.status == 409:  # conflict secret already exists
            kcli.replace_namespaced_secret(name=secret_name, namespace=namespace, body=secret)
            logger.info(f"Secret {secret_name} replaced successfully.")
        else:
            logger.info(f"Error in creating kubernetes secret! {kcrae}")
            raise


def remove_old_secrets(kcli: kubernetes.client.CoreV1Api, secret_name: str, namespace: str) -> None:
    """
    Remove old kubernetes secret certificates.
    :params:
        :kcli: kubernetes.client.CoreV1Api: Kubernetes Client.
        :secret_name: str: Name of the secret.
        :namespace: str: Kubernetes namespace.
    :returns: None

    Author: Namah Shrestha
    """
    try:
        kcli.delete_namespaced_secret(name=secret_name, namespace=namespace)
        logger.info(f"Secret {secret_name} deleted successfully.")
    except kubernetes.client.rest.ApiException as kcrae:
        if kcrae.status == 404:
            logger.info(f"Secret {secret_name} not found in namespace {namespace}.")
        else:
            logger.error(f"Error in removing old kubernetes secret! {kcrae}")
            raise


def generate_service_certs(
    base_cert_directory: str,
    namespace: str,
    service_name: str,
    generate_k8s_secrets: bool,
) -> None:
    """
    Generate certificates for the service.
    :params:
        :service: str: The service name.
    :returns: None
    """
    try:
        # setup and removal of old certs
        certificate_config: dict = get_certificate_config(base_cert_directory, namespace, service_name)  # generate the config for certificates.
        create_cert_directory(cert_directory=certificate_config["cert_directory"])  # create directory if it does not exist.
        remove_files(cert_directory=certificate_config["cert_directory"], file_list=certificate_config["certificate_list"])  # remove old certificates.

        # creation of new certs
        create_ca(cert_directory=certificate_config["cert_directory"], common_name=certificate_config["ca_common_name"])  # create CA
        create_client_csr(cert_directory=certificate_config["cert_directory"], common_name=certificate_config["client_common_name"])  # create client CSR
        create_client_cert(cert_directory=certificate_config["cert_directory"], expiration=certificate_config["certificate_expiration"])  # create client cert
        create_server_csr(cert_directory=certificate_config["cert_directory"], common_name=certificate_config["server_common_name"])  # create server CSR
        create_server_cert(cert_directory=certificate_config["cert_directory"], expiration=certificate_config["certificate_expiration"])  # create server cert
        remove_files(cert_directory=certificate_config["cert_directory"], file_list=certificate_config["certificate_cleanup_list"])  # cleanup unnecessary certs: csr basically

        # kubernetes actions
        if generate_k8s_secrets:
            kubernetes.config.load_incluster_config()
            kcli: kubernetes.client.CoreV1Api = kubernetes.client.CoreV1Api()
            remove_old_secrets(kcli=kcli, secret_name=certificate_config["secret_name"], namespace=namespace)
            create_kubernetes_secrets(
                kcli=kcli,
                cert_directory=certificate_config["cert_directory"],
                secret_name=certificate_config["secret_name"],
                namespace=namespace
            )
    except Exception as e:
        logger.error(f"Error in processing cnf file: {e}")
        raise Exception(e)


@click.command()
@click.option(
    "--generate_k8s_secrets",
    type=bool,
    default=True,
    help="If set to true, certificates are stored as k8s secrets."
)
def main(generate_k8s_secrets: bool) -> None:
    try:
        with open(SERVICES_LIST_JSON_FILE, "r") as fr:
            services_list: list[str] = json.loads(fr.read())
        for service in services_list:
            generate_service_certs(BASE_CERT_DIRECTORY, NAMESPACE, service, generate_k8s_secrets)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise Exception(e)


if __name__ == "__main__":
    main()
