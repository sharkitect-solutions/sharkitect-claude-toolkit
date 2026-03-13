# Cross-Platform File Operation Commands

## Platform Detection

```python
import platform
system = platform.system()  # 'Windows', 'Darwin', 'Linux'
```
## Listing and Inventory

**List files with details -- PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse -File |
  Select-Object FullName, Length, LastWriteTime, Extension | Sort-Object Length -Descending
```
**Bash (Linux; macOS lacks -printf, use `stat -f` instead):**
```bash
find . -type f -printf '%s\t%T+\t%p\n' | sort -rn
```

**Count files by extension -- PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse -File |
  Group-Object Extension | Sort-Object Count -Descending | Select-Object Count, Name
```
**Bash:**
```bash
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
```

**Find large files (100MB+) -- PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse -File | Where-Object { $_.Length -gt 100MB } |
  Sort-Object Length -Descending |
  Select-Object @{N='SizeMB';E={[math]::Round($_.Length/1MB,1)}}, FullName
```
**Bash:**
```bash
find . -type f -size +100M -exec ls -lh {} \; | sort -k5 -rh
```

**Find old files (90+ days) -- PowerShell:**
```powershell
$cutoff = (Get-Date).AddDays(-90)
Get-ChildItem -Path . -Recurse -File | Where-Object { $_.LastWriteTime -lt $cutoff } |
  Sort-Object LastWriteTime | Select-Object LastWriteTime, FullName
```
**Bash:**
```bash
find . -type f -mtime +90 -printf '%T+ %p\n' | sort
```
## Moving with Metadata Preservation

**PowerShell (same volume):** `Move-Item -Path "source.pdf" -Destination "dest\source.pdf"`

**PowerShell (cross-volume):** `robocopy "C:\source" "D:\dest" "file.pdf" /MOV /COPY:DAT`

**Bash:** `mv source.pdf dest/` (same FS) or `cp -a source.pdf dest/ && rm source.pdf` (cross-FS)

**Python (cross-platform, recommended):**
```python
import shutil, os
shutil.copy2(src, dst)    # Preserves timestamps
os.remove(src)
```

**Bulk move with JSON logging -- PowerShell:**
```powershell
$log = @()
Get-ChildItem -Path ".\unsorted" -File | ForEach-Object {
    $dest = ".\sorted\$($_.Extension.TrimStart('.'))"
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    $entry = [PSCustomObject]@{
        Timestamp = Get-Date -Format 'o'; Action = 'move'
        Source = $_.FullName; Dest = Join-Path $dest $_.Name
    }
    Move-Item -Path $_.FullName -Destination $entry.Dest; $log += $entry
}
$log | ConvertTo-Json | Set-Content ".\move-log.json"
```
## Duplicate Detection

**Find exact duplicates by hash -- PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse -File |
  ForEach-Object { [PSCustomObject]@{
    Hash = (Get-FileHash $_.FullName -Algorithm MD5).Hash; Path = $_.FullName
  }} | Group-Object Hash | Where-Object { $_.Count -gt 1 } |
  ForEach-Object { $_.Group | Format-Table }
```
**Bash:**
```bash
find . -type f -exec md5sum {} + | sort | uniq -w32 -dD
```

**Size-first pre-filter (hash only same-size files) -- PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse -File | Group-Object Length |
  Where-Object { $_.Count -gt 1 } | ForEach-Object { $_.Group } |
  ForEach-Object { [PSCustomObject]@{
    Hash = (Get-FileHash $_.FullName -Algorithm MD5).Hash; Path = $_.FullName
  }}
```

## Symlink and Junction Detection

**PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse -Force |
  Where-Object { $_.Attributes -match 'ReparsePoint' } |
  Select-Object FullName, LinkType, Target
```
**Bash:** `find . -type l -printf '%p -> %l\n'`

**Python (cross-platform):**
```python
import os
for root, dirs, files in os.walk('.'):
    for name in dirs + files:
        path = os.path.join(root, name)
        if os.path.islink(path):
            print(f"SYMLINK: {path} -> {os.readlink(path)}")
```

## Path and Character Safety

**Paths exceeding Windows MAX_PATH (260) -- PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse |
  Where-Object { $_.FullName.Length -gt 250 } |
  Select-Object @{N='Len';E={$_.FullName.Length}}, FullName
```

**Files with reserved characters -- PowerShell:**
```powershell
Get-ChildItem -Path . -Recurse |
  Where-Object { $_.Name -match '[<>:"|?*]' } | Select-Object FullName
```

**Case-conflict detection -- Python (cross-platform):**
```python
from collections import defaultdict
import os
names = defaultdict(list)
for root, dirs, files in os.walk('.'):
    for name in files:
        names[os.path.join(root, name.lower())].append(os.path.join(root, name))
for key, paths in names.items():
    if len(paths) > 1:
        print(f"CASE CONFLICT: {paths}")
```
