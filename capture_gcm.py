# 捕获 git credential manager 输出的 token
# 通过 fake credential helper 链截获 GCM 的输出
import subprocess, sys, os

# 让 git 调用 GCM，然后我们用自定义 helper 接收
# 方法：设置 credential.helper 为一个脚本，它调用真正的 manager 并保存输出
helper_script = r'''#!/bin/bash
# 调用真正的 GCM (manager) 并捕获输出
output=$(git-credential-manager get 2>/dev/null || git credential-manager get 2>/dev/null)
echo "$output" > /tmp/gcm_output.txt
echo "$output"
'''

# 写 helper
with open('/tmp/gcm_helper.sh', 'w') as f:
    f.write(helper_script)

print("helper 已写。尝试触发 git credential fill...")
# 用这个 helper 跑 credential fill
env = dict(os.environ)
env['GIT_TERMINAL_PROMPT'] = '0'
cmd = ['git', '-c', 'credential.helper=/tmp/gcm_helper.sh', 'credential', 'fill']
p = subprocess.run(cmd, input='protocol=https\nhost=github.com\n\n', capture_output=True, text=True, timeout=25, env=env)
print("stdout:", p.stdout[:200])
print("stderr:", p.stderr[:200])
if os.path.exists('/tmp/gcm_output.txt'):
    data = open('/tmp/gcm_output.txt').read()
    print("\nGCM 输出捕获:")
    import re
    for line in data.splitlines():
        if line.startswith('password='):
            print('password=<hidden len=%d>' % len(line.split('=',1)[1]))
        elif line.startswith('username='):
            print(line)
        else:
            print(line[:80])
