pipeline {
  agent none

  stages {
    stage('Upload content'){
      parallel {
        stage('Roger_Roger MakeMKV Movies') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'collection=Roger_Roger; python3 ./loadplexdata.py -i /srv/masters_${collection}/MakeMKV -o /srv/plexmedia_${collection}_Movies/ -c ./convertMovies.yml'
          }
        }
        stage('Rose_Garden MakeMKV Movies') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'collection=Rose_Garden; python3 ./loadplexdata.py -i /srv/masters_${collection}/MakeMKV -o /srv/plexmedia_${collection}_Movies/ -c ./convertMovies.yml'
          }
        }
        stage('Donna_Collection MakeMKV Movies') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'collection=Donna_Collection; python3 ./loadplexdata.py -i /srv/masters_${collection}/MakeMKV -o /srv/plexmedia_${collection}_Movies/ -c ./convertMovies.yml'
          }
        }
        stage('Dragons_Den MakeMKV Movies') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'collection=Dragons_Den; python3 ./loadplexdata.py -i /srv/masters_${collection}/MakeMKV -o /srv/plexmedia_${collection}_Movies/ -c ./convertMovies.yml'
          }
        }
        stage('Koi_Pond MakeMKV Movies') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'collection=Koi_Pond; python3 ./loadplexdata.py -i /srv/masters_${collection}/MakeMKV -o /srv/plexmedia_${collection}_Movies/ -c ./convertMovies.yml'
          }
        }
        stage('Dragons_Den MakeMKV TV') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'collection=Dragons_Den; python3 ./loadplexdata.py -i /srv/masters_${collection}/MakeMKV -o /srv/plexmedia_${collection}_TV/ -c ./convertTV.yml'
          }
        }
        stage('Koi_Pond MakeMKV TV') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'collection=Koi_Pond; python3 ./loadplexdata.py -i /srv/masters_${collection}/MakeMKV -o /srv/plexmedia_${collection}_TV/ -c ./convertTV.yml'
          }
        }
        stage('PlayOn Movies') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'python3 ./loadplexdata.py -i /srv/masters_DVR/PlayOn -o /srv/plexmedia_DVR_Movies/ -c ./convertMovies.yml'
          }
        }
        stage('PlayOn Reformatted TV') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'python3 ./loadplexdata.py -i /srv/masters_DVR/PlayOn -o /srv/plexmedia_DVR_TV/ -c ./convertTV.yml'
          }
        }
        stage('PlayOn Format-Filtered TV') {
          agent {
            label "plex-shares"
          }
          steps {
            echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
            sh 'ls /srv/*/*'
            sh 'python3 ./loadplexdata.py --dvr -i /srv/masters_DVR/PlayOn -o /srv/plexmedia_DVR_TV/ -c ./convertTV.yml'
          }
        }
      }
    }
  }
}
