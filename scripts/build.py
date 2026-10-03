#!/usr/bin/env python3
"""从 rules/claude.list 生成各客户端格式的规则文件到 dist/。

用法：python3 scripts/build.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "rules" / "claude.list"
DIST = ROOT / "dist"

ALLOWED_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}
RAW_BASE = "https://raw.githubusercontent.com/windery/claude-proxy-rules/main/dist"
HEADER = "# 由 scripts/build.py 自动生成，请修改 rules/claude.list 后重新生成\n"


def load_rules():
    rules = []
    for lineno, line in enumerate(SRC.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        # 源文件不带策略组，只允许「类型,值」两段
        if len(parts) != 2 or parts[0] not in ALLOWED_TYPES or not parts[1]:
            raise SystemExit(f"{SRC.name}:{lineno} 格式不对：{line}")
        rules.append(f"{parts[0]},{parts[1].lower()}")
    if len(rules) != len(set(rules)):
        raise SystemExit("存在重复规则")
    return rules


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    rules = load_rules()
    lines = "\n".join(rules) + "\n"

    # mihomo / Clash rule-provider：classical yaml
    write(DIST / "clash" / "claude.yaml",
          HEADER + "payload:\n" + "".join(f"  - {r}\n" for r in rules))
    # mihomo / Clash rule-provider：classical text
    write(DIST / "clash" / "claude.txt", HEADER + lines)
    # Surge / Loon / Shadowrocket / Quantumult X(需开启解析器) 通用 list
    write(DIST / "surge" / "claude.list", HEADER + lines)

    # Clash Verge Rev「全局扩展覆写配置 / Merge」片段：引用远程规则集
    write(DIST / "clash-verge" / "merge.yaml", HEADER +
          "# 把 PROXY 换成你配置里实际的策略组名，如「🤖 AI」\n"
          "rule-providers:\n"
          "  claude:\n"
          "    type: http\n"
          "    behavior: classical\n"
          "    format: yaml\n"
          f"    url: {RAW_BASE}/clash/claude.yaml\n"
          "    path: ./ruleset/claude.yaml\n"
          "    interval: 86400\n"
          "prepend-rules:\n"
          "  - RULE-SET,claude,PROXY\n")
    # Clash Verge Rev 订阅「规则」增强：直接内联的写法，不依赖远程拉取
    write(DIST / "clash-verge" / "prepend-rules.yaml", HEADER +
          "# 把 PROXY 换成你配置里实际的策略组名，如「🤖 AI」\n"
          "prepend:\n" + "".join(f"  - {r},PROXY\n" for r in rules) +
          "\nappend: []\n\ndelete: []\n")

    print(f"已生成 {len(rules)} 条规则 → {DIST.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
