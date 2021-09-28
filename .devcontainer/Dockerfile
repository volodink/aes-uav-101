FROM node:16-alpine


RUN apk update && apk upgrade && \
    echo @edge http://nl.alpinelinux.org/alpine/edge/community >> /etc/apk/repositories && \
    echo @edge http://nl.alpinelinux.org/alpine/edge/main >> /etc/apk/repositories && \
    echo @edge http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories && \
    apk add \
      git \
      mc \
      htop \
      grep \
      chromium@edge \
      freetype@edge \
      harfbuzz@edge \
      wqy-zenhei@edge \
      ttf-liberation@edge \
      font-noto-devanagari@edge \
      font-noto-arabic@edge \
      font-noto-bengali@edge \
      tree \
      zsh-vcs@edge \
      zsh@edge \
      alpine-sdk \
      nss@edge \
      openrc iptables ca-certificates dumb-init git-lfs openssl tzdata wget \
      bash bash-doc bash-completion \
      shadow \
      util-linux build-base gcc abuild binutils binutils-doc gcc-doc \
      cmake cmake-doc extra-cmake-modules extra-cmake-modules-doc \
      ccache ccache-doc pciutils usbutils coreutils binutils findutils grep sudo

RUN npm install -g @marp-team/marp-cli
RUN npm install -g markdown-it-plantuml

USER node

RUN git config --global user.name "volodink" && git config --global user.email "volodin.konstantin@gmail.com"

RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

RUN sed -i 's/ZSH_THEME=\"robbyrussell\"/ZSH_THEME=\"half-life\"/g' /home/node/.zshrc

ENV IS_DOCKER true