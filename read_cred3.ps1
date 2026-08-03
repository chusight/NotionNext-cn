$ErrorActionPreference = "Stop"
try {
    # 读取 GitHub Desktop 凭据: target = GitHub - https://api.github.com/chusight
    $target = "GitHub - https://api.github.com/chusight"
    # 用 cmdkey 无法读密码，用 .NET 的 Credential 读取 (git-credential-manager 的存储)
    # GCM 实际存储位置: %LOCALAPPDATA%\GitHubDesktop\... 或直接读 registry/凭据管理器
    # 方法: 使用 PowerShell 调 advapi32 CredRead
    Add-Type -Namespace Win32 -Name CredUtil -MemberDefinition @'
    [DllImport("advapi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    public static extern bool CredRead(string target, int type, int reservedFlag, out IntPtr credentialPtr);
    [DllImport("advapi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    public static extern void CredFree(IntPtr cred);
'@
    $ptr = [IntPtr]::Zero
    $ok = [Win32.CredUtil]::CredRead($target, 1, 0, [ref]$ptr)
    if ($ok) {
        $cred = [System.Runtime.InteropServices.Marshal]::PtrToStructure($ptr, [type]::GetType("Win32.CREDENTIAL"))
        $user = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($cred.UserName)
        $pass = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($cred.CredentialBlob)
        Write-Output "USER: $user"
        Write-Output "TOKEN: $pass"
        [Win32.CredUtil]::CredFree($ptr)
    } else {
        Write-Output "CredRead 失败, 错误码: $([System.Runtime.InteropServices.Marshal]::GetLastWin32Error())"
        # 尝试类型 2 (domain password)
        $ok2 = [Win32.CredUtil]::CredRead($target, 2, 0, [ref]$ptr)
        if ($ok2) {
            $cred = [System.Runtime.InteropServices.Marshal]::PtrToStructure($ptr, [type]::GetType("Win32.CREDENTIAL"))
            $user = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($cred.UserName)
            $pass = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($cred.CredentialBlob)
            Write-Output "USER2: $user"
            Write-Output "TOKEN2: $pass"
            [Win32.CredUtil]::CredFree($ptr)
        }
    }
} catch {
    Write-Output "ERR: $_"
}
