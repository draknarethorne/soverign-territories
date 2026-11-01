param(
    [Parameter(Mandatory=$true)][ValidateSet("inspect", "recycle", "recover")][string]$Action,
    [Parameter(Mandatory=$true)][string]$Target,
    [string]$Identity
)
$ErrorActionPreference = "Stop"

function Canonical([string]$Path) {
    if ($Path.StartsWith("\\?\") -or $Path.StartsWith("\\")) {
        throw "Only ordinary local absolute paths are accepted"
    }
    if (-not [IO.Path]::IsPathRooted($Path) -or $Path -match '(^|\\)\.\.(\\|$)') {
        throw "Explicit absolute path without traversal required"
    }
    return [IO.Path]::GetFullPath($Path).TrimEnd("\")
}

$Target = Canonical $Target
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$allowed = Join-Path $repo "tmp\retire-proof"
if (-not $Target.StartsWith($allowed + "\", [StringComparison]::OrdinalIgnoreCase) -or
    ([IO.DirectoryInfo]$Target).Parent.Name -ne "snapshots") {
    throw "Only bounded generated sample snapshots are accepted"
}
foreach ($part in @($Target, $allowed)) {
    $current = $part
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -Force -LiteralPath $current
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Reparse path refused"
            }
        }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent) { break }
        $current = $parent.FullName
    }
}
$drive = New-Object IO.DriveInfo ([IO.Path]::GetPathRoot($Target))
if ($drive.DriveType -ne [IO.DriveType]::Fixed -or $drive.DriveFormat -ne "NTFS") {
    throw "Only local fixed NTFS recycle-capable volumes are accepted; no fallback"
}

$shell = New-Object -ComObject Shell.Application
$bin = $shell.Namespace(10)
if ($null -eq $bin) { throw "Recycle Bin Shell namespace unavailable" }

function Find-Exact {
    $matches = @()
    foreach ($item in $bin.Items()) {
        $path = [string]$item.Path
        if (-not $path -or ([IO.Path]::GetFileName($path)) -notlike '$R*') { continue }
        $meta = Join-Path ([IO.Path]::GetDirectoryName($path)) (
            '$I' + ([IO.Path]::GetFileName($path)).Substring(2))
        # Raw $I original path avoids display-name localization and hidden extensions.
        if (-not [IO.File]::Exists($meta)) { continue }
        $bytes = [IO.File]::ReadAllBytes($meta)
        if ($bytes.Length -lt 28 -or $bytes.Length -gt 131072) { continue }
        $version = [BitConverter]::ToInt64($bytes, 0)
        if ($version -eq 2) {
            $chars = [BitConverter]::ToUInt32($bytes, 24)
            if ($chars -gt 32768 -or 28 + 2 * $chars -gt $bytes.Length) { continue }
            $original = [Text.Encoding]::Unicode.GetString($bytes, 28, 2 * $chars).TrimEnd([char]0)
        } elseif ($version -eq 1 -and $bytes.Length -ge 544) {
            $original = [Text.Encoding]::Unicode.GetString($bytes, 24, 520).TrimEnd([char]0)
        } else { continue }
        try { $original = Canonical $original } catch { continue }
        if (-not $original.Equals($Target, [StringComparison]::OrdinalIgnoreCase)) { continue }
        if (-not [IO.Directory]::Exists($path)) { throw "Matching recycled item is not a directory" }
        $deletedFrom = [string]$item.ExtendedProperty("System.Recycle.DeletedFrom")
        if ($deletedFrom -and -not (Canonical $deletedFrom).Equals(
                [IO.Path]::GetDirectoryName($Target), [StringComparison]::OrdinalIgnoreCase)) {
            throw "Shell original directory disagrees with raw Recycle Bin identity"
        }
        $hash = [Security.Cryptography.SHA256]::Create()
        try {
            $digest = [BitConverter]::ToString($hash.ComputeHash($bytes)).Replace("-", "").ToLowerInvariant()
        } finally { $hash.Dispose() }
        $matches += @{
            item = $item
            identity = @{
                originalPath = $original
                itemPath = $path
                metadataPath = $meta
                metadataSha256 = $digest
                deletedFileTime = ([BitConverter]::ToInt64($bytes, 16)).ToString()
            }
        }
    }
    if ($matches.Count -gt 1) { throw "Ambiguous duplicate original paths in Recycle Bin" }
    if ($matches.Count -eq 1) { return $matches[0] }
    return $null
}

$found = Find-Exact
if ($Identity -and $found -and -not $found.identity.itemPath.Equals(
        $Identity, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Wrong recycled identity"
}
if ($Action -eq "inspect") {
    $value = $null
    if ($found) { $value = $found.identity }
    @{ identity = $value } | ConvertTo-Json -Compress -Depth 5
    exit 0
}
if ($Action -eq "recover") {
    if (-not $Identity -or -not $found) { throw "Exact recycled identity is required" }
    if (Test-Path -LiteralPath $Target) { throw "Recovery destination already exists" }
    # Canonical, nonlocalized Shell verb. Never synthesize a replacement from the archive.
    $found.item.InvokeVerb("undelete")
    $deadline = [DateTime]::UtcNow.AddSeconds(45)
    do {
        Start-Sleep -Milliseconds 100
        $remaining = Find-Exact
        if ([IO.Directory]::Exists($Target) -and -not $remaining) {
            @{ restored = $true; identity = $found.identity } | ConvertTo-Json -Compress -Depth 5
            exit 0
        }
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "Shell undelete did not complete within bounded wait"
}
if ($found) { throw "Preexisting recycled identity; refuse ambiguous new recycle" }
if (-not [IO.Directory]::Exists($Target)) { throw "Source directory does not exist" }

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

[ComImport, Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IShellItem {
    void BindToHandler(IntPtr pbc, ref Guid bhid, ref Guid riid, out IntPtr ppv);
    void GetParent(out IShellItem parent);
    void GetDisplayName(uint sigdnName, out IntPtr name);
    void GetAttributes(uint mask, out uint attributes);
    void Compare(IShellItem other, uint hint, out int order);
}
[ComImport, Guid("947AAB5F-0A5C-4C13-B4D6-4BF7836FC9F8"),
 InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IFileOperation {
    void Advise(IntPtr sink, out uint cookie);
    void Unadvise(uint cookie);
    void SetOperationFlags(uint flags);
    void SetProgressMessage([MarshalAs(UnmanagedType.LPWStr)] string message);
    void SetProgressDialog(IntPtr dialog);
    void SetProperties(IntPtr properties);
    void SetOwnerWindow(IntPtr owner);
    void ApplyPropertiesToItem(IShellItem item);
    void ApplyPropertiesToItems(IntPtr items);
    void RenameItem(IShellItem item, [MarshalAs(UnmanagedType.LPWStr)] string name, IntPtr sink);
    void RenameItems(IntPtr items, [MarshalAs(UnmanagedType.LPWStr)] string name);
    void MoveItem(IShellItem item, IShellItem destination, [MarshalAs(UnmanagedType.LPWStr)] string name, IntPtr sink);
    void MoveItems(IntPtr items, IShellItem destination);
    void CopyItem(IShellItem item, IShellItem destination, [MarshalAs(UnmanagedType.LPWStr)] string name, IntPtr sink);
    void CopyItems(IntPtr items, IShellItem destination);
    void DeleteItem(IShellItem item, IntPtr sink);
    void DeleteItems(IntPtr items);
    void NewItem(IShellItem destination, uint attributes, [MarshalAs(UnmanagedType.LPWStr)] string name,
                 [MarshalAs(UnmanagedType.LPWStr)] string template, IntPtr sink);
    void PerformOperations();
    void GetAnyOperationsAborted([MarshalAs(UnmanagedType.Bool)] out bool aborted);
}
public static class RecycleOnly {
    [DllImport("shell32.dll", CharSet=CharSet.Unicode, PreserveSig=false)]
    static extern void SHCreateItemFromParsingName(string path, IntPtr context,
        ref Guid iid, [MarshalAs(UnmanagedType.Interface)] out IShellItem item);
    [STAThread]
    public static void Move(string path) {
        object instance = Activator.CreateInstance(Type.GetTypeFromCLSID(
            new Guid("3AD05575-8857-4850-9277-11B85BDB8E09")));
        IShellItem item = null;
        try {
            var operation = (IFileOperation)instance;
            // SILENT | NOCONFIRMATION | NOERRORUI | RECYCLEONDELETE | EARLYFAILURE.
            // Deliberately no permanent-delete API or fallback implementation.
            operation.SetOperationFlags(0x00000414u | 0x00080000u | 0x00100000u);
            Guid iid = new Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE");
            SHCreateItemFromParsingName(path, IntPtr.Zero, ref iid, out item);
            operation.DeleteItem(item, IntPtr.Zero);
            operation.PerformOperations();
            bool aborted;
            operation.GetAnyOperationsAborted(out aborted);
            if (aborted) throw new InvalidOperationException("Recycle operation aborted; no fallback");
        } finally {
            if (item != null) Marshal.FinalReleaseComObject(item);
            Marshal.FinalReleaseComObject(instance);
        }
    }
}
'@
[RecycleOnly]::Move($Target)
$deadline = [DateTime]::UtcNow.AddSeconds(45)
do {
    Start-Sleep -Milliseconds 100
    $found = Find-Exact
    if (-not [IO.Directory]::Exists($Target) -and $found) {
        @{ recycled = $true; identity = $found.identity } | ConvertTo-Json -Compress -Depth 5
        exit 0
    }
} while ([DateTime]::UtcNow -lt $deadline)
throw "Recycle operation did not yield an actual unique recycled identity; no fallback"
