provider "google-beta" {
  project = "halogen-segment-241921"
  region  = "us-central1"
}

data "google_compute_default_service_account" "default" {
  project = "halogen-segment-241921"
}
# Don't forget to enable Service Usage API manualy

# Enable Storage API
resource "google_project_service" "storage_api" {
  project            = "halogen-segment-241921"
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

# Enable BigQuery API
resource "google_project_service" "bigquery_api" {
  project            = "halogen-segment-241921"
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

# enable composer_api
resource "google_project_service" "composer_api" {
  provider = google-beta
  project = "halogen-segment-241921"
  service = "composer.googleapis.com"
  // Disabling Cloud Composer API might irreversibly break all other
  // environments in your project.
  disable_on_destroy = false
}


# Create a Bucket named "evm_data"
resource "google_storage_bucket" "evm_data" {
  project = "halogen-segment-241921"
  name          = "evm_data"
  location      = "US"
  storage_class = "STANDARD"
  force_destroy = true  # Allows deletion of bucket with contents
  depends_on = [google_project_service.bigquery_api]

}

# Create a BigQuery dataset named "eth-data"
resource "google_bigquery_dataset" "eth_data" {
  project = "halogen-segment-241921"
  dataset_id = "eth_data"
  location   = "US" # Choose the appropriate location
  depends_on = [google_project_service.storage_api]
}

# Create a BigQuery table named "EVM_TRANSACTIONS" within the "eth-data" dataset

# This code is compatible with Terraform 4.25.0 and versions that are backwards compatible to 4.25.0.
# For information about validating this Terraform code, see https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build#format-and-validate-the-configuration

resource "google_compute_instance" "eth-collect" {
  project = "halogen-segment-241921"
  boot_disk {
    auto_delete = true
    device_name = "eth-collect"

    initialize_params {
      image = "projects/debian-cloud/global/images/debian-11-bullseye-v20240110"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = true

  labels = {
    goog-ec-src = "vm_add-tf"
  }

  machine_type = "e2-medium"
  name         = "eth-collect"

  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }

    queue_count = 0
    stack_type  = "IPV4_ONLY"
    subnetwork  = "projects/halogen-segment-241921/regions/us-central1/subnetworks/default"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = data.google_compute_default_service_account.default.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  tags = ["http-server", "https-server", "lb-health-check"]
  zone = "us-central1-c"

  metadata = {
  "enable-oslogin" = "TRUE"
  }

  # depends_on = [google_os_login_ssh_public_key.default]

  # provisioner "remote-exec" {
  # inline = [
  #   "sudo mkdir -p /home/alaingcp2023_gmail_com/python",
  #   "sudo mkdir -p /home/alaingcp2023_gmail_com/utils",
  # ]
  # }

  # connection {
  # type        = "ssh"
  # user        = "alaingcp2023_gmail_com"
  # private_key = file("C:/Users/AHEBIE/Documents/GHUB/ethereum-airflow/utils/my_ssh_keys/eth-ssh-key")
  # host        = self.network_interface[0].access_config[0].nat_ip
  # }


}


data "google_client_openid_userinfo" "me" {
}

resource "google_os_login_ssh_public_key" "default" {
  project = "halogen-segment-241921"
  user = data.google_client_openid_userinfo.me.email
  key = file("C:/Users/AHEBIE/Documents/GHUB/ethereum-airflow/utils/my_ssh_keys/eth-ssh-key.pub")
  # Path to your public key
}

output "authenticated_user_email" {
  value = data.google_client_openid_userinfo.me.email
}

output "default_gcompute_email" {
  value = data.google_compute_default_service_account.default.email
}