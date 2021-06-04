TARGET_PATH=
COMPOSER_ENV_NAME=mycomposer
LOCATION=us-central1

upload:
	gcloud composer environments storage dags import --environment ${COMPOSER_ENV_NAME} --location ${LOCATION} --source ${TARGET_PATH}

delete:
	gcloud composer environments storage dags delete --environment ${COMPOSER_ENV_NAME} --location ${LOCATION} ${TARGET_PATH}
