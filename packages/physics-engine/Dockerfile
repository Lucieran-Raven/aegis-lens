FROM rust:1.75-alpine as builder

WORKDIR /app

COPY Cargo.toml ./
COPY src ./src

RUN cargo build --release

FROM alpine:latest

RUN apk add --no-cache ca-certificates

WORKDIR /app

COPY --from=builder /app/target/release/physics-engine /usr/local/bin/physics-engine

EXPOSE 8080

CMD ["physics-engine"]
