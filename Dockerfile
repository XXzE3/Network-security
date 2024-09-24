FROM python:3.10-slim-buster
USER root
RUN mkdir /app
COPY . /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt
ARG AIRFLOW_PASSWORD
ENV AIRFLOW_PASSWORD=${AIRFLOW_PASSWORD}
ENV AWS_DEFAULT_REGION = "eu-north-1"
ENV BUCKET_NAME="networksecuritypritam"
ENV PREDICTION_BUCKET_NAME="networksecuritypredictions"
ENV AIRFLOW_HOME="/app/airflow"
ENV AIRFLOW_CORE_DAGBAG_IMPORT_TIMEOUT=1000
ENV AIRFLOW_CORE_ENABLE_XCOM_PICKLING=True
RUN airflow db init
RUN airflow users create -e reachpritamchakraborty@gmail.com -f pritam -l chakraborty -p ${AIRFLOW_PASSWORD} -r Admin -u pritam
RUN chmod 777 start.sh
RUN apt update -y
ENTRYPOINT [ "/bin/sh" ]
CMD ["start.sh"]