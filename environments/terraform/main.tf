terraform {
  backend "local" {
    path = "state/terraform.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }

  required_version = ">= 0.14.9"
}

provider "google" {
  project = "gcp-test-149405"
  region  = "us-central1"
  zone    = "us-central1-a"
}

resource "google_composer_environment" "test" {
  name   = "mycomposer"
  region = "us-central1"
  config {
    node_count = 3

    node_config {
      zone         = "us-central1-a"
      machine_type = "n1-standard-1"

      network    = google_compute_network.test.id
      subnetwork = google_compute_subnetwork.test.id

      disk_size_gb = 20

      service_account = google_service_account.test.name
    }

    software_config {
      airflow_config_overrides = {
        core-load_example = "True"
      }

      pypi_packages = {
        numpy = ""
        scipy = ""
      }

      env_variables = {
        FOO = "bar"
      }

      image_version  = "composer-1.16.5-airflow-1.10.15"
      python_version = 3
    }

    # database_config {
    #   machine_type = "db-n1-standard-2"
    # }
  }
}

resource "google_compute_network" "test" {
  name                    = "composer-test-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "test" {
  name          = "composer-test-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region        = "us-central1"
  network       = google_compute_network.test.id
}

resource "google_service_account" "test" {
  account_id   = "composer-env-account"
  display_name = "Test Service Account for Composer Environment"
}

resource "google_project_iam_member" "composer-worker" {
  role   = "roles/composer.worker"
  member = "serviceAccount:${google_service_account.test.email}"
}

resource "google_project_iam_member" "storage-admin" {
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.test.email}"
}

resource "google_project_iam_member" "bigquery-admin" {
  role   = "roles/bigquery.admin"
  member = "serviceAccount:${google_service_account.test.email}"
}

resource "google_project_iam_member" "cloudsql-client" {
  role   = "roles/cloudsql.admin"
  member = "serviceAccount:${google_service_account.test.email}"
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"
  default_table_expiration_ms = 3600000

  labels = {
    env = "default"
  }

  access {
    role          = "OWNER"
    user_by_email = google_service_account.bqowner.email
  }

}

resource "google_service_account" "bqowner" {
  account_id = "bqowner"
}

resource "google_storage_bucket" "composer-test" {
  name          = "composer-test-hoge"
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true
}

# resource "google_bigquery_table" "user" {
#   dataset_id = google_bigquery_dataset.default.dataset_id
#   table_id   = "user"
# 
#   time_partitioning {
#     type = "DAY"
#   }
# 
#   labels = {
#     env = "default"
#   }
# 
#   schema = <<EOF
# [
#   {
#     "name": "id",
#     "type": "STRING",
#     "mode": "REQUIRED",
#     "description": "The id"
#   },
#   {
#     "name": "name",
#     "type": "STRING",
#     "mode": "REQUIRED",
#     "description": "The name of the user."
#   }
# ]
# EOF
# 
# }
# 

resource "google_sql_database" "database" {
  name     = "user-db"
  instance = google_sql_database_instance.instance.name
}

resource "google_sql_database_instance" "instance" {
  name             = "user-db"
  region           = "us-central1"
  database_version = "POSTGRES_9_6"
  settings {
    tier              = "db-f1-micro"
    availability_type = "ZONAL"
    ip_configuration {
      ipv4_enabled = true
    }
  }

  deletion_protection = "true"
}