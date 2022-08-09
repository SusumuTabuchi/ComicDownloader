FROM centos:centos7.9.2009

# ユーザー設定
ARG USER_NAME="dev_user"
ARG USER_PASSWORD="kiifsII9skkl3"
ARG JENKINS_USER="jenkins"
ARG JENKINS_USER_PASSWORD="usSF9fj"

# 言語設定
ENV LANG=en_US.UTF-8

#########
# ユーザーの作成
#########
# 開発ユーザー
RUN groupadd -g 1000 developer && \
    useradd -g developer -G wheel -m -d /home/${USER_NAME} -s /bin/bash ${USER_NAME} && \
    echo "${USER_NAME}:${USER_PASSWORD}" | chpasswd
# jenkinsユーザー
RUN groupadd -g 2000 jenkins && \
    useradd -g jenkins -G wheel -m -d /home/${JENKINS_USER} -s /bin/bash ${JENKINS_USER} && \
    echo "${JENKINS_USER}:${JENKINS_USER_PASSWORD}" | chpasswd

# Install dependence
RUN yum update -y --exclude=kernel* --exclude=centos* \
    && yum install -y sudo \
    wget \
    unzip \
    curl \
    bzip2 \
    firewalld \
    tar

#########
# Install GoogleChrome & Chrome Driver
#########
# chrome
ADD google-chrome.repo /etc/yum.repos.d/google-chrome.repo
RUN yum install -y google-chrome-stable \
                   libOSMesa
# fonts
RUN yum install -y google-noto-cjk-fonts \
                   ipa-gothic-fonts

# chromedriver
ADD ./get_google-chrome-driver.sh /usr/local/bin
RUN /usr/local/bin/get_google-chrome-driver.sh
RUN google-chrome --version

# Dependencies
RUN yum install -y libX11 \
                   GConf2 \
                   fontconfig

#########
# Python for miniconda
#########
ENV PYTHON_VERSION 3.9.12
ENV CONDA_DIR /opt/conda
ENV PATH ${CONDA_DIR}/bin:${PATH}

# conda
RUN curl -L https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && sudo bash /tmp/miniconda.sh -bfp /opt/conda/ \
    && rm -rf /tmp/miniconda.sh
RUN sudo /opt/conda/bin/conda install -y -c conda-canary -c defaults -c conda-forge \
    conda \
    conda-package-handling \
    python=$PYTHON_VERSION \
    pycosat \
    requests \
    ruamel_yaml \
    cytoolz \
    anaconda-client \
    nbformat \
    pytest \
    pytest-cov \
    pytest-timeout \
    mock \
    responses \
    pexpect \
    flake8 \
    enum34 \
    beautifulsoup4 \
    jupyterlab \
    selenium \
    pydrive \
    pymysql \
    pandas \
    toml \
    chromedriver-binary \
    jupyter_contrib_nbextensions \
    && sudo /opt/conda/bin/conda clean --all --yes

RUN sudo /opt/conda/bin/pip install codecov radon \
    && sudo rm -rf ~root/.cache/pip

#########
# jupyter
#########
RUN jupyter contrib nbextension install --sys-prefix
RUN jupyter nbextensions_configurator enable --user

#########
# MariaDB
#########
RUN wget https://downloads.mariadb.com/MariaDB/mariadb_repo_setup && \
    chmod +x mariadb_repo_setup && \
    ./mariadb_repo_setup && \
    yum install -y perl-DBI libaio libsepol lsof boost-program-options && \
    yum install -y MariaDB-client

#########
# Jenkins
#########
# java
RUN yum install -y java-11-openjdk.x86_64 git
# SSH
RUN yum install -y openssh \
    openssh-server
RUN mkdir /var/run/sshd
RUN ssh-keygen -t rsa -N "" -f /etc/ssh/ssh_host_rsa_key && \
    ssh-keygen -t dsa -N "" -f /etc/ssh/ssh_host_dsa_key && \
    ssh-keygen -t ecdsa -N "" -f /etc/ssh/ssh_host_ecdsa_key && \
    ssh-keygen -t ed25519 -N "" -f /etc/ssh/ssh_host_ed25519_key
RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
# ssh公開鍵
ADD ./setting_sshkey.sh /tmp/setting_sshkey.sh
USER jenkins
RUN mkdir ~/.ssh && \
    cd ~/.ssh && \
    touch authorized_keys

#########
# ユーザーの切り替え
#########
USER ${USER_NAME}

#########
# CMD
#########
# CMD ["/sbin/init"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "/sbin/init", "/usr/sbin/sshd"]