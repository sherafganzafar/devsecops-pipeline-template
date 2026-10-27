# AKS setup (one time) with cost guardrails

Run these in Azure Cloud Shell (portal.azure.com, the `>_` icon, Bash).
Free-account credit is USD 200 for 30 days. The goal is to spend almost none of it.

## 0. Before you start (portal)
- Cost Management > Budgets: create a USD 10 monthly budget with email alerts at 25%, 50%, 80% and 100%.
- Never click "Upgrade to pay-as-you-go".

## 1. Create everything with an expiry tag (4 hours)

```bash
RG=devsecops-rg
LOCATION=southeastasia
ACR=devsecopsacr$RANDOM
AKS=devsecops-aks
EXPIRY=$(date -d '+4 hours' +%s)

az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.ContainerRegistry

az group create --name $RG --location $LOCATION --tags delete-after=$EXPIRY
az acr create --resource-group $RG --name $ACR --sku Basic
az aks create --resource-group $RG --name $AKS --tier free \
  --node-count 1 --node-vm-size Standard_B2s \
  --attach-acr $ACR --generate-ssh-keys
```

Notes:
- `--tier free` means no paid control plane. Only the one node VM is billed.
- Do not enable monitoring add-ons, autoscaling or extra node pools.
- If `Standard_B2s` is not available for your subscription or region, the error message
  lists allowed sizes. Pick the smallest one and/or try another region.

## 2. Service principal for GitHub Actions

```bash
SUB=$(az account show --query id -o tsv)
az ad sp create-for-rbac --name devsecops-gh --role Contributor \
  --scopes /subscriptions/$SUB --sdk-auth
```

This is scoped to the whole subscription so the cleanup job still works after
the resource group is deleted. Use this subscription only for learning.

## 3. GitHub secrets (Settings > Secrets and variables > Actions)

| Secret | Value |
|---|---|
| `AZURE_CREDENTIALS` | the full JSON printed above |
| `ACR_NAME` | your ACR name (without .azurecr.io) |
| `AZURE_RESOURCE_GROUP` | `devsecops-rg` |
| `AKS_CLUSTER_NAME` | `devsecops-aks` |

Then: Actions tab > `deploy-aks` > Run workflow.

## 4. When you are done

```bash
az group delete --name devsecops-rg --yes --no-wait
```

The `azure-cleanup` workflow also deletes the group automatically once the
`delete-after` tag has passed. Check portal > Resource groups afterwards: it should be empty.
