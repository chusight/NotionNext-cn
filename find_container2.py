import re
html = open('out/idea.html', encoding='utf-8').read()
# 找到第一个 notion-asset-wrapper-image
idx = html.find('notion-asset-wrapper-image')
# 往回找最近的 <main 或 article 包裹
pre = html[:idx]
# 找最近的3个开始标签及其类
tags = re.findall(r'<(main|article|div|section)[^>]*>', pre)
print("figure 前的最近容器标签:")
for t in tags[-6:]:
    cls = re.search(r'class="([^"]*)"', t)
    print("  ", t[:20], "->", (cls.group(1)[:80] if cls else "no class"))
