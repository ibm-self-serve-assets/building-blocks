# Text To SQL Fast API Tools

<!-- ABOUT THE PROJECT -->

The Text To SQL Fast API Tools provide API interfaces to the watsonx.data services that can be used by a chat application or called by Tools built in watsonx Orchestrate. 

This README will guide you through the steps to deploy the project locally, on OpenShift or IBM Code Engine. Additionally, you will learn how to access the Swagger documentation once the project is deployed.

## Deploying the application

## Deploying locally

To run application on your local machine, follow these steps:

1. Navigate to the project directory:

    ```bash
    cd text_to_sql_tools/
    ```

2. Create a Python Enviroment, Activate it, and Install Requirements:

    ```bash
    python -m venv assetEnv
    source assetEnv/bin/activate
    pip install -r requirements.txt
    python prereqs.py
    ```

 3. Update your secrets:

    Copy `env` to `.env` and fill in the variables with your url, passwords, and apikeys.

    See the `env` file for more details on how to find the required values.


    | Name                   | Value                                                                                                 |
    | -----------------------| ----------------------------------------------------------------------------------------------------- |
    | APP_API_KEY            | Password used in the API header                                                                       |
    | ---------------------- | ----------------------------------------------------------------------------------------------------- |
    | TEXT_TO_SQL_ENDPOINT   | IBM Cloud API Key                                                                                     |
    | ---------------------- | ----------------------------------------------------------------------------------------------------- |
    | WXD_PROJECT_ID         | watsonx.ai URL                                                                                        |
    | ---------------------- | ----------------------------------------------------------------------------------------------------- |
   
4. Start the project:

    ```bash
    python app.py
    ```

5. URL access:

    The url, for purposes of using cURL is http://0.0.0.0:4050.

    To access Swagger go to http://0.0.0.0:4050/docs


### Deploying onto OpenShift

You can deploy this application onto a provisioned [Red Hat OpenShift](https://cloud.ibm.com/docs/openshift?topic=openshift-getting-started) cluster. See the steps [here.](./openshift-setup/README.md)


## Using the application APIs

After deploying the application, you can now test the API

### Test from Swagger

Open Swagger by going to `<url>/docs`.