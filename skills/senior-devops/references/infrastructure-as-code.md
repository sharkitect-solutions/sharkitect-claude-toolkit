# Infrastructure as Code Deep Patterns

## Module Composition: Flat vs Nested

**Flat modules** (recommended for most teams):
Each module is independent. The root configuration composes them explicitly.
```hcl
module "vpc"     { source = "./modules/networking" }
module "rds"     { source = "./modules/data"       }
module "ecs"     { source = "./modules/compute"    }
```
Advantages: clear dependency graph, easy to test individually, simple state structure.

**Nested modules** (use only for published reusable modules):
A parent module calls child modules internally. The consumer sees one interface.
```hcl
module "platform" { source = "git::https://github.com/org/platform.git" }
```
Danger: nested modules hide complexity. When they break, debugging requires understanding
the full internal tree. Only use for well-tested, versioned, shared modules.

**Decision rule:** If more than one team will consume the module, nest and version it.
If only your team uses it, keep it flat.

## State Isolation Strategies

### Workspaces: Why They Are Dangerous for Production

Terraform workspaces share the same backend configuration and state file path prefix.
They were designed for temporary environments, not production isolation.

Problems with workspaces for prod/staging:
- One `terraform destroy` command with the wrong workspace selected wipes production
- No RBAC differentiation -- anyone with backend access can switch workspaces
- State files live in the same bucket prefix, making audit trails harder
- A workspace name typo creates a new empty state instead of erroring

### Separate State Files (Recommended)

```
environments/
  production/
    backend.tf       # bucket = "myco-tf-state", key = "prod/terraform.tfstate"
    main.tf
  staging/
    backend.tf       # bucket = "myco-tf-state", key = "staging/terraform.tfstate"
    main.tf
```
Each environment is a completely separate Terraform root. Different state files, different
backend configs, different IAM permissions. You cannot accidentally destroy production
from the staging directory.

## Import Strategies for Brownfield Infrastructure

### Step-by-step import workflow
1. Inventory existing resources: `aws ec2 describe-instances`, `gcloud compute instances list`
2. Write the Terraform resource blocks to match current configuration
3. Run `terraform import aws_instance.web i-1234567890abcdef0`
4. Run `terraform plan` -- output should show NO changes if import was accurate
5. Iterate: fix any drift between your HCL and actual state until plan is clean

### Bulk import with import blocks (Terraform 1.5+)
```hcl
import {
  to = aws_s3_bucket.logs
  id = "my-existing-bucket-name"
}
```
Run `terraform plan -generate-config-out=generated.tf` to auto-generate HCL.
Review generated code carefully -- it is verbose and often includes defaults you
should strip out to keep modules clean.

### Common import pitfalls
- Importing an Auto Scaling Group does NOT import its launch template or instances
- Importing an RDS instance does NOT import parameter groups or subnet groups
- Security group rules must be imported separately from security groups
- Always check `terraform state show <resource>` after import to verify attributes

## Terraform Plan Output in CI Gates

Parse plan output programmatically to gate deployments:
```bash
terraform plan -out=tfplan -detailed-exitcode
# Exit code 0 = no changes
# Exit code 1 = error
# Exit code 2 = changes present

terraform show -json tfplan | jq '.resource_changes[] |
  select(.change.actions | contains(["delete"])) |
  .address'
```
Use this to require manual approval for any plan that contains `delete` actions.
Automate `create` and `update` plans. Block `delete` plans for review.

## Provider Version Pinning

```hcl
terraform {
  required_version = ">= 1.5.0, < 2.0.0"   # Pin Terraform itself
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"    # Allow patch updates, block minor
    }
  }
}
```
Run `terraform init -upgrade` to update within constraints. Never use `>= X` without
an upper bound -- a major version bump can destroy infrastructure via schema changes.

## Secret Management in IaC

### Decision Matrix

| Approach | Complexity | Security | Use When |
|----------|-----------|----------|----------|
| AWS SSM Parameter Store | Low | Good | Small teams, AWS-only |
| HashiCorp Vault | High | Excellent | Multi-cloud, dynamic secrets needed |
| SOPS + git | Medium | Good | Need secrets in version control (encrypted) |
| GCP Secret Manager | Low | Good | Small teams, GCP-only |

### Vault Integration Pattern
```hcl
data "vault_generic_secret" "db" {
  path = "secret/data/production/database"
}

resource "aws_db_instance" "main" {
  password = data.vault_generic_secret.db.data["password"]
}
```
Vault generates short-lived credentials. Terraform reads them at plan/apply time.
The secret never exists in state -- only a reference to the Vault path.

**SOPS pattern** for teams not ready for Vault:
```bash
sops --encrypt --age $(cat ~/.sops/age-key.pub) secrets.yaml > secrets.enc.yaml
```
Encrypted file committed to git. Decrypted at CI/CD time with the private key
stored in the CI secret store. Never commit the plaintext file.

## Cost Estimation with Infracost

```bash
infracost breakdown --path=. --format=json --out-file=/tmp/infracost.json
infracost diff --path=. --compare-to=/tmp/infracost-base.json
```
Integrate into CI: fail the pipeline if monthly cost increase exceeds a threshold.
```bash
DIFF=$(infracost diff --path=. --compare-to=base.json --format=json |
  jq '.diffTotalMonthlyCost | tonumber')
if (( $(echo "$DIFF > 500" | bc -l) )); then
  echo "Cost increase exceeds $500/month. Requires manual approval."
  exit 1
fi
```

## Drift Detection and Remediation

### Scheduled drift checks
Run `terraform plan` on a cron schedule (daily or weekly). If exit code is 2 (changes
detected), notify the team via Slack/PagerDuty.

### Common drift sources
- Console changes: someone modified a security group rule via AWS Console
- Auto Scaling events: ASG launched instances not in state
- External automation: another tool modified the same resource
- Tag propagation: AWS applies tags that Terraform does not manage

### Remediation options
1. **Accept drift:** Update HCL to match current state (`terraform state show` -> copy)
2. **Revert drift:** Run `terraform apply` to force resources back to declared state
3. **Ignore drift:** Use `lifecycle { ignore_changes = [tags] }` for attributes managed externally

Rule: if a resource is managed by Terraform, ALL changes go through Terraform.
If another system must modify it, use `ignore_changes` for those specific attributes
to prevent Terraform from reverting them on every apply.

## Advanced: State File Internals

Terraform state is a JSON document mapping resource addresses to cloud provider IDs.
Understanding its structure explains many confusing behaviors:

- `serial` increments on every write. Two concurrent `apply` runs with the same serial
  cause a state conflict -- this is why locking exists.
- `lineage` is a UUID generated at `init`. Moving state between backends requires matching
  lineage or using `-force-copy`.
- Each resource entry contains the full API response from the provider. This is why state
  files contain secrets -- the provider stores the database password it received.
- `terraform state pull | jq '.resources | length'` tells you state size. Over 500
  resources in a single state file is a signal to split.

### State Surgery

```bash
# Move a resource from one state to another (splitting monolith state)
terraform state mv -state-out=../new-project/terraform.tfstate \
  'module.database' 'module.database'

# Rename a resource without destroying it (refactoring modules)
terraform state mv 'aws_instance.old_name' 'aws_instance.new_name'

# Remove a resource from state without destroying it (adopting by another tool)
terraform state rm 'aws_instance.manual'
```

State surgery is irreversible without backups. Always `terraform state pull > backup.json`
before any `state mv` or `state rm` operation.

## The Abstraction Trap

The most common IaC failure mode in mature organizations is over-abstraction. Teams build
"platform modules" with 50+ variables, conditionals for every cloud provider, and
multi-level nesting. Debugging requires reading 4 layers of modules to understand
what `variable "enable_enhanced_monitoring"` actually does.

**Litmus test:** If a new team member cannot understand what a module deploys by reading
it for 5 minutes, the module is too abstract. Flatten it. Duplicate code between
environments is cheaper than a module that nobody can debug at 2 AM during an incident.
