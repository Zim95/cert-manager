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

4. Create an `env.mk` file in the root of the repository and set the following variables:
    ```
    REPO_NAME=<your-docker-username>
    USER_NAME=<your-docker-username>
    NAMESPACE=<your-namespace>
    HOST_DIR=<absolute-path-to-your-local-working-directory>
    ```

5. Run the development build script, if not already done.
    ```
    make dev_build
    ```
    This will build the docker image required for k8s development.

6. Run the development setup script.
    ```
    make dev_setup
    ```
    This will setup the development environment.

7. Get inside the pod:
    First check the pod status:
    ```
    kubectl get pods -n <your-namespace>  --watch
    ```
    You should see the pod being created and then it will be running.
    ```
    NAME                                            READY   STATUS    RESTARTS   AGE
    cert-manager-development-5fb88464fb-xwf8q       1/1     Running   0          9m34s
    ```
    Once the pod is running, get inside the pod:
    ```
    kubectl exec -it cert-manager-development-5fb88464fb-xwf8q -n <your-namespace> -- bash
    ```
    Now you are inside the pod.

8. Now we test if your local working directory is mounted to the pod.
    In your text editor outside the pod (in your local machine - working directory), create a new file and save it as `test.txt`. Check if that file is present in the pod.
    ```
    ls
    ```
    You should see the `test.txt` file.
    This means that your local working directory is mounted to the pod. You can make changes in your working directory and they will be reflected in the pod.
    You are free to develop the code and test the workings.

9. Now, we need to activate teh virtual env once we are inside the container.
    ```
    source $(poetry env info --path)/bin/activate
    ```

10. Install all dependencies with poetry.
    ```
    poetry install
    ```

11. Once done you can run the teardown script.
    ```
    make dev_teardown
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
Once you are done with dev changes. You can make a production setup.
1. Build: `make prod_build`.
2. Setup: `make prod_setup`.
3. Teardown: `make prod_teardown`.


# Create a job from the cronjob to run immediately
Sometimes you need to run a cron job immediately. You can do that by hitting the following command:
```
kubectl create job --from=cronjob/<your-cronjob-name> <job-name> -n <namespace>
```
In our case, it would be:
```
kubectl create job --from=cronjob/cert-manager cert-manager-job -n browseterm-new
```