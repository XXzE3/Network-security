Fraud URL Detection

The project focuses on noting some features in the URL and classifying it as fraud or safe.

A XGBClassifier model is used for classifying the URLs.

Training Pipeline

The pipeline follows the following steps:
Data Ingestion - The data is ingested into the pipeline from MongoDB and stored as an artifact. The whole dataset along with train and test samples are stored as artifacts from this pipeline.
Data validation - The ingested data is then validated by cross checking with the Schema and checked for any data drift. The validated data is then stored as an artifact from this pipeline step.
Data Transformation - The validated data is then transformed according to requirements observed in EDA and stored as an artifact for the model to take as an input.
The transformations done in this project includes replacing null values with the help of KNNImputer and assigning the non fraud URLs a value of 0 instead of -1. The KNNImputer is also stored as a preprocessor object in the artifact, later to be utilised in the prediction pipeline.
Model Trainer - The transformed data is then passed to the XGBClassifier model. The model is trained using the train sample and validated using the test sample. 
Hyperparameter of the model are tuned using the RandomSearchCV technique.
Metrics like F1 score, Precision, Recall are evaluated for both the train and test sample
If the test sample f1 score is lower than a threshold then the model is rejected.
To prevent underfitting and overfitting, if the difference between test f1 score and train f1 score is higher than a threshold, then the model is rejected.
The approved model is stored as an artifact for this step.
Model Evaluation - The available best model is compared with the currently saved model on the basis of f1 score. This step is used to check if a change in the model has led to a better performance or which version of the model performs the best with the current data.
The classification score of both the models along with their paths and acceptance status is stored as an artifact for this step.
The MLflow module is utilised to track the classification score of each trained model for this step.
Model Pusher - The 

