import subprocess
import sys
import time
import json
from pathlib import Path

# ==== CONFIG ====
APP_NAME = "flask-bluegreen"
DOCKERHUB_USER = "rijomjohn"
IMAGE_REPO = f"{DOCKERHUB_USER}/{APP_NAME}"
CHART_PATH = "charts/flask-bluegreen"
NAMESPACE = "default"
# ===============

def sh(cmd, check=True):
    print(f"\n$ {cmd}")
    p = subprocess.run(cmd, shell=True, text=True)
    if check and p.returncode != 0:
        sys.exit(p.returncode)

def sh_out(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def get_current_values():
    try:
        out = sh_out(f"helm get values {APP_NAME} -n {NAMESPACE} -o json")
        return json.loads(out)
    except subprocess.CalledProcessError:
        return {}

def main():
    # 1) Build & push image
    version = time.strftime("v%Y%m%d%H%M%S")
    image_tag = f"{IMAGE_REPO}:{version}"
    print(f"Building image: {image_tag}")

    sh(f"docker build -t {image_tag} ./app")
    sh(f"docker push {image_tag}")

    # 2) Initial install if needed (blue active by default)
    current = get_current_values()
    if not current:
        print("No existing release found, installing chart with blue active...")
        sh(
            "helm upgrade --install "
            f"{APP_NAME} {CHART_PATH} "
            f"-n {NAMESPACE} "
            f"--set image.repository={IMAGE_REPO} "
            f"--set image.tagBlue={version} "
            f"--set image.tagGreen={version} "
            f"--set activeColor=blue "
        )

    # 3) Decide target color (switch the *other* color)
    # If active is blue → update green; if active is green → update blue.
    current = get_current_values()
    active = current.get("activeColor", "blue")
    target = "green" if active == "blue" else "blue"
    print(f"Active color: {active}. Target color for new release: {target}")

    # 4) Update target color's image tag with new version, keep replicas > 0
    set_tag_flag = f"--set image.tag{target.capitalize()}={version}"
    sh(
        "helm upgrade --install "
        f"{APP_NAME} {CHART_PATH} -n {NAMESPACE} "
        f"--reuse-values {set_tag_flag}"
    )

    # 5) Wait for target deployment to be ready
    target_deploy = f"{APP_NAME}-{target}"
    sh(f"kubectl rollout status deploy/{target_deploy} -n {NAMESPACE} --timeout=120s")

    # 6) Switch traffic to target color (Service selector)
    sh(
        "helm upgrade --install "
        f"{APP_NAME} {CHART_PATH} -n {NAMESPACE} "
        f"--reuse-values --set activeColor={target}"
    )

    # 7) Scale down the previous color to zero (cleanup)
    if active == "blue":
        sh(
            "helm upgrade --install "
            f"{APP_NAME} {CHART_PATH} -n {NAMESPACE} "
            f"--reuse-values --set replicas.blue=0 --set replicas.green=2"
        )
    else:
        sh(
            "helm upgrade --install "
            f"{APP_NAME} {CHART_PATH} -n {NAMESPACE} "
            f"--reuse-values --set replicas.green=0 --set replicas.blue=2"
        )

    print("\n✅ Deployment complete.")
    print(f"Version {version} is now live on {target.upper()}.")

    # Optional: show service URL via minikube
    print("\nTip: to open the service in your browser:")
    print(f"minikube service {APP_NAME} -n {NAMESPACE}")

if __name__ == "__main__":
    main()

