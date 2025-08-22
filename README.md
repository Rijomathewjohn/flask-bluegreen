Flask Blue-Green Deployment on Minikube with Helm
=================================================

This project demonstrates a **Blue-Green deployment strategy** for a Flask web application using:

-   **Python** (Flask app)

-   **Docker** (containerization)

-   **DockerHub** (image registry)

-   **Helm** (deployment manager)

-   **Minikube + kubectl** (local Kubernetes cluster)

When you run the automation script, it:

1.  Pulls the latest code

2.  Builds and pushes a Docker image to DockerHub

3.  Deploys the new version as the **inactive color** (Blue or Green)

4.  Waits for health checks to pass

5.  Switches the Service to the new version

6.  Scales down the old version

* * * * *

🛠️ Prerequisites
-----------------

Make sure the following are installed on your system:

-   Python **3.9+**

-   Git

-   Docker (and logged in with `docker login`)

-   Minikube (with Docker driver)

-   kubectl

-   Helm v3

-   A DockerHub account

* * * * *

⚡ Setup
-------

### 1\. Install dependencies

# Ubuntu example
sudo apt-get update
sudo apt-get install -y git python3 python3-pip docker.io

# Add user to docker group (re-login required)
sudo usermod -aG docker $USER

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash`

### 2\. Start Minikube

`minikube start --driver=docker
kubectl config use-context minikube`

### 3\. DockerHub login

`docker login`

* * * * *

▶️ Run the Project
------------------

### 1\. Clone repository

`git clone https://github.com/YOUR-USERNAME/flask-bluegreen.git
cd flask-bluegreen`

### 2\. Configure DockerHub username

Edit **`scripts/deploy.py`** and update:

`DOCKERHUB_USER = "your-dockerhub-username"`

### 3\. Deploy application

`python3 scripts/deploy.py`

This will:

-   Build & push Docker image (`your-dockerhub-username/flask-bluegreen:vTIMESTAMP`)

-   Deploy to Minikube with Helm

-   Perform Blue→Green switch if needed

### 4\. Access the app

`minikube service flask-bluegreen`

Then open the displayed URL in your browser.\
You'll see output like:

`Hello from Flask! Active color: green, version: v20250822180000`

Refreshing after a redeploy will switch between Blue and Green.
