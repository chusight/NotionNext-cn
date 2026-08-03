# 用 DPAPI (CurrentUser) 解密 GitHub Desktop 凭据
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
[CredUtil]::CredFree($ptr)

Add-Type -AssemblyName System.Security
# DPAPI 解密 (CurrentUser scope)
$decrypted = [System.Security.Cryptography.ProtectedData]::Unprotect(
    $blob, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
$text = [System.Text.Encoding]::UTF8.GetString($decrypted).TrimEnd("`0")
if (-not $text) { $text = [System.Text.Encoding]::Unicode.GetString($decrypted).TrimEnd("`0") }
Write-Output "DECRYPTED: $text"
