# Strong_App_Import

## Purpose

Ingestion of a flat file export from the `Strong App` that i use for my workout tracking as there is no API to access said data.

## SIPOC

### Scopes

- Operations external to this containerized app take place in an SMB network share.
  - The Ingestion, processing, and archival of a flat file export
- The insert/upsert of data in/into the Postgres Database
-

### Inputs

- Flat File Export
  - With this naming convention: `strong.csv`
  - into target location on client machine
  - With the following Columns:

| Column                      | Data Definition     | Nullability |
| --------------------------- | ------------------- | ----------- |
| RowID^[Postgres Table Only] | BIGINT IDENTITY(11) | NOT NULL    |
| Date                        | DATETIME2(7)        | NULL        |
| [Workout Name]              | NVARCHAR(500)       | NULL        |
| Duration                    | NVARCHAR(50)        | NULL        |
| [Exercise Name]             | NVARCHAR(500)       | NULL        |
| Set Order                   | TINYINT             | NULL        |
| Weight                      | DECIMAL(18, 2)      | NULL        |
| Reps                        | INT                 | NULL        |
| Distance                    | INT                 | NULL        |
| Seconds                     | INT                 | NULL        |
| Notes                       | NVARCHAR(1000)      | NULL        |
| [Workout Notes]             | NVARCHAR(1000)      | NULL        |
| RPE                         | DECIMAL(3, 1)       | NULL        |

- Configuration variables govern the service's behavior

TODO provide list of variables and their uses

### Process

TODO process documentation

## Installation

1. `python -m pip install poetry python-dotenv pre-commit`
1. `pre-commit install`
1. `pre-commit autoupdate`

---

Pull image from ghcr.io

```sh
docker pull ghcr.io/bryan-jenks-home-lab/etl_strong_app:main
```

Run image

```sh
docker run -d \
    -e DB_CONNECTION_STRING='postgresql+psycopg2://<USER>:<PASSWORD>@<SERVER>:<PORT>/<DATABASE>' \
    -e EXPECTED_FILE=strong.csv \
    -e TARGET_TABLE=<DATABASE>.<SCHEMA>.<TABLE_NAME> \
    -e WATCH_PATH=/data/inbound \
    -e STAGING_PATH=/data/outbound \
    -e PROCESSED_PATH=/data/processed \
    -v /<PATH_ON_YOUR_MACHINE>/strong_app_import/inbound:/data/inbound \
    -v /<PATH_ON_YOUR_MACHINE>/strong_app_import/outbound:/data/outbound \
    -v /<PATH_ON_YOUR_MACHINE>/strong_app_import/processed:/data/processed \
    ghcr.io/bryan-jenks-home-lab/etl_strong_app:main
```

---

### Outputs

- Data Payload into target database table
- Archived Flat File Export `strong.csv` in archival directory

### Customers

- Bryan

## Development Environment setup <!-- DOC finish fleshing out this section -->

### pre-commit hooks

-

### poetry

-

### makefile

## Deployment Details

- Environmental variables that need to be passed to the container should be placed in the portainer docker-compose stack interface and fed to the container

## Roadmap
