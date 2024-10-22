pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "divyavundavalli/ecom_project"
        // Use DOCKER_REGISTRY_CREDENTIALS to store Docker Hub credentials
        DOCKER_REGISTRY_CREDENTIALS = credentials('docker')
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: "https://github.com/DivyaJyothiVundavalli/Ecom_Project_space.git"
            }
        }
        
        stage('Docker Login') {
            steps {
                // Login to Docker Hub using credentials
                sh '''
                    docker info
                    echo $DOCKER_REGISTRY_CREDENTIALS_PSW | docker login -u $DOCKER_REGISTRY_CREDENTIALS_USR --password-stdin
                '''
            }
        }
        
        stage('Docker Build & Push') {
            steps {
                script {
                    try {
                        // Build the Docker image
                        sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
                        sh "docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest"
                        
                        // Push both tagged versions to Docker Hub
                        sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    } catch (Exception e) {
                        echo "Error during Docker build/push: ${e.getMessage()}"
                        throw e
                    }
                }
            }
        }
    }
    
    post {
        always {
            sh 'docker logout'
            // Clean up Docker images to free up space
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            sh "docker rmi ${DOCKER_IMAGE}:latest || true"
        }
    }
}
