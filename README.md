# cloud-carbon-footprint-analyzer

Jupyter notebooks for quick analysis and visualization of cloud-carbon-footprint data

## requirements & installation

`Python >= 3.10`

`pip >= 22.0`

install dependencies:

```sh
pip install -r requirements.txt 
```

## GitLab CI integration

This reporting solution can be integrated in a GitLab CI pipeline.

```yml
variables:
  # secrets that have to be set
  AZURE_CLIENT_ID: ""
  AZURE_CLIENT_SECRET: ""
  AZURE_TENANT_ID: ""
  # azure configuration
  AZURE_USE_BILLING_DATA: "true"
  AZURE_AUTH_MODE: "default"
  AZURE_RESOURCE_TAG_NAMES: '["resourceGroup","project","customer"]'
  AZURE_CONSUMPTION_CHUNKS_DAYS:
    value: "14"
    description: "Perform requests to the Azure API in chunks of X days to avoid rate limit errors"
  # settings for run
  START_DATE:
    value: ""
    description: "Estimation range start date, YYYY-MM-DD, default: start of last month"
  END_DATE:
    value: ""
    description: "Estimation range end date, YYYY-MM-DD, default: end of last month"

stages:
  - estimate
  - report

estimate:
  image: node:16
  stage: estimate
  timeout: 24h
  before_script:
    - git clone https://github.com/cloud-carbon-footprint/cloud-carbon-footprint.git
    - cd cloud-carbon-footprint
    - yarn install
  script:
    # if start date is not set, set to beginning of last month
    - START_DATE=${START_DATE:-$(date -d " $(date +\%Y-\%m-01) -1 month" +\%Y-\%m-01)}
    # if end date is not set, set to end of last month
    - END_DATE=${END_DATE:-$(date -d " $(date +\%Y-\%m-01) -1 day" +\%Y-\%m-\%d)}
    - echo estimating for time range from $START_DATE to $END_DATE
    - yarn start-cli --startDate $START_DATE --endDate $END_DATE
  artifacts:
    paths:
      - "cloud-carbon-footprint/packages/cli/estimates.cache.day.json"
    expire_in: 1 hour

report:
  image: python:3.10
  stage: report
  before_script:
    - pip install jupyter
    - git clone https://github.com/NicolasBissig/cloud-carbon-footprint-analyzer.git
    - cd cloud-carbon-footprint-analyzer
    - pip install -r requirements.txt
  script:
    - jupyter nbconvert --to html --no-input --execute report.ipynb
  artifacts:
    paths:
      - "cloud-carbon-footprint-analyzer/report.html"
    expire_in: 1 hour
```
