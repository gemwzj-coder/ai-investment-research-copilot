"""受控知识来源登记：为 Wiki 导出、PDF/Excel 清洗结果保留可审计元数据。

本模块刻意只依赖标准库。公开 Demo 使用 JSON，是为了让仓库可直接运行；
真实环境可由 Confluence、Notion 或公司 Wiki 的导出/接口任务生成同一份清单。
"""

import json
import os


REQUIRED_FIELDS = {
    "id", "title", "source_type", "source_url", "owner",
    "updated_at", "data_as_of", "access_level", "version", "file",
}


def load_manifest(path: str) -> list[dict]:
    """读取并校验来源清单；不存在时返回空列表，保持旧知识库兼容。"""
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    sources = payload.get("sources", []) if isinstance(payload, dict) else []
    if not isinstance(sources, list):
        raise ValueError("source manifest 的 sources 必须是数组")

    seen_ids = set()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError(f"第 {index} 条来源不是对象")
        missing = REQUIRED_FIELDS - set(source)
        if missing:
            raise ValueError(f"来源 {source.get('id', index)} 缺少字段：{', '.join(sorted(missing))}")
        if source["id"] in seen_ids:
            raise ValueError(f"来源 id 重复：{source['id']}")
        seen_ids.add(source["id"])
    return sources


def source_for_file(knowledge_path: str, manifest_path: str | None = None) -> dict:
    """按知识库文件名匹配来源；一份导出文件仅对应一个已审批来源。"""
    filename = os.path.basename(knowledge_path)
    for source in load_manifest(manifest_path or ""):
        if os.path.basename(str(source["file"])) == filename:
            return dict(source)
    return {}


def provenance_line(source: dict) -> str:
    """写入检索上下文的机器可读来源行，供回答页生成可核验引用。"""
    if not source:
        return ""
    return (
        "【来源元数据】"
        f"资料={source['title']}；数据截至={source['data_as_of']}；"
        f"更新={source['updated_at']}；版本={source['version']}；"
        f"责任人={source['owner']}；权限={source['access_level']}；"
        f"链接={source['source_url']}"
    )


def citation_label(source: dict) -> str:
    """为最终回答构造简洁引用，不暴露不必要的内部字段。"""
    if not source:
        return ""
    return f"{source['title']}｜数据截至：{source['data_as_of']}｜版本：{source['version']}"
