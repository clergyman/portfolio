# Portfolio API Test Pack

Realistic `pytest` API automation project for a fictional `user-portfolio` microservice in a trading platform.

The suite is designed to be runnable on a clean workstation without any service running on `localhost`. It combines:

- a local OpenAPI contract for a portfolio service
- mocked HTTP API tests that still produce real request/response objects
- Petstore-based smoke scenarios modeled on public Swagger endpoints
- contract, API, integration, and end-to-end style layers
- minimal Allure result generation without test annotations

## What is in scope

- Contract coverage against a local OpenAPI 3 document
- Realistic domain setup helpers for portfolios, transfers, orders, and valuation
- Offline HTTP interaction testing using `requests` plus `responses`
- Allure result generation through the `allure-pytest` plugin

## Project layout

```text
openapi/
  user-portfolio.yaml

tests/
  helpers/
  contracts/
  api/
  integration/
  e2e/
  public_sandbox/

allurerc.mjs
package.json
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -e .
npm install
pytest
```

Pytest writes raw Allure results to `allure-results/`.

## Allure

Generate a local report from existing test results:

```bash
npx allure generate allure-results -o allure-report --clean
```

Open the generated report:

```bash
npx allure open allure-report
```

## Test selection

Run the full offline suite:

```bash
pytest
```

Run only modeled portfolio coverage:

```bash
pytest -m "contract or api or integration or e2e"
```

Run only Petstore-shaped smoke scenarios:

```bash
pytest tests/public_sandbox -m smoke
```

Run optional live checks against the public Petstore sandbox:

```bash
RUN_LIVE_SANDBOX=1 pytest -m live
```

## Environment variables

- `PORTFOLIO_API_BASE_URL`: defaults to `https://portfolio-api.sandbox.allyre.example`
- `PUBLIC_SANDBOX_BASE_URL`: defaults to `https://petstore3.swagger.io/api/v3`
- `RUN_LIVE_SANDBOX`: set to `1` to execute real outbound sandbox checks
- `TEST_ENVIRONMENT`: defaults to `local`

## Notes

- The default suite is fully offline and does not require a running backend.
- The portfolio API itself is fictional, but the test structure mirrors a real microservice test repository.
