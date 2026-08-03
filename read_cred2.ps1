# 用 Windows Credential Manager 读取 GitHub 凭据（git 的 manager helper 用的就是这个）
$ErrorActionPreference = "Stop"
try {
    # 方法1: 读 git-credential-manager 存储的通用凭据
    $cred = New-Object System.Net.NetworkCredential
    # 通过 cmdkey 找 target
    $output = cmdkey /list 2>&1 | Out-String
    $targets = [regex]::Matches($output, 'target=([^\r\n]+)') | ForEach-Object { $_.Groups[1].Value.Trim() }
    Write-Output "=== 凭据目标 ==="
    $targets | ForEach-Object { Write-Output "  $_" }
    Write-Output "=== 尝试 git:https://github.com ==="
    # GCM 的存储格式: git:https://github.com
    foreach ($t in $targets) {
        if ($t -match 'github') {
            Write-Output "匹配目标: $t"
        }
    }
} catch {
    Write-Output "ERR: $_"
}
