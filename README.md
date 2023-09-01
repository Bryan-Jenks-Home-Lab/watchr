# Watchr

<!-- markdownlint-disable MD033-->
<!-- Header & Preview Image -->

<h1 align="center">
  <a href="https://www.apple.com/ios/health/" target="_blank">
    <img src="images/applehealth.jpeg" height="50%" width="50%">
  </a>
</h1>

<!-- Shields -->
<p align="center">
  <a href="https://github.com/Bryan-Jenks-Home-Lab/watchr/blob/master/LICENSE">
    <img src="https://img.shields.io/static/v1.svg?style=flat&label=License&message=Apache 2.0&logoColor=eceff4&logo=github&colorA=black&colorB=green"/>
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg"/>
  </a>
  <img src="https://img.shields.io/github/commit-activity/m/Bryan-Jenks-Home-Lab/watchr">
  <a href="https://github.com/Bryan-Jenks-Home-Lab/watchr/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/Bryan-Jenks-Home-Lab/watchr"/>
  </a>
  <img src="https://img.shields.io/github/v/release/Bryan-Jenks-Home-Lab/watchr">
  <a href="https://wakatime.com/badge/github/Bryan-Jenks-Home-Lab/watchr">
    <img src="https://wakatime.com/badge/github/Bryan-Jenks-Home-Lab/watchr.svg"/>
  </a>
  <a href="https://github.com/marketplace/actions/super-linter">
    <img src="https://github.com/Bryan-Jenks-Home-Lab/watchr/workflows/Lint%20Code%20Base/badge.svg"/>
  </a>
  <a href="https://interrogate.readthedocs.io/en/latest/">
    <img src="images/interrogate_badge.svg"/>
  </a>
  <a href="https://github.com/Bryan-Jenks-Home-Lab/watchr/pulls">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?longCache=true" alt="Pull Requests">
  </a>
</p>

<!-- Description -->

> `Watchr` Is a file watching service for importing records into a Postgres database.

Watchr is organized through the usage of Pydantic models to govern the behavior of how a file get processed, the actions around its artifact cleanup, and other configuration.

This project is still rough and narrowly focused for my own personal use cases at the moment but in the future i may put forth more intention in making this more general and accessible to others.

---

## Table of Contents

---

- [Watchr](#watchr)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
    - [Recommended](#recommended)
  - [Installation](#installation)
    - [Users](#users)
    - [Contributors](#contributors)
  - [Usage](#usage)
    - [Example](#example)
  - [Documentation](#documentation)
  - [Resources](#resources)
  - [Development](#development)
    - [Security](#security)
    - [Future](#future)
    - [History](#history)
    - [Community](#community)
  - [Credits](#credits)
  - [License](#license)

---

## Features

---

[Return To Top](#table-of-contents)

<++>

---

## Requirements

---

[Return To Top](#table-of-contents)

<++>

---

### Recommended

---

[Return To Top](#table-of-contents)

<++>

---

## Installation

---

[Return To Top](#table-of-contents)

<++>

---

### Users

---

[Return To Top](#table-of-contents)

<++>

See [Usage](#usage)

---

### Contributors

---

[Return To Top](#table-of-contents)

See [CONTRIBUTING](CONTRIBUTING.md)

---

## Usage

---

[Return To Top](#table-of-contents)

<++>

---

### Example

---

[Return To Top](#table-of-contents)

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

## Documentation

---

[Return To Top](#table-of-contents)

<++>

---

## Resources

---

[Return To Top](#table-of-contents)

<++>

---

## Development

---

[Return To Top](#table-of-contents)

1. `python -m pip install poetry python-dotenv pre-commit`
1. `pre-commit install`
1. `pre-commit autoupdate`

See [Road Map](ROADMAP.md)

---

### Security

---

[Return To Top](#table-of-contents)

See [SECURITY](SECURITY.md)

---

### Future

[Return To Top](#table-of-contents)

See [ROADMAP](ROADMAP.md)

---

### History

[Return To Top](#table-of-contents)

See [RELEASES](https://github.com/Bryan-Jenks-Home-Lab/watchr/releases)

---

### Community

---

[Return To Top](#table-of-contents)

<++>

See [CODE OF CONDUCT](CODE_OF_CONDUCT.md)

---

## Credits

---

[Return To Top](#table-of-contents)

See [AUTHORS](AUTHORS.md)

---

## License

---

[Return To Top](#table-of-contents)

See [LICENSE](LICENSE)
