# Security Policy

## Reporting a vulnerability

Please report security issues privately to the repository owner instead of opening a public issue. Include a clear description, reproduction steps and the affected version.

## Security model

Vector PDF Suite treats uploaded files as untrusted input. The application enforces per-file and per-batch limits, validates supported file types, processes inputs in isolated temporary directories and removes temporary data after each job.

The desktop API listens only on the local loopback interface. Its shutdown endpoint is protected by a random per-session token and is not enabled in normal web deployments.

## Supported versions

Security fixes are applied to the latest published release.

## Public deployments

The default configuration is intended for local use. Before exposing the API to a public network, deploy it behind an authenticated reverse proxy, configure explicit CORS origins, add rate limiting and review storage and retention requirements for your environment.
