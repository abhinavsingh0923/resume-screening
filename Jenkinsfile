pipeline {
    agent any

    environment {
        // Define environment variables
        DOCKER_IMAGE = "username/resume-screening" // Replace with your DockerHub
        DOCKER_TAG = "latest" // Default tag, will be overwritten by git tag or commit hash in real use
        K8S_NAMESPACE = "resume-screener-ns"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // Set image tag based on git commit short hash
                    DOCKER_TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                }
            }
        }

        stage('Test') {
            steps {
                echo 'Running Tests...'
                // Install dev dependencies and run tests
                sh 'pip install uv'
                sh 'uv sync'
                sh 'uv run pytest tests/ -v'
            }
        }

        stage('Security Scans') {
            parallel {
                stage('Trivy File Scan') {
                   steps {
                       echo 'Running Trivy FS Scan...'
                       // Ensure Trivy is installed on the agent
                       sh 'trivy fs --exit-code 0 --no-progress .'
                   }
                }
                stage('OWASP Dependency Check') {
                    steps {
                        echo 'Running OWASP Dependency Check...'
                        // Assumes dependency-check-cli is available
                        // Using a simple placeholder for demonstration if tool not in path
                        // sh 'dependency-check.sh --project "Resume Screener" --scan .'
                        echo "Dependency Scan skipped (tool setup required)"
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube Analysis...'
                // Requires SonarQube plugin and server configuration in Jenkins
                withSonarQubeEnv('SonarQube Server') { // Replace 'SonarQube Server' with your configured server name
                   // sh 'uv run sonar-scanner' // Assumes sonar-scanner is available
                   echo "SonarQube analysis mock"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker Image...'
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Trivy Image Scan') {
            steps {
                echo 'Scanning Docker Image...'
                sh "trivy image --exit-code 0 ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    echo 'Pushing Docker Image...'
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials-id') { // Replace credential ID
                        dockerImage.push()
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Update K8s Manifests') {
            steps {
                script {
                    echo 'Updating K8s Manifests...'
                    // Check if ArgoCD Image Updater is handling this. 
                    // If manual update is needed:
                    sh "sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|' k8s/deployment.yaml"
                }
            }
        }
        
        stage('Git Commit & Push Manifest') {
            steps {
                script {
                   echo 'Committing updated manifest...'
                   withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                       sh """
                           git config user.email "jenkins@example.com"
                           git config user.name "Jenkins CI"
                           git add k8s/deployment.yaml
                           git commit -m "Update image tag to ${DOCKER_TAG} [skip ci]" || echo "No changes to commit"
                           git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/yourusername/resume-screening.git HEAD:main
                       """
                   }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
