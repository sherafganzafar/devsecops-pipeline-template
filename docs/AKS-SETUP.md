# AKS setup (one time)

Run these in Azure Cloud Shell (portal.azure.com, the `>_` icon) or any terminal
with the Azure CLI. Replace the names if you like. ACR names must be globally
unique and lowercase.

```bash
RG=devsecops-rg
LOCATION=southeastasia
ACR=devsecopsacr$RANDOM
AKS=devsecops-aks

az group create --name $RG --location $LOCATION
az acr create --resource-group $RG --name $ACR --sku Basic
az aks create --resource-group $RG --name $AKS --node-count 1 \
  --node-vm-size Standard_B2s --attach-acr $ACR --generate-ssh-keys

# Service principal that GitHub Actions will use
SUB=$(az account show --query id -o tsv)
az ad sp create-for-rbac --name devsecops-gh --role Contributor \
  --scopes /subscriptions/$SUB/resourceGroups/$RG --sdk-auth
```

The last command prints a JSON block. Copy it into a GitHub secret.

## GitHub secrets (Settings, Secrets and variables, Actions)

| Secret | Value |
|---|---|
| `AZURE_CREDENTIALS` | the full JSON from the last command |
| `ACR_NAME` | your ACR name (without .azurecr.io) |
| `AZURE_RESOURCE_GROUP` | `devsecops-rg` |
| `AKS_CLUSTER_NAME` | `devsecops-aks` |

Then: Actions tab, `deploy-aks`, Run workflow.

## Cost warning

AKS nodes are billed while the cluster exists. When you are done (screenshots
taken, post written), delete everything:

```bash
az group delete --name devsecops-rg --yes --no-wait
```
