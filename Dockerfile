FROM ubuntu:latest

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y clang libclang-dev \
        libc6-dev swig python3 python3-dev make

COPY ./ /app
WORKDIR /app

ENV LD_LIBRARY_PATH=/app/backend

RUN make -C /app/backend

CMD echo 'SERVER STARTING: http://localhost:8080/index.html'
CMD python3 backend/server.py 8080