## SSL / TLS Fundamentals

SSL (Secure Sockets Layer) and its successor TLS (Transport Layer Security) are protocols used to secure communication over a network.

They provide:

- Encryption of data between client and server
- Authentication of the server identity
- Data integrity during transmission

In real-world production systems, SSL certificates are issued by trusted Certificate Authorities (CAs).
For local development, self-signed certificates are commonly used.

---

## Why mkcert

mkcert is a local development tool designed to simplify HTTPS setup.

It:

- Creates a local Certificate Authority (CA)
- Installs the CA into the operating system and browser trust store
- Generates locally trusted SSL certificates

Because the CA is trusted by the system, browsers show a valid lock icon instead of security warnings.

Important points:

- mkcert is installed on the local system, not inside the project
- Only generated certificates are stored in the repository

---

## Self-Signed Certificates (Local Development)

Self-signed certificates are certificates that are not issued by a public CA.

Using mkcert improves the self-signed workflow by:

- Making certificates trusted locally
- Avoiding browser warnings
- Providing a production-like HTTPS experience during development

These certificates are meant only for local or internal use.

---

## Certificate Storage Strategy

Certificates generated using mkcert are stored inside the project directory.

Responsibilities are clearly separated:

- Local system: certificate generation and trust
- Project repository: certificate storage
- Infrastructure layer: certificate usage

Certificates are later mounted into the reverse proxy container.

---

## Local Domain Mapping

A local domain is mapped to the local machine using the system hosts file.

This allows:

- Domain-based SSL certificate generation
- Browser lock icon verification
- A realistic, production-style local setup

Instead of accessing services via localhost, a custom local domain is used.

### screenshot of working

![ch](../screenshots/s1.png)
![js](../screenshots/s2.png)
![jj](../screenshots/s3.png)
