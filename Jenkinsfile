pipeline {
    agent any 
    environment {
        PYTHON_PATH = 'C:/google_scraping/venv/Scripts/python' // Python Virtual Environment
    }
    stages {
        stage('Cloning Repository') {
            steps {
                git url: 'https://github.com/Enzymedica-Inc/google_scraping.git', branch: 'main'
            }
        }
        stage('Setup Python Environment') {
            steps {
                sh "${PYTHON_PATH} -m pip install -r requirements.txt"
            }
        }
        stage('Run_Google_Scraping_Script') {
            steps {
                sh "${PYTHON_PATH} C:\google_scraping\google_scraping_script.py"
            }
        }
        stage('ML_Models_Implementation') {
            steps {
                sh "${PYTHON_PATH} C:\google_scraping\google_KW_ML_models.py"
            }
        }
        stage('Amazon_Keywords_Clustering') {
            steps {
                sh "${PYTHON_PATH} C:\google_scraping\keywords_for_amazon.py"
            }
        }
        // stage('Loading into DB') {
        //     steps {
        //         sh "${PYTHON_PATH} /Users/d.tanubudhi/Documents/google_scraping/db_insertion.py"
        //     }
        // }
    }
    post {
        always {
            // Clean up workspace after job completes
            cleanWs()
        }
    }
}
