# Deploy the Application to Code Engine

## Manual method if your application code resides in a Github Enterprise repository

1. Log into [IBM Cloud](cloud.ibm.com)

2. Create an IBM Cloud API Key.  See [Creating and IBM Cloud API Key](https://www.ibm.com/docs/en/app-connect/container?topic=servers-creating-cloud-api-key)

3. Create an image container registry namespace

    Open the IBM Cloud Shell from the IBM Cloud Console (4th icon from the top right, looks like a console window).
    
    Run the command:
    ```
    ibmcloud cr namespace-add <cr namespace>
    ```
    
4. Navigate to **Code Engine**

    Follow this link to get to Code Engine: https://cloud.ibm.com/codeengine/projects

    Create a new project, click the blue **Create** button

5. Create secrets within the project

    Take the **Secrets and configmaps** link, 
    
    **Registry secret**
    - Select **Create**
    - Select **Registry secret**, then **Next**
    - Enter a secret name, like `build-secret`
    - For **Target registry** choose `Other`
    - For **Registry server** enter `us.icr.io`
    - For **Password** enter your IBM Cloud API Key 
    - Select **Create**

   **SSH secret**
    - Select **Create**
    - Select **SSH secret**, then **Next**
    - Enter a secret name, like `my-ssh`
    - Enter the contents of your SSH **private** key, generated on your local machine using the `ssh keygen -t rsa` command. Note you have to have created an SSH key on your [github.ibm.com](github.ibm.com) (or other GHE respositiory) user (go into **Settings** -> **SSH and GPG Keys** on your github user profile. Add a new SSH key with your `id_rsa.pub` contents)
    - Select **Create**

6. Create an image build
    
    From the Code Engine Project window, select **Image builds**, then go into the **Image build** tab, click build **Create** button
    
    Under the **Source** tab:
    - Name your build (something like `sequifi-app`
    - For **Code repo URL** use the SSH repo format i.e. `git@github.ibm.com:<org>/Sequifi-LLM-Service.git`
    - Choose the SSH secret you creatd in step 4 above
    - Choose the branch name, i.e. `main`
    - Choose the subdirectory where the `Dockerfile` resides if not in top level repo directory
    - Select **Next**

    Under the **Strategy** tab:
    - Choose name of Dockerfile
    - Choose timeout value (we used 15m)
    - Choose Build resources (we used XL)
    - Select **Next**

    Under **Output** tab
    - Enter `us.icr.io` for the **Registry server**
    - Set **Registry secret** to the **Registry secret** created in step 5 above
    - Set **Namespace** to the container registry namespace you created in step 3 above
    - Select **Done**

    Once the **Configuration** is set up, in the **Build runs** pane select **Create**, then **Submit build**

7. Create an Application

    Navigate to the **Applications** tab within **Code Engine** on the left side and click **Create**.

    - Provide a name for the Application, i.e. `sequifi-app`
    - Choose **Use an existing container image**, and enter the image name created in previous step for **Image reference**, i.e. `us.icr.io/<cr_namespace>/sequifi-app:latest`
    - Change the Ephemeral storage to 2.04
    - Limit the instance scaling to 1 and 1
    - Select **Domain mappings** to **Public**.
    - Under the **Optional settings**, **Environment variables**, create the variables with the credentials based on the `env` file
    - Under **Optional settings**, **Image start options** change the **Listening port** to 4050
    - Finally click **Create**

## If code resides in public github

Leave out the steps to create the SSH key secret.

Use the normal repository syntax, i.e. `https://github.com/<org>>/<repo>`

## Accessing the URL on Code Engine

Wait for the build to complete. To access the URL go into the **Applications** page within the Code Engine Project, and click the **OpenURL** link next to the newly deployed `sequifi-app` application

A quick sanity check with `<url>/docs` will take you to the swagger ui. To try the APIs from swagger, you will need to click the **Authorize** button at the topand add the value you set for RAG-APP-API-KEY in the environment variables
