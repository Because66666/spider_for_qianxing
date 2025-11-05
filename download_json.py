"""
用于下载千星奇遇教程相关的 JSON 文件并持久化到本地。
版权归属米哈游，仅供学习交流使用，请勿用于商业用途。
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import url_map, SAVE_PATH


def build_session(headers: dict[str, str]) -> requests.Session:
    """
    创建并配置带有重试策略的 HTTP 会话。

    参数：
    - headers: 需要设置的请求头字典。

    返回：
    - 配置好的 `requests.Session` 实例。
    """
    session = requests.Session()
    session.headers.update(headers)

    # 配置重试：对 5xx 等状态码进行指数退避重试
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_json(session: requests.Session, url: str, timeout: float = 10.0) -> Optional[Any]:
    """
    发起 GET 请求并以 JSON 格式解析响应。

    参数：
    - session: 已配置好的 `requests.Session`。
    - url: 目标地址。
    - timeout: 请求超时时间（秒）。

    返回：
    - 解析成功返回 JSON 对象（dict/list 等），失败返回 None。
    """
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.JSONDecodeError:
        logging.error(f"响应非 JSON：{url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败：{url} —— {e}")
    return None


def save_json(output_dir: str, name: str, obj: Any) -> None:
    """
    将 JSON 对象以美化格式写入到指定目录的文件中。

    参数：
    - output_dir: 目标目录路径。
    - name: 文件前缀名（不含扩展名）。
    - obj: 待写入的 JSON 对象。
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def download_all(urls: dict[str, str], output_dir: str, sleep_seconds: float = 1.0) -> int:
    """
    下载映射中的所有 JSON 文件并保存到本地。

    参数：
    - urls: 名称到 URL 的映射字典。
    - output_dir: 保存目录。
    - sleep_seconds: 相邻请求之间的间隔，避免过快访问。

    返回：
    - 成功返回 0；若有失败则返回 1。
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "origin": "https://act.mihoyo.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://act.mihoyo.com/",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    }

    session = build_session(headers)
    all_ok = True
    for name, url in urls.items():
        logging.info(f"下载 {name}：{url}")
        data = fetch_json(session, url)
        if data is None:
            logging.error(f"获取 {name} 失败")
            all_ok = False
        else:
            save_json(output_dir, name, data)
            logging.info(f"保存完成：{name}.json")
        time.sleep(sleep_seconds)

    return 0 if all_ok else 1


def main() -> int:
    """
    脚本入口：批量下载并写入 JSON 文件。

    返回：
    - 进程返回码：成功为 0，若存在失败为 1。
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    return download_all(url_map, SAVE_PATH)


if __name__ == "__main__":
    raise SystemExit(main())