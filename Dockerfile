FROM ubuntu:16.04

ARG DEBIAN_FRONTEND="noninteractive"
ARG PYTHON_VERSION="3.8.5"

# pyenv variables
ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PATH="/opt/pyenv/shims:/opt/pyenv/bin:$PATH" \
    PYENV_ROOT="/opt/pyenv" \
    PYENV_SHELL="bash"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    sudo \
    git \
    vim \
    zip \
    unzip \
    htop \
    bzip2 \
    libx11-6 \
    build-essential \
    ca-certificates \
    libbz2-dev \
    libffi-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    liblzma-dev \
    llvm \
    make \
    netbase \
    pkg-config \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install pyenv
RUN git clone --depth 1 https://github.com/pyenv/pyenv.git $PYENV_ROOT && \
    pyenv install $PYTHON_VERSION && \
    pyenv global $PYTHON_VERSION && \
    find $PYENV_ROOT/versions -type d '(' -name '__pycache__' -o -name 'test' -o -name 'tests' ')' -exec rm -rf '{}' + && \
    find $PYENV_ROOT/versions -type f '(' -name '*.pyo' -o -name '*.exe' ')' -exec rm -f '{}' + && \
    rm -rf /tmp/*

# update wheel
RUN pip install --upgrade pip setuptools wheel

# workdir
WORKDIR /home

# .vimrc and supertab
RUN git clone --depth 1 https://github.com/amix/vimrc.git ~/.vim_runtime && \
    sh ~/.vim_runtime/install_awesome_vimrc.sh
RUN git clone --depth 1 https://github.com/ervandew/supertab.git ~/.vim_runtime/my_plugins/supertab

# bachrc: shortcut and disalbe Ctrl+S
RUN echo 'alias st="git status"' >> ~/.bashrc && \
    echo 'stty -ixon' >> ~/.bashrc && \
    echo 'TERM="xterm-256color"' >> ~/.bashrc && \
    echo 'set t_ut=' >> ~/.vimrc && \
    echo "let g:snipMate = { 'snippet_version' : 1 }" >> ~/.vimrc

# fzf
RUN git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && \
    ~/.fzf/install

# ripgrep
RUN curl -LO https://github.com/BurntSushi/ripgrep/releases/download/13.0.0/ripgrep_13.0.0_amd64.deb && \
    dpkg -i ripgrep_13.0.0_amd64.deb && rm ripgrep*
