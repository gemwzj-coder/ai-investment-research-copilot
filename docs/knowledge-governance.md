# 知识来源治理与 Wiki 接入边界

## Wiki 不等于维基百科

Wiki 是团队协作维护知识的机制或系统，核心能力是页面组织、版本历史、责任人、审批、链接和权限；维基百科只是最知名的公开 Wiki 网站。投研场景中的 Wiki 通常是公司内部的 Confluence、Notion、语雀或自研知识库。

本项目不声称已接入某个企业 Wiki。它提供一个可审计的来源登记接口：企业 Wiki 的导出文件、受控 PDF/Excel 清洗结果，或后续 API 同步任务，均可登记为同一种 `source`。

## 来源层、索引层与生成层

```text
受控 Wiki / PDF / Excel（事实来源、责任人、版本、权限）
  → 清洗成知识库文本 + source_manifest.json（来源登记）
  → 精确索引 / 向量索引（检索层）
  → 带资料名、数据截止日和版本的引用（生成层）
```

向量库负责“找相近资料”，不应成为事实来源；QA 文本是检索视图，也不应替代原始文档。任何重要数值应能回到资料名、数据截止日、版本和原始链接。

## 本地演示方式

```powershell
Copy-Item knowledge.example.txt knowledge.txt
Copy-Item source_manifest.example.json source_manifest.json
python manage_kb.py rebuild --note "load public wiki-export demo"
python app.py
```

`source_manifest.json` 不应提交真实内部链接、责任人信息或权限策略。公开仓库仅保留 `source_manifest.example.json`。

## 每个来源的最小字段

| 字段 | 用途 |
|---|---|
| `id` | 稳定标识与审计关联 |
| `title` | 回答中显示的资料名称 |
| `source_type` | `wiki_export`、`pdf`、`excel` 等 |
| `source_url` | 可回到原始资料的受控链接 |
| `owner` | 资料责任人 |
| `updated_at` / `data_as_of` | 更新时点与业务数据口径 |
| `access_level` | 文档级权限标签；生产环境必须在检索前校验 |
| `version` | 回滚和引用版本 |
| `file` | 本次清洗后知识库文件名 |

## 生产接入原则

1. 由同步任务或人工审批从 Wiki 读取已授权资料；不要让模型自行抓取网页。
2. 解析后保留原始链接、页码/表格位置、责任人、版本和数据截止日。
3. 权限过滤应在检索前由后端完成，不能只在 Prompt 中要求模型保密。
4. 来源清单变化与知识库正文变化都应触发索引重建、审计和回归评测。
5. 数据冲突、来源过期或字段缺失时，不自动给出确定性结论，转入补库或人工核验。
