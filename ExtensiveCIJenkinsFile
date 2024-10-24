pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "divyavundavalli/ecom_projectExCI"
        DOCKER_REGISTRY_CREDENTIALS = credentials('docker')
        // For Python virtual environment
        VENV_NAME = "venv"
        PYTHON_VERSION = "python3"
    }
    
    // options {
    //     // Keep the 10 most recent builds
    //     buildDiscarder(logRotator(numToKeepStr: '10'))
    //     // Timeout if build takes more than 1 hour
    //     timeout(time: 1, unit: 'HOURS')
    //     // Add timestamps to console output
    //     timestamps()
    // }
    
    stages {
        stage('Checkout') {
            steps {
                // Clean workspace before build
                cleanWs()
                git branch: 'main',
                    url: "https://github.com/DivyaJyothiVundavalli/Ecom_Project_space.git"
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    // Create and activate virtual environment
                    sh """
                        ${PYTHON_VERSION} -m venv ${VENV_NAME}
                        . ${VENV_NAME}/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    """
                }
            }
        }
        
        stage('Code Quality & Security') {
            parallel {
                stage('Lint Check') {
                    steps {
                        script {
                            sh """
                                . ${VENV_NAME}/bin/activate
                                pip install flake8 pylint
                                # Run flake8
                                flake8 . --max-line-length=120 --exclude=${VENV_NAME} || true
                                # Run pylint
                                pylint --exit-zero *.py || true
                            """
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        script {
                            sh """
                                . ${VENV_NAME}/bin/activate
                                # Install security scanning tools
                                pip install bandit safety
                                
                                # Run Bandit security scan
                                bandit -r . -f json -o bandit-results.json -ll || true
                                
                                # Check dependencies for known security vulnerabilities
                                safety check || true
                                
                                # Run detect-secrets for credential scanning
                                pip install detect-secrets
                                detect-secrets scan . > secrets-scan.json || true
                            """
                        }
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    try {
                        sh """
                            . ${VENV_NAME}/bin/activate
                            # Run tests with coverage
                            pytest -v --cov=app --cov-report=xml --cov-report=html test.py
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'UNSTABLE'
                        echo "Tests failed: ${e.getMessage()}"
                    }
                }
            }
            post {
                always {
                    // Archive test and coverage reports
                    archiveArtifacts artifacts: 'coverage.xml, htmlcov/**'
                    // Publish coverage report
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    try {
                        // Build Docker image
                        sh """
                            docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                                --build-arg PYTHON_VERSION=${PYTHON_VERSION} .
                            docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Docker build failed: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Security Scan Docker Image') {
            steps {
                script {
                    sh """
                        # Install Trivy
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

                        # Scan Docker image
                        trivy image ${DOCKER_IMAGE}:${BUILD_NUMBER} --no-progress --exit-code 0 \
                            --severity HIGH,CRITICAL --format template \
                            --template '{{- range . }}{{- range .Vulnerabilities }}{{println .VulnerabilityID .Severity .PkgName .InstalledVersion .FixedVersion }}{{- end }}{{- end }}' \
                            > trivy-results.txt
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-results.txt'
                }
            }
        }
        
        stage('Docker Login and Push') {
            steps {
                script {
                    try {
                        // Remove existing credentials and login
                        sh '''
                            rm -rf ~/.docker/config.json || true
                            echo $DOCKER_REGISTRY_CREDENTIALS_PSW | docker login -u $DOCKER_REGISTRY_CREDENTIALS_USR --password-stdin
                        '''
                        
                        // Push Docker images
                        sh """
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker push ${DOCKER_IMAGE}:latest
                        """
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Docker push failed: ${e.getMessage()}"
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline executed successfully!"
            // Notify on success if needed
            emailext (
                subject: "Pipeline Successful: ${currentBuild.fullDisplayName}",
                body: """
                    Pipeline completed successfully!
                    Build URL: ${env.BUILD_URL}
                    Coverage Report: ${env.BUILD_URL}Coverage_Report/
                """,
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        failure {
            echo "Pipeline failed! Check the logs for details."
            emailext (
                subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                body: """
                    Pipeline failed!
                    Build URL: ${env.BUILD_URL}
                    Console Output: ${env.BUILD_URL}console
                """,
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        always {
            // Clean up Docker
            sh '''
                docker logout || true
                rm -rf ~/.docker/config.json || true
            '''
            
            // Remove Docker images
            sh """
                docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true
                docker rmi ${DOCKER_IMAGE}:latest || true
            """
            
            // Clean workspace
            cleanWs(cleanWhenNotBuilt: false,
                   deleteDirs: true,
                   disableDeferredWipeout: true,
                   cleanWhenSuccess: true,
                   cleanWhenUnstable: true)
        }
    }
}
