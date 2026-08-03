# 提取干净的 GitHub token 并写入临时文件
$ErrorActionPreference = "Stop"
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
public struct CREDENTIAL {
    public uint Flags; public uint Type; public IntPtr TargetName; public IntPtr Comment;
    public long LastWritten; public uint CredentialBlobSize; public IntPtr CredentialBlob;
    public uint Persist; public uint AttributeCount; public IntPtr Attributes;
    public IntPtr TargetAlias; public IntPtr UserName;
}
public static class CredUtil {
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool CredRead(string target, int type, int reservedFlag, out IntPtr credentialPtr);
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern void CredFree(IntPtr cred);
}
'@

$target = "GitHub - https://api.github.com/chusight"
$ptr = [IntPtr]::Zero
$ok = [CredUtil]::CredRead($target, 1, 0, [ref]$ptr)
if (-not $ok) { Write-Output "FAIL"; exit 1 }
$cred = [System.Runtime.InteropServices.Marshal]::PtrToStructure($ptr, [type][CREDENTIAL])
$blobSize = [int]$cred.CredentialBlobSize
$blob = New-Object byte[] $blobSize
[System.Runtime.InteropServices.Marshal]::Copy($cred.CredentialBlob, $blob, 0, $blobSize)
# GitHub Desktop 的 token 是 ASCII 文本（不是 UTF-16），尝试多种解码取最长可打印串
$ascii = [System.Text.Encoding]::ASCII.GetString($blob)
$utf16 = [System.Text.Encoding]::Unicode.GetString($blob).TrimEnd("`0")
# 选取包含 gho_/ghp_/gho 的串
$candidates = @($ascii, $utf16)
$best = ""
foreach ($c in $candidates) {
    $m = [regex]::Match($c, 'gh[pousr]_[A-Za-z0-9]+')
    if ($m.Success -and $m.Value.Length -gt $best.Length) { $best = $m.Value }
    # 也尝试纯可打印长串
    $printable = [regex]::Match($c, '[\x20-\x7E]{20,}')
    if ($printable.Success -and $printable.Value.Length -gt $best.Length) { $best = $printable.Value }
}
if ($best) {
    Write-Output "TOKEN_OK length=$($best.Length)"
    $best | Out-File -FilePath "$env:TEMP\gh_token.txt" -Encoding ascii -NoNewline
} else {
    Write-Output "NO_TOKEN_FOUND"
    Write-Output "ASCII: $ascii"
}
[CredUtil]::CredFree($ptr)
