FROM amd64/amazonlinux:latest

# Install program
ADD ./build /code/build
WORKDIR /code/build
RUN yum install -y python3-pip
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -e .