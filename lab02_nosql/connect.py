#!/usr/bin/env python3
"""Kết nối MongoDB Atlas cho LAB 02 — đúng mẫu trong đề PDF mục 5.

    python3 connect.py            # hỏi URI bằng getpass (ký tự không hiển thị)

URI đầy đủ dạng:

    mongodb+srv://student_lab:<db_password>@dscluster.xxxxx.mongodb.net/?retryWrites=true&w=majority

Lưu ý:
- Không ghi URI/mật khẩu vào file, ảnh chụp hay commit.
- Mật khẩu chứa ký tự đặc biệt (`@ % / :`) phải URL-encode (ví dụ `@` → `%40`).
- Biến môi trường `MONGO_URI` được ưu tiên nếu có (dùng cho CI); không đọc từ file trong repo.
- Timeout → kiểm tra IP Cloud Shell đã allowlist, DNS, trạng thái cluster.
- AuthenticationFailed → kiểm tra user/password (hoặc URL-encode).
"""

from __future__ import annotations

import os
import sys
from getpass import getpass

import utf8_console  # noqa: F401 - bật UTF-8 cho Windows

from pymongo import MongoClient
from pymongo.errors import ConfigurationError, OperationFailure, ServerSelectionTimeoutError

DB_NAME = "sales_nosql"
TIMEOUT_MS = 12000


def _prompt_uri() -> str:
    uri = os.environ.get("MONGO_URI")
    if uri:
        return uri.strip()
    return getpass("Paste complete Atlas URI: ").strip()


def get_client(uri: str | None = None) -> MongoClient:
    """Tạo client và ping để chắc chắn cluster trả lời."""
    uri = uri or _prompt_uri()
    if not uri:
        raise SystemExit("Chưa nhập URI. Dán URI mongodb+srv://... của cluster Atlas.")
    client = MongoClient(uri, serverSelectionTimeoutMS=TIMEOUT_MS)
    try:
        client.admin.command("ping")
    except ServerSelectionTimeoutError:
        client.close()
        raise SystemExit(
            "Không kết nối được cluster (timeout). Kiểm tra:\n"
            "  1. IP Cloud Shell đã thêm ở Atlas → Security → Network Access chưa\n"
            "     (curl -4 https://api.ipify.org);\n"
            "  2. cluster đang Running và tên host trong URI đúng;\n"
            "  3. mạng cho phép cổng 27017 / DNS SRV."
        )
    except OperationFailure as exc:
        client.close()
        raise SystemExit(
            f"Kết nối tới cluster được nhưng xác thực thất bại: {exc}\n"
            "  Kiểm tra user student_lab, mật khẩu và URL-encode ký tự đặc biệt."
        )
    except ConfigurationError as exc:
        client.close()
        raise SystemExit(f"URI không hợp lệ: {exc}")
    return client


def get_database(uri: str | None = None):
    """Trả về database `sales_nosql` sau khi ping thành công (giống đề)."""
    client = get_client(uri)
    print("Connected successfully")
    return client[DB_NAME]


def main() -> int:
    client = get_client()
    try:
        db = client[DB_NAME]
        print("Database:", db.name)
        print("Collections:", sorted(db.list_collection_names()) or "(rỗng)")
        print("Số document:", {c: db[c].count_documents({})
                               for c in ("customers", "products", "orders")})
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
