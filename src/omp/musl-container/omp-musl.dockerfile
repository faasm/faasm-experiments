FROM alpine

RUN apk update && \
    apk add g++ libgomp make

# Compile omp programs
COPY src /build
WORKDIR /build
RUN make

# clean up
RUN rm -rf /build
WORKDIR /
