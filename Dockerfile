FROM ubuntu:latest
RUN apt-get update && \
      apt-get -y install sudo
RUN adduser --disabled-password --gecos '' docker
RUN adduser docker sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
        USER dockerRUN curl -sS https://download.spotify.com/debian/pubkey_6224F9941A8AA6D1.gpg | sudo gpg --dearmor --yes -o /etc/apt/trusted.gpg.d/spotify.gpg
RUN echo "deb http://repository.spotify.com stable non-free" | tee /etc/apt/sources.list.d/spotify.list
RUN sudo apt-get update && sudo apt-get install spotify-client


RUN apt install python3.11 python3-pip -y
ENV WORKSPACE /opt/installs
RUN mkdir -p $WORKSPACE
WORKDIR $WORKSPACE
COPY requirements.txt requirements.txt
RUN python3.11 -m pip install -r requirements.txt
COPY . .
CMD ["python3.11", "startup/startup.py"]