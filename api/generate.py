"""
Vercel Serverless Function — 新闻 HTML 日报生成 API

端点: GET /api/generate?limit=20&timeout=15&retries=2
返回: JSON { "success": true, "html": "...", "generated_at": "..." }
      或 JSON { "success": false, "error": "..." }
"""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta

# 将 scripts 目录加入 sys.path，以便导入 generate_news_html
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

BEIJING_TZ = timezone(timedelta(hours=8), "Asia/Shanghai")


def build_response(handler, status_code, body_dict):
    """构造 JSON 响应"""
    payload = json.dumps(body_dict, ensure_ascii=False, indent=2)
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(payload.encode("utf-8"))


def parse_int(value, default):
    try:
        return int(value[0]) if value else default
    except (ValueError, TypeError):
        return default


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api/generate":
            self._handle_generate(parsed)
        elif path == "/api/health":
            build_response(self, 200, {
                "status": "ok",
                "time": datetime.now(BEIJING_TZ).isoformat()
            })
        else:
            build_response(self, 404, {"error": "not found", "path": path})

    def _handle_generate(self, parsed):
        try:
            qs = parse_qs(parsed.query)
            limit = max(10, min(20, parse_int(qs.get("limit"), 20)))
            timeout = max(5, min(30, parse_int(qs.get("timeout"), 15)))
            retries = max(0, min(5, parse_int(qs.get("retries"), 2)))

            # 动态导入 generate_report
            from generate_news_html import generate_report

            # 构造简易 args 对象
            class Args:
                pass

            args = Args()
            args.limit = limit
            args.timeout = timeout
            args.retries = retries
            args.paper_node_id = "25950"
            args.screenshot = False
            args.screenshot_width = 920
            args.screenshot_height = 60000
            args.screenshot_timeout = 60

            generated_at = datetime.now(BEIJING_TZ)

            # 调用核心生成逻辑 — 直接生成 HTML 字符串
            html_text, ok_count, total_count, source_details = self._run_generate(
                args, generated_at
            )

            build_response(self, 200, {
                "success": True,
                "generated_at": generated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "source_count": ok_count,
                "total_sources": total_count,
                "sources": source_details,
                "html": html_text,
            })

        except Exception:
            build_response(self, 500, {
                "success": False,
                "error": traceback.format_exc(),
            })

    def _run_generate(self, args, generated_at):
        """调用 generate_news_html 中的各个 fetch 函数并渲染 HTML"""
        from generate_news_html import (
            render_news_card_html,
            parse_jinzanzan_gold_price,
            parse_60s,
            parse_weibo,
            parse_zhihu,
            parse_douyin_hot,
            parse_tencent,
            parse_thepaper,
            parse_eastmoney_stock_news,
            parse_bilibili_hot_search,
            parse_bilibili_popular,
            parse_ithome,
            parse_sspai,
            parse_juejin,
            parse_baidu_hot,
            parse_toutiao_hot,
            parse_hackernews,
            parse_cankaoxiaoxi,
            parse_solidot,
            parse_cls_hot,
            parse_cls_telegraph,
        )

        results = [
            parse_jinzanzan_gold_price(args.timeout, args.retries),
            parse_60s(args.limit, args.timeout, args.retries),
            parse_weibo(args.limit, args.timeout, args.retries),
            parse_zhihu(args.limit, args.timeout, args.retries),
            parse_douyin_hot(args.limit, args.timeout, args.retries),
            parse_tencent(args.limit, args.timeout, args.retries),
            parse_thepaper(args.limit, args.timeout, args.retries, args.paper_node_id),
            parse_eastmoney_stock_news(args.limit, args.timeout, args.retries),
            parse_bilibili_hot_search(args.limit, args.timeout, args.retries),
            parse_bilibili_popular(args.limit, args.timeout, args.retries),
            parse_ithome(args.limit, args.timeout, args.retries),
            parse_sspai(args.limit, args.timeout, args.retries),
            parse_juejin(args.limit, args.timeout, args.retries),
            parse_baidu_hot(args.limit, args.timeout, args.retries),
            parse_toutiao_hot(args.limit, args.timeout, args.retries),
            parse_hackernews(args.limit, args.timeout, args.retries),
            parse_cankaoxiaoxi(args.limit, args.timeout, args.retries),
            parse_solidot(args.limit, args.timeout, args.retries),
            parse_cls_hot(args.limit, args.timeout, args.retries),
            parse_cls_telegraph(args.limit, args.timeout, args.retries),
        ]

        html_text = render_news_card_html(results, generated_at)

        ok_count = sum(1 for r in results if r.ok)
        total_count = len(results)
        source_details = [
            {
                "name": r.name,
                "ok": r.ok,
                "count": len(r.items),
                "error": r.error if not r.ok else "",
            }
            for r in results
        ]

        return html_text, ok_count, total_count, source_details

    def log_message(self, format, *args):
        # 静默日志，避免干扰 Vercel 日志系统
        pass
