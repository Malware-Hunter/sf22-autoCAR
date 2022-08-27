FROM ubuntu:focal

#Install System Dependecies for R
#https://environments.rstudio.com/docker (Last Acess 27-August-2022)
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    apt-transport-https \
    build-essential \
    curl \
    gfortran \
    libatlas-base-dev \
    libbz2-dev \
    libcairo2 \
    libcurl4-openssl-dev \
    libicu-dev \
    liblzma-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpcre3-dev \
    libtcl8.6 \
    libtiff5 \
    libtk8.6 \
    libx11-6 \
    libxt6 \
    locales \
    tzdata \
    zlib1g-dev \
    wget \
    vim \
    openjdk-17-jdk

#Install R
RUN DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends software-properties-common dirmngr -y
RUN DEBIAN_FRONTEND=noninteractive wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
RUN DEBIAN_FRONTEND=noninteractive apt update
RUN DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends r-base -y

#Install R Packages
RUN Rscript --no-save -e 'install.packages("arules", repos="http://cran.r-project.org")'
RUN Rscript --no-save -e 'install.packages("arulesCBA", repos="https://cran.rstudio.com")'

WORKDIR /sf22
COPY . ./
RUN DEBIAN_FRONTEND=noninteractive apt install python3-pip -y
RUN DEBIAN_FRONTEND=noninteractive pip install -r requirements.txt
