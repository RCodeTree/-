import logging
import os
import time

import requests

log = logging.getLogger("upload")

DEFAULT_API_URL = os.environ.get("PROBE_API_URL", "")
API_TOKEN = os.environ.get("PROBE_API_TOKEN", "")


def upload(results, api_url=None, token=None, retries=3, backoff=1.0, timeout=5):
    """把探活结果 POST 到服务端，带指数退避重试。
    4xx 客户端错误不重试，5xx/网络错误重试。返回是否成功（尽力而为）。
    """
    api_url = api_url or DEFAULT_API_URL
    token = token or API_TOKEN

    if not api_url:
        log.info("未配置 PROBE_API_URL，跳过上报")
        return False

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(api_url, json=results, headers=headers, timeout=timeout)
            resp.raise_for_status()
            log.info("上报成功: %s (第 %d 次尝试)", api_url, attempt)
            return True
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status is not None and 400 <= status < 500:
                log.error("上报被拒绝(4xx=%s)，不重试", status)
                return False
            log.warning("上报失败(5xx=%s)，第 %d 次尝试", status, attempt)
        except requests.exceptions.RequestException as e:
            log.warning("上报网络错误(%s)，第 %d 次尝试", type(e).__name__, attempt)

        if attempt < retries:
            sleep = backoff * (2 ** (attempt - 1))  # 1s, 2s, 4s...
            log.debug("退避 %.1fs 后重试", sleep)
            time.sleep(sleep)

    log.error("上报最终失败(已重试 %d 次)", retries)
    return False
