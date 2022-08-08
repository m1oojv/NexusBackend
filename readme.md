# Nexus Broker Backend

---

## Preface

This document is a guide to help you start developing the Nexus Broker application's backend.
The backend is structured using the [serverless framework](https://www.serverless.com/framework/docs) and is hosted on 
AWS. This repository contains the code that are used to (mainly) generate AWS lambda functions which function as the 
intermediary between the frontend and the backend infrastructure (databases, AWS cognito, etc.).

A http endpoint is used to allow the frontend to interact with the backend lambda functions, while python's boto3 
library is used to enable the lambda functions to interact with AWS services.

To facilitate clean code, python's [PEP8](https://peps.python.org/pep-0008/) coding standards is encouraged to be 
followed when contributing to this repository as much as possible.

## Quick Start

### Prerequisites

* [Node.js](https://nodejs.org/en/download/)
* [Serverless Framework](https://www.serverless.com/framework/docs/getting-started)
* [Python](https://www.python.org/downloads/)
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [Docker](https://www.docker.com/products/docker-desktop/)
* [PostgreSQL](https://www.postgresql.org/download/windows/)

---
## (Old)
### Running the code

1. Fork this repository and git clone the forked copy to your local machine.
2. Run `cd NexusBrokerBackend`
3. Run `npm install`
4. Open `config.yml` in your text editor.
5. Change the `STAGE_NAME` and `STATE_MACHINE_NAME` variable to something unique to you.
6. Open `src/config/config.ini`, ensure that the endpoint points to the correct (staging vs production) database.
**NOTE: Ensure you don't do your development work using the production database!**
7. Set AWS environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
8. Run `serverless deploy`
---
## (New)
### Running the code
1. Git clone `NexusBrokerBack` to your local machine.
2. Run `cd NexusBrokerBackend`
3. Git checkout to ... `git checkout <branch_name>`
4. Run `npm install`
5. Run `pip install -r requirements.txt`
6. Go to commands.txt and copy the content and paste it in the command prompt / windows powershell
7. Create database `python db/database.py`
8. Upgrade migration `alembic upgrade head`
9. Seed data `python -m db.seed`
10. Run `serverless offline start --functionCleanupIdleTimeSeconds 1 --stage development`

> NOTE: Request for csv files

---
## Services

Services will be resolved into individual AWS lambda functions and will each serve a single purpose. The frontend of 
the application will call these lambda functions (and thus these services) when retrieving/updating data from the 
backend. Services are stored under the `src/services` folder. These services are categorised into a few groups and 
details of each group and their services are documented below.

### Threats
*Insert description here*

#### Update threat scenario
*Insert description here*
* Source: `src/services/threats.py`
* API path: `/updatethreatscenario`
* API method: `POST`
* Input: ...
* Output: ...

#### Supply chain threat scenario details
*Insert description here*
* Source: `src/services/threats.py`
* API path: `/supplychainthreatscenariodetails`
* API method: `POST`
* Input: ...
* Output: ...

#### Vendor threat scenario
*Insert description here*
* Source: `src/services/threats.py`
* API path: `/vendorthreatscenario`
* API method: `POST`
* Input: ...
* Output: ...

### Controls
*Insert description here*

#### Company control families
*Insert description here*
* Source: `src/services/controls.py`
* API path: `/vendorcontrolfamilies`
* API method: `POST`
* Input: 
* Output: 

####  Company control family details
*Insert description here*
* Source: `src/services/controls.py`
* API path: `/vendorcontrolfamilydetails`
* API method: `POST`
* Input: 
* Output: 

#### Company control details
*Insert description here*
* Source: `src/services/controls.py`
* API path: `/vendorcontroldetails`
* API method: `POST`
* Input: 
* Output: 

### Controls assessment
*Insert description here*

#### Control assessment
*Insert description here*
* Source: `src/services/controlsassessment.py`
* API path: `/controlassessment`
* API method: `POST`
* Input: 
* Output: 

#### Control assessment family
*Insert description here*
* Source: `src/services/controlsassessment.py`
* API path: `/controlassessmentfamily`
* API method: `POST`
* Input: 
* Output: 

#### Update control score
*Insert description here*
* Source: `src/services/controlsassessment.py`
* API path: `/updatecontrolscore`
* API method: `POST`
* Input: 
* Output: 

### Insurance APIs
*Insert description here*

#### Company details
*Insert description here*
* Source: `src/services/insurance.py`
* API path: `/companydetails`
* API method: `POST`
* Input:
  * UUID of company whose details are to be retrieved.
* Output: 
  * Details of the company.
```
[
  {
    "id": "string", 
    "companyName": "string", 
    "revenue": float, 
    "industry": "string", 
    "country": "string", 
    "description": "string", 
    "assessmentProgress": "NOT STARTED"|"IN PROGRESS"|"COMPLETED"
    "lastAssessed": "string", 
    "employees": int, 
    "domain": "string", 
    "threatAssessment": "NOT STARTED"|"IN PROGRESS"|"COMPLETED", 
    "exposureAssessment": "NOT STARTED"|"IN PROGRESS"|"COMPLETED",
    "controlsAssessment": "NOT STARTED"|"IN PROGRESS"|"COMPLETED", 
    "scanResults": {JSON OBJECT}, 
    "pii": int, 
    "pci": int, 
    "phi": int, 
    "financials": {JSON OBJECT}, 
    "assessment": [JSON LIST]
  }   
]
```

#### Insured Companies
*Insert description here*
* Source: `src/services/insurance.py`
* API path: `/insuredcompanies`
* API method: `GET`
* Input: 
* Output: 

#### Insurance dashboard
*Insert description here*
* Source: `src/services/insurance.py`
* API path: `/insurancedashboard`
* API method: `GET`
* Input: 
* Output: 

#### Calculate company scores
*Insert description here*
* Source: `src/services/insurance.py`
* API path: `None`
* API method: `None`
* Input: 
* Output: 

#### Add new company
Called when a new client (company) is added into the broker application. Purpose is to create a new company entry in 
the database and will trigger the client report calculation and generation process.
Will push relevant company details to the `jobsWorker` lambda function queue once it finishes running.
* Source: `src/services/insurance.py`
* API path: `/addnewcompany`
* API method: `POST`
* Input: Details obtained from the form the user fills up when creating a new client.
```
{
  "companyName": "string", 
  "domain": "string", 
  "countries": "string", 
  "industry": "string", 
  "employees": int, 
  "revenue": int, 
  "records": int
  "
}
```
* Output: UUID assigned to the company.
```
{
  "uuid": "string"
}
```

#### Delete company
*Insert description here*
* Source: `src/services/insurance.py`
* API path: `/deletecompany`
* API method: `DELETE`
* Input: 
* Output: 

### Model
*Insert description here*

#### Retrieve model parameters class
*Insert description here*
* Source: `src/services/model.py`
* API path: `None`
* API method: `None`
* Input: 
* Output: 

#### Write model results
*Insert description here*
* Source: `src/services/model.py`
* API path: `None`
* API method: `None`
* Input: 
* Output: 

### User data
Functions that are related to managing a user of the broker application.

#### User data
*Insert description here*
* Source: `src/services/userdata.py`
* API path: `None`
* API method: `None`
* Input: 
* Output: 

#### User profile
*Insert description here*
* Source: `src/services/userdata.py`
* API path: `/userprofile`
* API method: `GET`
* Input: 
* Output: 

#### Create new user
*Insert description here*
* Source: `src/services/userdata.py`
* API path: `/createnewuser`
* API method: `POST`
* Input: 
* Output: 

### PDF generator
Used to generate a PDF version of a risk assessment for a company.

#### Generate PDF
Endpoint to call to generate the PDF risk assessment report for a company.
* Source: `src/services/reportlab-2.py`
* API path: `/generatepdf`
* API method: `POST`
* Input: 
  * UUID of company whose risk report is to be generated.
* Output: 
  * Link to download the generated report.

### Others

#### Jobs Worker
Assigns an assessment ID to the risk assessment job and creates blank control assessments rows in the database.
Domain of the company is then assessed for its risk posture
* Source: `src/services/insurance.py`
* API path: `None`
* API method: `None`
* Input:
  * Details of a company gotten from `addnewcompany`.
```
{
  "uuid": "string", 
  "companyName": "string", 
  "domain": "string", 
  "estimatedControls": "Yes"
}
```
* Output: `None`
