# DevSecOps Pipeline Template

A small, working template that shows security scanning as part of CI/CD:
a GitHub Actions pipeline that scans dependencies with Snyk, summarizes the
result in the run page, blocks the build on high/critical findings, and only
then builds the Docker image.

## What is inside

| Path | Purpose |
|---|---|
| `app/main.py` | Tiny Flask service with a `/health` endpoint |
| `Dockerfile`, `docker-compose.yml` | Container build, runs as a non-root user |
| `.github/workflows/security.yml` | Scan, gate, then build. Runs on push, PRs and weekly |
| `k8s/` | Deployment and Service manifests |
| `.github/workflows/deploy-aks.yml` | Manual deploy to Azure Kubernetes Service (see `docs/AKS-SETUP.md`) |
| `scripts/summarize_snyk.py` | Reads Snyk JSON, prints a severity table, fails above a threshold |

## Pipeline flow

```
push / PR / weekly
      |
  Snyk scan --> summary in run page --> gate (fail on high+)
        --> docker build --> deploy to a temporary kind cluster --> /health smoke test

  manual: deploy-aks workflow --> ACR build --> AKS deploy
```

## Setup

1. Create a free Snyk account and copy your API token.
2. In your GitHub repo: Settings > Secrets and variables > Actions > New secret,
   name it `SNYK_TOKEN`.
3. Push to `main` or open a pull request. Check the Actions tab.

## Run locally

```bash
docker compose up --build
curl localhost:8000/health

# test the summary script on a sample report
python scripts/summarize_snyk.py tests/sample-snyk-results.json --fail-on high
```

## Tuning

- Change `--fail-on high` to `critical` for a softer gate, or `medium` for a stricter one.
- Add `snyk container test` or `snyk iac test` steps to cover images and Terraform.

## Notes

This is a template. Results depend on your dependencies and Snyk's database at
the time of the run.
