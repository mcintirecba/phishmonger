# Relevant Citation:

Dobolyi, D. G., & Abbasi, A. (2016, September). Phishmonger: A free and open source public archive of real-world phishing websites. In Intelligence and Security Informatics (ISI), 2016 IEEE Conference on (pp. 31-36). IEEE.
https://ieeexplore.ieee.org/document/7745439

# Usage

### To build the Docker image, use:

docker build -t phishmonger_docker .

### To run the Docker image, use:

docker run -it phishmonger_docker

### To execute PhishMonger from bash, use:

python3 pullPhishLoop.py

### To exit the Docker image from bash (i.e., from within), use:

exit

### To stop the Docker image from outside, use:

docker ps -a # to get <container ID>
docker stop <container ID>

### To restart/re-attach the Docker image and re-enter bash, use:

docker ps -a # to get <container ID>
docker start <container ID>
docker attach <container ID>

### To extract/copy PhishMonger output from the Docker image to the current host path, use:

docker ps -a # to get <container ID>
docker cp <container ID>:/phishmonger/output .
