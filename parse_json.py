"""
用于解析 JSON 文件，并生成结构化的 Markdown 文件，便于 AI 阅读与分析。
"""

import json
import sys
import logging
from pathlib import Path
from typing import Any, Optional

from config import SAVE_PATH, url_map


def load_json_files(save_path: str, file_map: dict[str, str]) -> dict[str, Any]:
    """
    读取配置中的所有 JSON 文件到内存并返回。

    参数：
    - save_path: JSON 文件所在目录路径。
    - file_map: 键到 URL 的映射（仅使用键来定位 JSON 文件）。

    返回：
    - 一个字典，键为文件前缀名称，值为对应的 JSON 内容。

    异常：
    - FileNotFoundError：当任意必须的 JSON 文件缺失时抛出。
    """
    base = Path(save_path)
    if not base.exists():
        raise FileNotFoundError(f"目录不存在：{base}")

    data: dict[str, Any] = {}
    for filename in file_map.keys():
        file_path = base / f"{filename}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"JSON 文件缺失：{file_path}")
        with file_path.open("r", encoding="utf-8") as f:
            data[filename] = json.load(f)
    return data


def get_text_content(data: dict[str, Any], text_key: str, real_id: Any) -> Optional[str]:
    """
    根据 real_id 从文本 JSON 中取出内容。

    参数：
    - data: 已加载的所有 JSON 数据字典。
    - text_key: 文本 JSON 的键名，例如 'ugc_tutoria_text'。
    - real_id: 对应目录项中的 real_id。

    返回：
    - 找到则返回字符串内容；找不到或结构不符时返回 None。
    """
    text_store = data.get(text_key)
    if isinstance(text_store, dict):
        value = text_store.get(real_id)
        if isinstance(value, str):
            return value
        if value is None:
            return None
        return str(value)
    return None


def count_text_length(text: str, exclude_whitespace: bool = True) -> int:
    """
    计算文本的字数（字符数）。

    参数：
    - text: 待统计的文本内容。
    - exclude_whitespace: 是否排除空白字符（空格、制表符、换行等）。

    返回：
    - 字符数，若排除空白则不计入所有空白字符。
    """
    if exclude_whitespace:
        return sum(1 for ch in text if not ch.isspace())
    return len(text)


def count_file_length(file_path: Path, exclude_whitespace: bool = True) -> int:
    """
    读取文件并统计字数（字符数）。

    参数：
    - file_path: 文件路径。
    - exclude_whitespace: 是否排除空白字符。

    返回：
    - 文件内容的字符数；若文件不存在则返回 0 并记录日志。
    """
    try:
        with file_path.open("r", encoding="utf-8") as fh:
            return count_text_length(fh.read(), exclude_whitespace)
    except FileNotFoundError:
        logging.warning(f"文件不存在：{file_path}")
        return 0


def write_catalog_markdown(
    data: dict[str, Any], catalog_key: str, text_key: str, output_dir: str
) -> int:
    """
    将目录 JSON（包含层级与 real_id）与文本 JSON 整理为 Markdown 文件。

    参数：
    - data: 已加载的所有 JSON 数据字典。
    - catalog_key: 目录 JSON 的键名，例如 'ugc_tutoria_catelog'。
    - text_key: 文本 JSON 的键名，例如 'ugc_tutoria_text'。
    - output_dir: 输出 Markdown 文件的目录。

    返回：
    - 成功返回 0，失败（例如结构缺失）返回 1。
    """
    catalog_items = data.get(catalog_key)
    if not isinstance(catalog_items, list):
        logging.error(f"{catalog_key} 结构不正确或不存在")
        return 1

    out_path = Path(output_dir) / f"{catalog_key}.md"
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write(f"# {catalog_key}\n\n")

        def write_items(items: list[dict[str, Any]]) -> None:
            """
            递归写入目录项到 Markdown 文件。

            参数：
            - items: 当前层级的目录项列表。
            """
            for item in items:
                title = item.get("title", "")
                fh.write(f"### {title}\n")
                real_id = item.get("real_id")
                if real_id is not None:
                    content = get_text_content(data, text_key, real_id)
                    if content:
                        fh.write(f"{content}\n\n")
                    else:
                        # logging.warning(f"{real_id} 在 {text_key} 中不存在或为空")
                        pass
                children = item.get("children")
                if isinstance(children, list) and children:
                    write_items(children)

        for item in catalog_items:
            title = item.get("title", "")
            fh.write(f"## {title}\n")
            real_id = item.get("real_id")
            if real_id is not None:
                content = get_text_content(data, text_key, real_id)
                if content:
                    fh.write(f"{content}\n\n")
                else:
                    pass
                    # logging.warning(f"{real_id} 在 {text_key} 中不存在或为空")
            children = item.get("children")
            if isinstance(children, list) and children:
                write_items(children)

    return 0


def main() -> int:
    """
    脚本入口：加载 JSON 并生成 Markdown 文件。

    返回：
    - 进程返回码，成功为 0，失败为 1。
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        data = load_json_files(SAVE_PATH, url_map)
    except FileNotFoundError as e:
        logging.error(str(e))
        return 1

    codes: list[int] = []
    for catalog in ["ugc_tutoria_catelog", "course_catelog"]:
        text_key = catalog.replace("_catelog", "_text")
        logging.info(f"生成 {catalog}.md")
        code = write_catalog_markdown(data, catalog, text_key, SAVE_PATH)
        codes.append(code)

        # 统计字数并输出到控制台
        md_path = Path(SAVE_PATH) / f"{catalog}.md"
        count = count_file_length(md_path, exclude_whitespace=True)
        logging.info(f"{catalog}.md 字数统计：{count}")

    return 0 if all(code == 0 for code in codes) else 1


if __name__ == "__main__":
    sys.exit(main())
