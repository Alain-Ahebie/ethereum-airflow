# ethereum-airflow

#                                          ELT ARCHITECTURE

![Alt text](utils/img/ETH-ETL_v1.1.png)





ssh-keygen -t rsa -f ~/.ssh/my-ssh-key -C alaingcp2023 -b 2048

esource "google_compute_instance" "default" {
  // ... (your existing configuration for the instance) ...

  provisioner "remote-exec" {
    inline = [
      "mkdir -p /path/to/your/directory"
    ]
  }

  connection {
    type        = "ssh"
    user        = "your-username"
    private_key = file("~/.ssh/id_rsa")
    host        = self.network_interface[0].access_config[0].nat_ip
  }
}

data "google_client_openid_userinfo" "me" {
}

resource "google_os_login_ssh_public_key" "default" {
  user = data.google_client_openid_userinfo.me.email
  key  = file("id_rsa.pub") 
}