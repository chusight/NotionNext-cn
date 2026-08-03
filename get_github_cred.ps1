# 从 Windows 凭据管理器提取 GitHub token
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Security.Credentials.PasswordVault, Windows.Security.Credentials, ContentType=WindowsRuntime]
$vault = New-Object Windows.Security.Credentials.PasswordVault
try {
    $items = $vault.RetrieveAll()
    foreach ($item in $items) {
        if ($item.Resource -like '*github*') {
            $cred = $vault.Retrieve($item.Resource, $item.UserName)
            Write-Output "RESOURCE: $($item.Resource)"
            Write-Output "USER: $($item.UserName)"
            Write-Output "PASSWORD: $($cred.Password)"
        }
    }
} catch {
    Write-Output "ERR: $_"
}
