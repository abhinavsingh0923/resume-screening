# AI-Powered Resume Screening Application

A modern web application that uses AI to screen and evaluate resumes against job descriptions, providing instant feedback and candidate rankings.

## 🚀 Features

- **Bulk Resume Processing**: Upload and analyze multiple resumes (up to 10) at once
- **Smart Matching**: AI-powered matching of candidate skills and experience to job requirements
- **Detailed Analysis**: Get comprehensive insights for each candidate
- **Visual Results**: View candidate rankings and score distributions through interactive charts
- **PDF Support**: Upload job descriptions and resumes in PDF format

## 📋 Requirements

- Python 3.10+
- `uv` package manager (recommended)
- Google Gemini API key
- Docker (optional)
- Kubernetes Cluster (for production)

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-screening.git
   cd resume-screening
   ```

2. Set up a virtual environment:
   ```bash
   # Install uv if you haven't (https://docs.astral.sh/uv/)
   pip install uv
   
   # Sync dependencies
   uv sync
   ```

3. Create a `.env` file with your API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Usage

1. Start the application:
   ```bash
   uv run streamlit run app/app.py
   # OR using make
   make run
   ```

2. Open your browser and navigate to `http://localhost:8501`

## 🐳 Docker Usage

1. **Build the image**:
   ```bash
   make docker-build
   # OR
   docker build -t resume-screener .
   ```

2. **Run the container**:
   ```bash
   make docker-run
   # OR
   docker run -p 8501:8501 --env-file .env resume-screener
   ```

## ☸️ Kubernetes Deployment

The application is designed to be deployed on Kubernetes with ArgoCD and monitored using the PLG stack (Prometheus, Loki, Grafana).

### 1. Manual Deployment

```bash
# Apply Namespace
kubectl apply -f k8s/namespace.yaml

# Create Secret (Replace w/ actual key first!)
kubectl apply -f k8s/secret.yaml

# Apply Deployment, Service, HPA, Ingress
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
```

### 2. Monitoring Setup (Helm)

You can install the entire PLG stack (Prometheus, Loki, Grafana) with one command:

```bash
# Make script executable
chmod +x monitoring/install.sh

# Run install script
./monitoring/install.sh
```

Alternatively, you can install components individually:

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/prometheus -n monitoring --create-namespace -f monitoring/prometheus-values.yaml

# Install Loki
helm install loki grafana/loki-stack -n monitoring -f monitoring/loki-values.yaml

# Install Grafana
helm install grafana grafana/grafana -n monitoring -f monitoring/grafana-values.yaml
```

### 📊 Accessing Dashboards

- **Grafana**: http://localhost:80 (via LoadBalancer) or port-forward
- **Prometheus**: Internal access via Grafana
- **User**: `admin`
- **Password**: `admin`

## 🔄 CI/CD Pipeline

The project includes a `Jenkinsfile` for a complete CI/CD pipeline:

1.  **Checkout**: Clones the repo.
2.  **Test**: Runs `pytest` unit tests.
3.  **Security Scans**:
    *   **Trivy**: Scans filesystem and Docker image for vulnerabilities.
    *   **OWASP Dependency Check**: Checks for vulnerable dependencies.
4.  **SonarQube**: Performs static code analysis.
5.  **Build**: Builds the Docker image.
6.  **Push**: Pushes the image to DockerHub.
7.  **Deploy**: Updates the Kubernetes manifest in the repo (GitOps).

### Git Workflow

1.  **Develop**: Create a new branch `git checkout -b feature/new-feature`
2.  **Commit**: `git commit -am "feat: added new feature"`
3.  **Push**: `git push origin feature/new-feature`
4.  **Merge**: Create a Pull Request to `main`.
5.  **CI/CD**: Jenkins automatically picks up the changes on `main`, runs tests, builds, and deploys.

## 🛠️ Development

### Project Structure

- `app/`: Source code directory
  - `app.py`: Streamlit frontend application
  - `workflow.py`: LangGraph workflow definition
  - `chains.py`: LLM chain definitions
- `tests/`: Unit tests
- `k8s/`: Kubernetes manifests (Deployment, Service, Ingress, etc.)
- `monitoring/`: Helm values for Prometheus/Loki
- `Jenkinsfile`: CI/CD definition
- `Dockerfile`: Container configuration

### Running Tests

```bash
uv run pytest tests/ -v
# OR
make test
```