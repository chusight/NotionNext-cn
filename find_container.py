import re
html = open('out/idea.html', encoding='utf-8').read()
m = re.search(r'<figure class="notion-asset-wrapper', html)
if m:
    start = max(0, m.start() - 800)
    seg = html[start:m.start() + 80]
    # 提取所有 class
    classes = re.findall(r'class="([^"]+)"', seg)
    print("figure 附近容器类名:")
    for c in classes[-6:]:
        print("  ", c[:100])
