terraform {
  required_version = ">= 1.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

resource "google_project_service" "cloudfunctions" {
  service = "cloudfunctions.googleapis.com"
}

resource "google_project_service" "run" {
  service = "run.googleapis.com"
}

resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"
}

resource "google_project_service" "logging" {
  service = "logging.googleapis.com"
}

resource "google_project_service" "pubsub" {
  service = "pubsub.googleapis.com"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "monitoring.googleapis.com",
    "firestore.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
    "appengine.googleapis.com"  # Required for Cloud Scheduler
  ])
  
  service            = each.value
  disable_on_destroy = false
}

# Service Account for Cloud Functions
resource "google_service_account" "cloud_functions_sa" {
  account_id   = "network-monitor-functions"
  display_name = "Network Monitor Functions"
  description  = "Service account for network monitoring Cloud Functions"
}

# IAM roles for the service account
resource "google_project_iam_member" "function_permissions" {
  for_each = toset([
    "roles/compute.viewer",
    "roles/monitoring.viewer", 
    "roles/datastore.user",
    "roles/logging.logWriter"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}

# Cloud Storage bucket for function source code
resource "google_storage_bucket" "function_source" {
  name                        = "${var.project_id}-network-monitor-functions"
  location                    = var.region
  force_destroy              = true
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
}

# Firestore database (Native mode)
resource "google_firestore_database" "network_monitor_db" {
  project                     = var.project_id
  name                       = "(default)"
  location_id                = var.region
  type                       = "FIRESTORE_NATIVE"
  concurrency_mode           = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Scheduler Jobs
resource "google_cloud_scheduler_job" "network_data_collection" {
  name             = "network-data-collection"
  description      = "Collect network resource data every 15 minutes"
  schedule         = "*/15 * * * *"  # Every 15 minutes
  time_zone        = "UTC"
  attempt_deadline = "600s"
  
  retry_config {
    retry_count = 3
  }
  
  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.network_data_collector.service_config[0].uri
    
    oidc_token {
      service_account_email = google_service_account.cloud_functions_sa.email
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_cloudfunctions2_function.network_data_collector
  ]
}

resource "google_cloud_scheduler_job" "network_metrics_collection" {
  name             = "network-metrics-collection"
  description      = "Collect network metrics every 5 minutes"
  schedule         = "*/5 * * * *"   # Every 5 minutes
  time_zone        = "UTC"
  attempt_deadline = "600s"
  
  retry_config {
    retry_count = 3
  }
  
  http_target {
    http_method = "POST"
    uri         = "${google_cloudfunctions2_function.network_metrics_collector.service_config[0].uri}?duration=10"
    
    oidc_token {
      service_account_email = google_service_account.cloud_functions_sa.email
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_cloudfunctions2_function.network_metrics_collector
  ]
}

# Cloud Function for Network Data Collection
resource "google_cloudfunctions2_function" "network_data_collector" {
  name        = "network-data-collector"
  location    = var.region
  description = "Collect GCP network resource data"
  
  build_config {
    runtime     = "python311"
    entry_point = "network_data_collector"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source_zip.name
      }
    }
  }
  
  service_config {
    max_instance_count    = 10
    min_instance_count    = 0
    available_memory      = "512M"
    timeout_seconds       = 540
    service_account_email = google_service_account.cloud_functions_sa.email
    
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_storage_bucket_object.function_source_zip
  ]
}

# Cloud Function for Network Metrics Collection
resource "google_cloudfunctions2_function" "network_metrics_collector" {
  name        = "network-metrics-collector"
  location    = var.region
  description = "Collect GCP network performance metrics"
  
  build_config {
    runtime     = "python311"
    entry_point = "network_metrics_collector"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source_zip.name
      }
    }
  }
  
  service_config {
    max_instance_count    = 5
    min_instance_count    = 0
    available_memory      = "1G"
    timeout_seconds       = 540
    service_account_email = google_service_account.cloud_functions_sa.email
    
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_storage_bucket_object.function_source_zip
  ]
}

# Upload function source code
data "archive_file" "function_source" {
  type        = "zip"
  output_path = "function-source.zip"
  source_dir  = "../backend/cloud_functions"
}

resource "google_storage_bucket_object" "function_source_zip" {
  name   = "function-source-${data.archive_file.function_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.function_source.output_path
}

# IAM for Cloud Functions (allow unauthenticated access for testing)
resource "google_cloudfunctions2_function_iam_member" "data_collector_invoker" {
  project        = google_cloudfunctions2_function.network_data_collector.project
  location       = google_cloudfunctions2_function.network_data_collector.location
  cloud_function = google_cloudfunctions2_function.network_data_collector.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

resource "google_cloudfunctions2_function_iam_member" "metrics_collector_invoker" {
  project        = google_cloudfunctions2_function.network_metrics_collector.project
  location       = google_cloudfunctions2_function.network_metrics_collector.location
  cloud_function = google_cloudfunctions2_function.network_metrics_collector.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

# Outputs
output "network_data_collector_url" {
  description = "URL of the network data collector function"
  value       = google_cloudfunctions2_function.network_data_collector.service_config[0].uri
}

output "network_metrics_collector_url" {
  description = "URL of the network metrics collector function" 
  value       = google_cloudfunctions2_function.network_metrics_collector.service_config[0].uri
}

output "firestore_database" {
  description = "Firestore database name"
  value       = google_firestore_database.network_monitor_db.name
}

output "service_account_email" {
  description = "Service account email for Cloud Functions"
  value       = google_service_account.cloud_functions_sa.email
}

output "scheduler_jobs" {
  description = "Cloud Scheduler job names"
  value = {
    data_collection    = google_cloud_scheduler_job.network_data_collection.name
    metrics_collection = google_cloud_scheduler_job.network_metrics_collection.name
  }
}