# Deploy to IBM Cloud Code Engine

Research checked against IBM Cloud Code Engine documentation on 2026-09-22.

## Prerequisites

- IBM Cloud CLI
- Code Engine CLI plugin
- an active Code Engine project selected with `ibmcloud ce project select`
- Confluent Cloud credentials in a local `.env`

IBM Code Engine can build and deploy directly from local source using `--build-source .` and a Dockerfile. It can also map a Code Engine secret into application environment variables.

Official references:
- https://cloud.ibm.com/docs/codeengine?topic=codeengine-app-local-source-code
- https://cloud.ibm.com/docs/codeengine?topic=codeengine-secret
- https://cloud.ibm.com/docs/codeengine?topic=codeengine-envvar

## Recommended deployment

```bash
cp .env.example .env
# edit .env

ibmcloud login
ibmcloud target -r <your-region>
ibmcloud ce project select --name <your-project>

./infra/code-engine/deploy.sh
```

The script defaults to:
- app name: `factorypulse-streamhouse`
- CPU: 1
- memory: 2 GB
- min scale: 1
- max scale: 1

Override, for example:

```bash
CE_APP_NAME=my-streamhouse-demo MIN_SCALE=1 MAX_SCALE=1 ./infra/code-engine/deploy.sh
```

`APP_NAME` is reserved for the human-readable title shown by the application; `CE_APP_NAME` is the DNS-safe Code Engine application resource name.

## Why minimum scale 1?

The UI is a live demo and the in-memory retrieval index is replayed from Kafka at startup. Keeping one warm instance avoids a cold-start replay during a presentation.

## Health check

After deployment:

```bash
ibmcloud ce application get --name factorypulse-streamhouse
```

Open the returned URL and check:

```text
/api/health
/docs
```

## Updating

Re-run `deploy.sh`. If the Code Engine application already exists, the script uses `application update` and rebuilds from the local Dockerfile.

## Secret handling

The script stores:
- Kafka bootstrap server,
- Kafka API key/secret,
- optional Schema Registry credentials,
- optional watsonx API key/project ID,

inside a Code Engine secret and maps it to environment variables. Non-secret runtime selectors such as `RAG_PIPELINE_MODE` remain ordinary environment values.
