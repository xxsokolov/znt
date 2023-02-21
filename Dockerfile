FROM python:3.10
MAINTAINER Luke Crooks "luke@pumalo.org"

#RUN pip install --upgrade pip
#WORKDIR /opt/app/znt

WORKDIR /home/app/znt
RUN mkdir -p /home/app/znt
RUN cd /home/app/znt
RUN git clone https://github.com/xxsokolov/znt.git .

RUN dir /home/app/znt
RUN ls -la /home/app/znt
RUN python -m venv venv
RUN pip install --upgrade pip
RUN ls .
RUN ["/bin/bash", "-c", "source venv/bin/activate"]
RUN pip install -r /home/app/znt/.requirements
CMD ["/bin/bash"]

