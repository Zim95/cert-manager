# cert-manager
Manages Certificates for our microservices


# Dev Setup - Kubernetes
NOTE: This setup is a little different on windows. Please use WSL in windows.
    Basically, the script files wont work on windows and therefore, you need to manually setup.
    The developer of this repository hates working with windows.

1. To Develop inside kubernetes, you need to first install Docker Desktop and follow this guideline: `https://docs.docker.com/desktop/features/kubernetes/`.

2. Once `kubectl` is setup and you have the `docker-desktop` cluster ready. We can proceed further.

3. First of all, make sure `./infra/development/entrypoint-development.sh` is an executable.
    ```
    chmod +x ./infra/development/entrypoint-development.sh
    ```
    NOTE: Even if you do this in the dockerfile, when you mount the hostpath, the file inside the container will be overwritten by our local file.
        So, when the pod tries to run entrypoint-development.sh, it is trying to run our local file that has been mapped to the pod.
        So, we need to make sure our local file is an executable.
    
    In prod envs, we dont mount hostpath, so we dont need to worry about this. The chmod in the dockerfile will take effect.

4. Type the following to build the docker image for k8s development:
    ```
    ./scripts/development/development-build.sh <docker-username> <docker-repository>
    ```
    This will build the docker image required for k8s development.

    OR

    You can also edit the `Makefile`. Set values for your username and repository name.
    Then you can use the following command to build the docker image:
    ```
    make dev_build
    ```

5. Next you can setup the development environment by hitting this command:
    ```
    ./scripts/development/development-setup.sh <namespace> <absolute-path-to-current-working-directory>
    ```

    OR

    You can also edit the `Makefile`. Set values for your namespace and host directory.
    Then you can use the following command to setup the development environment:
    ```
    make dev_setup
    ```

6. Now, that we have setup, we can check the pods with the following command:
    ```
    $ kubectl get pods -n <namespace>
    NAME                                            READY   STATUS    RESTARTS   AGE
    cert-manager-development-5fb88464fb-xwf8q            1/1     Running   0          9m34s
    ```

8. If the pod is running, exec into the pod:
    ```
    kubectl exec -it cert-manager-development-5fb88464fb-xwf8q -n <namespace> -- bash
    ```
    This will be the terminal where you run your code in.

9. Next from your local working directory, try creating a file.
    ```
    touch test1234
    ```
    This file should appear inside the pod. Type `ls` to check.

10. Once the file appears, you are good. You can make changes to your current workspace folder and then run the code from within the pod.

11. Finally, once done, you can delete everything by hitting this command:
    ```
    ./scripts/development/development-teardown.sh <namespace>
    ```
    Or
    ```
    make dev_teardown
    ```

12. Now, we need to activate teh virtual env once we are inside the container.
    ```
    source $(poetry env info --path)/bin/activate
    ```

13. Install all dependencies with poetry.
    ```
    poetry install
    ```

NOTE: To run anything inside the shell, activate the virtualenv. But to run anything as a container command, we need to use `poetry run`.


# Working with dependencies
1. Adding dependencies:
    ```
    poetry add <dependency>
    ```

2. Adding dependencies with specific versions:
    - Add the dependency with version in the `pyproject.toml` file.
    - Then run `poetry update`.

3. Removing a dependency
    - `poetry remove <package>`


# Adding a new service
1. Simply add the service name to services.list.json.


# Prod deployment
1. Build: `make prod_build`.
2. Setup: `make prod_setup`.
3. Teardown: `make prod_teardown`.
