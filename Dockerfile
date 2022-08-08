FROM centos:centos7.9.2009

# ユーザー設定
ARG USER_NAME="dev_user"
ARG USER_PASSWORD="kiifsII9skkl3"

# 言語設定
ENV LANG=en_US.UTF-8

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
    && sudo /opt/conda/bin/conda clean --all --yes

RUN sudo /opt/conda/bin/pip install codecov radon \
    && sudo rm -rf ~root/.cache/pip

# RUN sudo yum -y install epel-release
# RUN sudo yum -y update
# # RUN sudo reboot
# RUN sudo yum groupinstall "Development Tools" -y
# RUN sudo yum install openssl-devel libffi-devel bzip2-devel -y

# RUN curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
# RUN tar xfv Python-${PYTHON_VERSION}.tgz
# RUN rm -rf Python-3.9.12.tgz

# RUN cd Python-${PYTHON_VERSION}
# RUN ./configure --enable-optimizations
# RUN sudo make altinstall

# # pip
# RUN curl -O https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
# RUN python /tmp/get-pip.py

# # symlink for python3.x
# RUN  PY_MVER=$(echo ${PYTHON_VERSION} | sed s/\.[0-9,]\.[0-9,]*$//g); \
# echo ${PY_MVER}; \
# if [ "${PY_MVER}" = "3" ]; then \
#       ln -s /usr/local/bin/python3 /usr/local/bin/python; \
#       ln -s /usr/local/bin/pip3 /usr/local/bin/pip; \
# fi

# # pip modules
# RUN pip install --upgrade pip
# RUN pip install selenium

# ユーザーの作成と切り替え
RUN groupadd -g 1000 developer && \
    useradd -g developer -G wheel -M -d /home/${USER_NAME} -s /bin/bash ${USER_NAME} && \
    echo "${USER_NAME}:${USER_PASSWORD}" | chpasswd
USER ${USER_NAME}

CMD ["/sbin/init"]