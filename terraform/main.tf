provider "google-beta" {
  # credentials = file("<PATH_TO_SERVICE_ACCOUNT_KEY.json>") 
  project = "plomber"
  region  = "us-central1"
}

# Create a Bucket named "evm_bucket"
resource "google_storage_bucket" "evm_bucket" {
  project = "plomber"
  name          = "evm_bucket"
  location      = "US"
  storage_class = "STANDARD"
  force_destroy = true  # Allows deletion of bucket with contents

}

# Create a BigQuery dataset named "eth-data"
resource "google_bigquery_dataset" "eth_data" {
  project = "plomber"
  dataset_id = "eth_data"
  location   = "US" # Choose the appropriate location
}

# Create a BigQuery table named "EVM_TRANSACTIONS" within the "eth-data" dataset
resource "google_bigquery_table" "evm_transactions" {
  project = "plomber"
  dataset_id = google_bigquery_dataset.eth_data.dataset_id
  table_id   = "EVM_TRANSACTIONS"

  schema = jsonencode([
    {
      name = "transaction_hash",
      type = "STRING",
      mode = "REQUIRED"
    },
    {
      name = "block_number",
      type = "INTEGER",
      mode = "REQUIRED"
    },
    {
      name = "value",
      type = "FLOAT",
      mode = "NULLABLE"
    },
    # Add additional fields as required
  ])

  # Optionally, i can define time partitioning, clustering, or other features here
}

# This code is compatible with Terraform 4.25.0 and versions that are backwards compatible to 4.25.0.
# For information about validating this Terraform code, see https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build#format-and-validate-the-configuration

# resource "google_compute_instance" "eth-collect" {
#   boot_disk {
#     auto_delete = true
#     device_name = "eth-collect"

#     initialize_params {
#       image = "projects/debian-cloud/global/images/debian-11-bullseye-v20240110"
#       size  = 10
#       type  = "pd-balanced"
#     }

#     mode = "READ_WRITE"
#   }

#   can_ip_forward      = false
#   deletion_protection = false
#   enable_display      = true

#   labels = {
#     goog-ec-src = "vm_add-tf"
#   }

#   machine_type = "e2-medium"
#   name         = "eth-collect"

#   network_interface {
#     access_config {
#       network_tier = "PREMIUM"
#     }

#     queue_count = 0
#     stack_type  = "IPV4_ONLY"
#     subnetwork  = "projects/plomber/regions/us-central1/subnetworks/default"
#   }

#   scheduling {
#     automatic_restart   = true
#     on_host_maintenance = "MIGRATE"
#     preemptible         = false
#     provisioning_model  = "STANDARD"
#   }

#   service_account {
#     email  = "908912453933-compute@developer.gserviceaccount.com"
#     scopes = ["https://www.googleapis.com/auth/cloud-platform"]
#   }

#   shielded_instance_config {
#     enable_integrity_monitoring = true
#     enable_secure_boot          = false
#     enable_vtpm                 = true
#   }

#   tags = ["http-server", "https-server", "lb-health-check"]
#   zone = "us-central1-c"
# }
