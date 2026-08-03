# 完整 CREDENTIAL 结构读取 GitHub token (v2 - 修正 using 位置)
$ErrorActionPreference = "Stop"
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
public struct CREDENTIAL {
    public uint Flags;
    public uint Type;
    public IntPtr TargetName;
    public IntPtr Comment;
    public long LastWritten;
    public uint CredentialBlobSize;
    public IntPtr CredentialBlob;
    public uint Persist;
    public uint AttributeCount;
    public IntPtr Attributes;
    public IntPtr TargetAlias;
    public IntPtr UserName;
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
if (-not $ok) {
    $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
    Write-Output "CredRead 失败 code=$err"
    exit 1
}
$cred = [System.Runtime.InteropServices.Marshal]::PtrToStructure($ptr, [type][CREDENTIAL])
$user = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($cred.UserName)
$blobSize = [int]$cred.CredentialBlobSize
$blob = New-Object byte[] $blobSize
[System.Runtime.InteropServices.Marshal]::Copy($cred.CredentialBlob, $blob, 0, $blobSize)
$pass = [System.Text.Encoding]::Unicode.GetString($blob).TrimEnd("`0")
Write-Output "USER: $user"
Write-Output "TOKEN: $pass"
[CredUtil]::CredFree($ptr)
