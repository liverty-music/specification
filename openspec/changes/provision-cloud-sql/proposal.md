# Provision Cloud SQL

## Background

The backend application requires a reliable, scalable, and secure relational database to store user, artist, and concert data. Currently, no persistent database infrastructure exists.

## Goal

Provision a production-ready PostgreSQL database using Google Cloud SQL Enterprise Plus.

## Non-Goals

- Database schema migration (handled by `backend` application workflows).
- Populating initial data.
