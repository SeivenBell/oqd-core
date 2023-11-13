FROM python:3.10.13-slim-bookworm

WORKDIR /app
ADD . /app
ENV PYTHONPATH /app
ENV PATH "$PATH:/opt/julia-1.9.3/bin"

RUN \
    apt update \
    && apt install wget -y \
    && wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.3-linux-x86_64.tar.gz -P /opt \
    && tar zxvf /opt/julia-1.9.3-linux-x86_64.tar.gz -C /opt \
    && julia -e 'using Pkg; Pkg.add(["QuantumOptics", "Configurations"])'

RUN pip install .[all]

CMD rq worker --with-scheduler & python main.py
