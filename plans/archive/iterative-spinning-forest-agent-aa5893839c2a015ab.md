# Plan: Fix n8n Workflow Data Mapping — SystemLink Check Distribution v2

## Diagnosis Summary

### Root Cause: HTTP Request nodes replace $json with their API response

The workflow has a chain: Route Switch -> Search X -> IF Exists -> Create X / Set ID -> ... -> Write

The problem: Every **HTTP Request** node (Search Vendor, Search Check, Search Project, Create Vendor, Create Check, Create Project) replaces `$json` with the Airtable API response. This means all the original parsed data (vendor, checkNumber, date, amount, etc.) is LOST as soon as the first Search node runs.

### Specific Issues Found

**Issue 1: Create Vendor/Check/Project nodes write BLANK data**
- `Create Vendor` body uses `$json.vendor` -- but after `Search Vendor`, `$json = {records: []}`, so `$json.vendor` is undefined
- `Create Check` body uses `$json.checkNumber`, `$json.date`, etc. -- all undefined after Search Check
- `Create Project` body uses `$json.project` -- undefined after Search Project
- **Evidence**: Execution 2409 shows Create Vendor output has `Vendor Name = BLANK`, Create Check has `Check # = BLANK`, etc.

**Issue 2: Set ID nodes lose original data too**
- `Set Vendor ID Existing` has `includeOtherFields: true` but `$json` at that point is `{records: [{id: ...}]}` from Search -- no original fields
- `Set Vendor ID New` has `includeOtherFields: true` but `$json` is `{id, createdTime, fields}` from Create -- no original fields
- Same for Set Check ID and Set Project ID nodes

**Issue 3: Prepare Data code nodes partially fix Write nodes**
- The Prepare CLI/Unassigned/Retainer Code nodes pull original data from `$('Route Switch').item.json`
- They also check `$json.vendorRecordId` and `$json.checkRecordId`
- **But** since `$json` at that point is the Airtable response (from Create/Search), `$json.vendorRecordId` is UNDEFINED
- The fallback `$('Set Vendor ID New (Assigned)').item.json.vendorRecordId` does work since n8n can resolve cross-node references
- However the data STILL arrives correctly for Write CLI (confirmed in execution data) because the Prepare node assembles it from Route Switch + explicit cross-node references

**Issue 4: Write Retainer has "Retention" field that doesn't exist in Retainers table**
- The Retainers table schema has NO "Retention" field (CLI and Unassigned do)
- Write Retainer body includes `"Retention": $json.retention` which causes: `Unknown field name: "Retention"`
- This is the error that killed execution 2409 for retainer items

**Issue 5: Checks table records are created with BLANK data**
- Even though Write CLI records land correctly (because Prepare nodes fix the data), the **Checks** and **Vendors** and **Projects** tables have blank records
- This is because Create Vendor/Check/Project use `$json.fieldName` which is undefined

### What Actually Works
- Parse & Route: Correctly parses QBO data (98 items: 78 assigned, 12 unassigned, 8 retainer)
- Route Switch: Correctly routes items  
- Prepare Data nodes: Correctly reassemble data for Write nodes using `$('Route Switch').item.json`
- Write CLI: Successfully writes records with data (via Prepare CLI Data)
- Write Unassigned: Successfully writes records with data (via Prepare Unassigned Data)
- Write Processed ID nodes: Work using `$('Route Switch').item.json.uniqueId`

### What Doesn't Work
- Create Vendor: Writes blank Vendor Name (all 3 branches)
- Create Check: Writes blank Check #, Date, Amount, etc. (all 3 branches)
- Create Project: Writes blank Project Name (Assigned + Retainer branches)
- Write Retainer: Fails with "Unknown field name: Retention"
- No Get Check Record / Patch Check Projects nodes exist (were in v2 design but never added)

## Fix Strategy

The cleanest fix that preserves the existing architecture is to change all `$json.fieldName` references in Create and Search-result-dependent nodes to use `$('Route Switch').item.json.fieldName` instead. This is the same pattern the Prepare Data nodes and Write Processed ID nodes already use successfully.

### Changes Required

**1. Fix Create Vendor body (all 3 branches: Assigned, Unassigned, Retainer)**
- Change: `$json.vendor` -> `$('Route Switch').item.json.vendor`

**2. Fix Create Check body (all 3 branches)**
- Change all `$json.X` references to `$('Route Switch').item.json.X`
- For `$json.vendorRecordId`: need to reference the Set Vendor node. Use a Prepare-style approach or cross-node reference.
- **Key insight**: When Create Check runs, vendorRecordId is on either `Set Vendor ID Existing` or `Set Vendor ID New`. Since only one of these ran, we need a fallback pattern.
- **Solution**: Use the `$('Route Switch').item.json` for original data, but for vendorRecordId use: the Prepare pattern of trying multiple sources

**3. Fix Create Project body (Assigned + Retainer branches)**
- Change: `$json.project` -> `$('Route Switch').item.json.project`
- Change: `$json.className` -> `$('Route Switch').item.json.className`

**4. Fix Write Retainer body**
- Remove `"Retention": $json.retention` from the body (Retainers table has no Retention field)

**5. Fix Set ID nodes to extract vendorRecordId/checkRecordId correctly**
- The Set nodes with `includeOtherFields: true` won't carry original data (since $json is the API response)
- But they DO carry the record ID, which is what matters for downstream nodes
- The Prepare Data nodes handle reassembly -- this is actually fine AS IS

### Better Approach: Replace Prepare + Write pattern with direct $('Route Switch') references

Since the Prepare Data nodes already work, and the Write nodes reference `$json` which comes from Prepare, the Write CLI/Unassigned paths actually work. The only broken things are:

1. **Create nodes** (Vendor/Check/Project) -- need `$('Route Switch')` refs
2. **Write Retainer** -- remove "Retention" field
3. **vendorRecordId in Create Check** -- this is tricky because it comes from a Set node after the IF branch

For vendorRecordId in Create Check: The Create Check node receives input from `Set Check ID New` (but that's wrong -- it receives from `IF Check Exists -> FALSE -> Create Check`). Wait, let me re-trace:

Actually: `IF Vendor Exists` -> FALSE -> `Create Vendor` -> `Set Vendor ID New` -> `Search Check` -> `IF Check Exists` -> FALSE -> `Create Check`

So at `Create Check`, `$json` is `{records: []}` from Search Check. But `$json.vendorRecordId` was set on the Set Vendor ID New node with `includeOtherFields: true`... except $json at Set Vendor ID New was the Create Vendor response `{id, fields}`, so `includeOtherFields` passes through `{id, fields, vendorRecordId}`.

Then Search Check REPLACES all of this with `{records: []}`. So vendorRecordId is lost again.

**The fundamental issue**: Every HTTP Request node wipes out $json. The Set nodes try to pass data through, but the next HTTP Request wipes it again.

### REVISED APPROACH: Convert Create nodes to Code nodes that reference Route Switch

Instead of fighting the HTTP Request $json replacement, change the Create Vendor/Check/Project nodes from HTTP Request nodes to Code nodes that:
1. Get original data from `$('Route Switch').item.json`
2. Get record IDs from the Set ID nodes (using cross-node references)
3. Make the Airtable API call directly
4. Return both the API response AND the original data

**Actually, even simpler**: Just fix all the body expressions to use `$('Route Switch').item.json.X` for original data fields, and for record IDs use cross-node `$()` references.

For vendorRecordId in Create Check:
```
$('Set Vendor ID Existing (Assigned)').item.json.vendorRecordId ?? $('Set Vendor ID New (Assigned)').item.json.vendorRecordId
```
Wait -- this won't work because only one of those paths executed. n8n's `$()` reference will error on the path that didn't run.

**Safest approach**: Use a try/catch in the expression, or use the fact that the Prepare Data Code nodes already handle this correctly.

Actually the simplest approach: **Replace Create nodes with Code nodes** that do the HTTP call inline AND return original data.

No wait, even simpler -- the v2 script design was correct. The issue is that HTTP Request nodes wipe $json. Let me think about what ACTUALLY works...

### FINAL FIX PLAN

The Prepare Data Code nodes already solve the data reassembly problem for the Write nodes. The remaining issues are:

1. **Create Vendor/Check/Project write blank data** to their respective tables
2. **Write Retainer references non-existent "Retention" field**
3. **Checks table has no Projects link** (Get Check Record / Patch Check Projects missing)

For (1): Change the jsonBody of Create Vendor/Check/Project to use `$('Route Switch').item.json.X` instead of `$json.X`. For vendorRecordId in Create Check, we can't easily reference the Set node since only one branch ran. **Solution**: Use a Code node before Create Check to assemble the data, or restructure to use the Prepare pattern.

**Simplest working fix**: 
- Change Create Vendor body: `$('Route Switch').item.json.vendor`
- Change Create Check body: Use `$('Route Switch').item.json.X` for all original fields. For vendorRecordId, since the Create Check node sits after BOTH vendor paths converge into Search Check, and the Set Vendor nodes (both existing and new) set vendorRecordId... but then Search Check wipes it. 

**THE ACTUAL SIMPLEST FIX**: Add Code nodes before each Create node that reassemble data from Route Switch + set the record IDs, OR replace the HTTP Request Create nodes with Code nodes.

Actually, I realize the Prepare Data nodes DO THIS ALREADY for the Write nodes. The problem is only the Create Vendor/Check/Project nodes. These can be fixed by:

**For Create Vendor**: Just change `$json.vendor` to `$('Route Switch').item.json.vendor`. No record IDs needed.

**For Create Check**: Change all fields to use `$('Route Switch').item.json.X`. For vendorRecordId, use a JavaScript expression that tries both paths. In n8n expressions we can't do try/catch, but we CAN use optional chaining or ternary logic. However, since this is inside `JSON.stringify()`, we're limited.

**ALTERNATIVE**: Convert Create Check to a Code node that:
```javascript
const orig = $('Route Switch').item.json;
let vendorRecordId = '';
try { vendorRecordId = $('Set Vendor ID Existing (Assigned)').item.json.vendorRecordId; } catch(e) {}
if (!vendorRecordId) {
  try { vendorRecordId = $('Set Vendor ID New (Assigned)').item.json.vendorRecordId; } catch(e) {}
}
// ... make the API call or just return prepared data
```

But this requires the Code node to have the Airtable API key to make HTTP calls, which complicates things.

**BEST APPROACH**: Insert a "Prepare Check Data" Set/Code node between the converge point (where Set Vendor ID Existing and Set Vendor ID New merge into Search Check) and Search Check. This node would grab vendorRecordId from $json (which at that point IS the Set Vendor output with vendorRecordId) and ALSO grab all original data from Route Switch. Then downstream Create Check can use $json.X.

Wait, but `includeOtherFields: true` on Set Vendor ID nodes means they DO have vendorRecordId plus the API response fields. Then Search Check wipes it. So if I add a node BETWEEN Set Vendor and Search Check that saves vendorRecordId...

Actually the simplest: **Just change the body expression strings in the Create HTTP Request nodes to use cross-node references**:

For Create Vendor (body):
```
$('Route Switch').item.json.vendor
```

For Create Check (body):
```
$('Route Switch').item.json.checkNumber  (for Check #)
$('Route Switch').item.json.date         (for Date)  
$('Route Switch').item.json.checkTotal   (for Amount)
$('Route Switch').item.json.checkUrl     (for Check URL)
$('Route Switch').item.json.memo         (for Memo)
$('Route Switch').item.json.paymentType  (for Payment Type)
$('Route Switch').item.json.className    (for Class)
```

For Vendor link in Create Check, we need vendorRecordId. This is tricky.

**OPTION A**: Don't include Vendor link in Create Check. Add it later via Patch.
**OPTION B**: Convert Create Check to Code node.
**OPTION C**: Add a Merge node that combines vendorRecordId from Set Vendor with Search Check output.

**OPTION B is cleanest**. Convert Create Vendor/Check/Project from HTTP Request nodes to Code nodes that:
1. Read original data from `$('Route Switch').item.json`
2. Read record IDs from the appropriate Set nodes using try/catch
3. Make the API call via fetch/http
4. Return the created record info AND the original data + record IDs

This way the entire chain preserves data.

### EXECUTION PLAN

**Step 1: Get the current workflow JSON from n8n** (DONE)

**Step 2: Identify all nodes that need fixing**
Per branch (Assigned/Unassigned/Retainer), the following need fixes:

For ALL branches:
- Create Vendor: Fix body to use `$('Route Switch').item.json.vendor`
- Create Check: Convert to Code node with try/catch for vendorRecordId
- Set Check ID New: Ensure it passes checkRecordId + original data

For Assigned and Retainer branches:
- Create Project: Fix body to use `$('Route Switch').item.json.project` and `className`
  
For Retainer only:
- Write Retainer: Remove "Retention" field from body

Missing nodes (nice to have but not critical for demo):
- Get Check Record + Patch Check Projects (for linking Projects to Checks)

**Step 3: Build the updated workflow**
- Modify the Create Vendor nodes: Change jsonBody to use Route Switch references
- Modify the Create Check nodes: Convert to Code nodes that use Route Switch + vendorRecordId from Set nodes  
- Modify the Create Project nodes: Change jsonBody to use Route Switch references
- Fix Write Retainer: Remove Retention field
- Preserve Set Configuration and Query QBO Checks exactly as-is

**Step 4: Deploy via n8n REST API PUT**

**Step 5: Clear all Airtable records** (already empty)

**Step 6: Trigger workflow execution**

**Step 7: Verify data in Airtable**

**Step 8: Fix and repeat if needed**

## COMPLETE FIX LIST

Every node downstream of Search Processed IDs that references `$json.fieldName` for original data needs to be changed to `$('Route Switch').item.json.fieldName`. The affected nodes are:

### Per Branch (x3: Assigned, Unassigned, Retainer)

| Node | Current Expression | Fix |
|------|-------------------|-----|
| Search Vendor filterByFormula | `$json.vendor` | `$('Route Switch').item.json.vendor` |
| Create Vendor jsonBody | `$json.vendor` | `$('Route Switch').item.json.vendor` |
| Search Check filterByFormula | `$json.checkNumber` | `$('Route Switch').item.json.checkNumber` |
| Create Check jsonBody | `$json.checkNumber`, `$json.date`, `$json.checkTotal`, `$json.vendorRecordId`, `$json.checkUrl`, `$json.memo`, `$json.paymentType`, `$json.className` | All change to `$('Route Switch').item.json.X` except vendorRecordId (see below) |

### Assigned + Retainer only

| Node | Current Expression | Fix |
|------|-------------------|-----|
| Search Project filterByFormula | `$json.project` | `$('Route Switch').item.json.project` |
| Create Project jsonBody | `$json.project`, `$json.className` | `$('Route Switch').item.json.X` |

### vendorRecordId in Create Check

This is the tricky one. Create Check body uses `$json.vendorRecordId` for the Vendor link. But `$json` is the Search Check response. The vendorRecordId was set on either Set Vendor ID Existing or Set Vendor ID New, but then wiped by Search Check.

**Solution**: Don't include Vendor in Create Check body. Instead, create a separate Patch node after Create Check to link the vendor. OR omit the Vendor link for now (it's a nice-to-have for the demo, since Vendor is a separate table with its own records).

Actually, the simplest: Change Set Vendor ID nodes to also save vendorRecordId using a different approach. Or, since we're already changing Create Check, use a different expression.

In n8n, you CAN use `$('NodeName').item.json.field` to reference any upstream node's output. But the issue is that ONLY ONE of Set Vendor ID Existing / Set Vendor ID New ran, so you can't reference the one that didn't run.

**Approach**: For vendorRecordId, remove it from Create Check body. Instead, we'll link Vendor to Check later. For the demo, the Check records will have all scalar fields (Check #, Date, Amount, etc.) but may not have the Vendor link. That's acceptable.

Actually, there's a better approach: Since we're already fixing the architecture, we can add a **Merge** node after the two vendor paths converge, or add a **Code node** before Create Check that assembles all needed data.

**SIMPLEST FOR DEMO**: Just omit the Vendor link from Create Check. The Check record will still have all the important data. Vendor records exist separately and CLI/Unassigned/Retainer records link to both.

### Write Retainer Fix

| Node | Issue | Fix |
|------|-------|-----|
| Write Retainer jsonBody | Has `"Retention": $json.retention` | Remove this field (doesn't exist in Retainers table) |

### Summary: Total nodes to modify

- 3x Search Vendor (filter formula)
- 3x Create Vendor (body)
- 3x Search Check (filter formula)
- 3x Create Check (body - remove Vendor link, use Route Switch refs for all other fields)
- 2x Search Project (filter formula) - Assigned + Retainer
- 2x Create Project (body) - Assigned + Retainer
- 1x Write Retainer (body - remove Retention)

**Total: 17 node parameter changes**

## Execution Steps

1. Load current workflow from .tmp/current-workflow-dump.json
2. Modify the 17 node parameters in Python
3. Preserve Set Configuration and Query QBO Checks exactly as-is
4. PUT the modified workflow to n8n
5. Trigger execution (manual or webhook)
6. Wait for completion
7. Check Airtable data
8. If issues, fix and repeat

## Constraints
- DO NOT modify Set Configuration or Query QBO Checks nodes
- DO NOT change credentials, URLs, or parameters on those nodes
- Use n8n REST API for all workflow updates
- Use Airtable REST API for data verification
