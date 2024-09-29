# Fraud URL Detection

## Overview
The Fraud URL Detection project aims to classify URLs as either fraud or safe based on specific features extracted from the URLs. The project employs an XGBClassifier model to handle classification tasks.

## Key Features:
- **Modular Approach**: The code is structured in a modular format, where each module handles specific tasks and is invoked as needed.
- **Logging System**: A dedicated logging module tracks each step in the process with detailed messages, including timestamps.
- **Pipeline Structure**: The project follows a pipeline structure, where each step receives configuration and artifacts from the previous step, performs specific actions, and outputs an artifact for the next step.
- **CI/CD Automation**: The pipeline is fully automated using GitHub Actions and AWS, ensuring seamless integration and continuous delivery.

## Training Pipeline
The training pipeline consists of the following steps:

### 1. Data Ingestion:
- Data is ingested from MongoDB and stored as an artifact.
- The dataset, including train and test splits, is stored as artifacts for future reference.

### 2. Data Validation:
- The ingested data is validated against a predefined schema and checked for data drift.
- Validated data is stored as an artifact.

### 3. Data Transformation:
- The validated data undergoes transformations based on requirements identified during EDA (Exploratory Data Analysis).
- Key transformations include:
  - Using KNNImputer to handle missing values.
  - Changing the non-fraud URL label from -1 to 0.
- The KNNImputer object is saved as a preprocessor artifact for use in the prediction pipeline and the transform data is stored as an artifact.

### 4. Model Training:
- The transformed data is used to train an XGBClassifier model.
- Hyperparameters are tuned using RandomSearchCV.
- Key metrics (F1 Score, Precision, Recall) are evaluated for both the training and testing datasets.
- Model Validation:
  - If the test F1 score is below a set threshold, the model is rejected.
  - If the difference between test and train F1 scores exceeds a threshold, the model is also rejected.
- Approved models are stored as artifacts.

### 5. Model Evaluation:
- The current best model is compared to previously saved models using the F1 score.
- If the new model performs better, it is promoted to the best model.
- Metrics for all newly trained models are tracked using MLflow.
- The classification score of both models along with their paths and acceptance status is stored as an artifact for this step.

### 6. Model Pusher:
- The best model is saved in the `saved_model` directory, and its path is logged as an artifact.
- This path is used in the Model Evaluation step to retrieve the best-performing model for evaluation or future predictions.

## Prediction Pipeline
The batch prediction pipeline works as follows:
- A batch of data is provided as input.
- The data is transformed using the preprocessor object saved during the Data Transformation step.
- Predictions are made using the best model trained in the Model Training pipeline.

## S3 Sync (AWS)
### Training Pipeline:
- Artifacts from each step, including the best model, are saved to an S3 bucket in AWS.

### Prediction Pipeline:
- The predicted output is stored in the S3 bucket for future reference.

## API Integration
A FastAPI interface is developed to:
- Trigger the training pipeline.
- Perform batch predictions by uploading files for analysis.

## MLOps Pipeline using GitHub Actions, Docker, and AWS
The CI/CD pipeline automates the workflow as follows:

### Continuous Integration (CI):
- GitHub Actions automatically trigger upon code updates, running tests and ensuring code quality.

### Continuous Delivery (CD):
- A Docker image is created and pushed to the Elastic Container Registry (ECR) in AWS.

### Continuous Deployment (CD):
- The EC2 instance pulls the Docker image from the ECR and deploys the latest version.

### Docker Setup in EC2:
An Ubuntu EC2 instance is used for deployment. The following commands are executed to install Docker:
```bash
sudo apt-get update -y
sudo apt-get upgrade
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```
Once Docker is installed, a GitHub runner is configured on the EC2 instance to handle continuous deployment.

### Continuous Training:
- Airflow is used to manage continuous training inside the Docker container.
- Training is triggered manually when needed. 
<br> 
 
**[Note]** 
#### Environment Variables

To run this project locally or in CI/CD, ensure that the following environment variables are set:

#### Local Setup (.env file)

To run the project locally, create a `.env` file in the root directory and add the following environment variables:

```bash
MONGO_DB_URL = <your-mongodb-connection-url>
AWS_ACCESS_KEY_ID = <your-aws-access-key-id>
AWS_SECRET_ACCESS_KEY = <your-aws-secret-access-key>
AWS_DEFAULT_REGION = <your-aws-default-region>
BUCKET_NAME = <your-s3-bucket-name>
```

#### GitHub Secrets (for CI/CD pipeline)

To set up the CI/CD pipeline using GitHub Actions, configure the following secrets in GitHub repository:

```bash
AWS_ACCESS_KEY_ID = <your-aws-access-key-id>
AWS_ECR_LOGIN_URI = <your-aws-ecr-login-uri>
AWS_REGION = <your-aws-region>
AWS_SECRET_ACCESS_KEY = <your-aws-secret-access-key>
AIRFLOW_PASSWORD = <your-airflow-password>
ECR_REPOSITORY_NAME = <your-ecr-repository-name>
MONGO_DB_URL = <your-mongodb-connection-url>
```

