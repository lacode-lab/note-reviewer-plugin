#!/usr/bin/env python3
"""myblog-editor の必須出力ゲート（Stop フック）。

myblog-editor を実行したセッションで、レビューに着手した（対象を Read した）
にもかかわらず `_review/<base>-校閲.md` / `_review/<base>-タイトルとタグ.md` を
Write していない場合に、停止をブロックして生成を強制する。

設計メモ:
- 判定はトランスクリプトの「コマンド起動マーカー以降」に限定する。
  毎回フレッシュな出力を要求するため、過去ターンの生成は数えない。
- 対象未読（確認待ちで停止しただけ）のときはブロックしない。誤爆を避ける。
- stop_hook_active により本フックは1セッションにつき実質1回しか発火しない
  （= ナッジは1回限り）。ファイルが本当に作れない状況でも詰まらない。
- 解析に失敗したら黙って exit 0。ユーザーのセッションを壊さないことを最優先。
"""
import json
import sys

# コマンド本文に埋め込んだ機械可読マーカー（myblog-editor.md と一致させること）
RUN_MARKER = "NOTE_REVIEWER_RUN"

REQUIRED = [
    ("校閲.md", "_review/<元ファイル名>-校閲.md"),
    ("タイトルとタグ.md", "_review/<元ファイル名>-タイトルとタグ.md"),
]
WRITE_TOOLS = ("Write", "Edit", "MultiEdit")


def iter_tool_uses(entry):
    """1トランスクリプト行から tool_use ブロックを取り出す。"""
    msg = entry.get("message")
    if not isinstance(msg, dict):
        return
    content = msg.get("content")
    if not isinstance(content, list):
        return
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            yield block


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return 0

    if data.get("stop_hook_active"):
        return 0

    tpath = data.get("transcript_path")
    if not tpath:
        return 0

    try:
        with open(tpath, encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except Exception:
        return 0

    # 直近の myblog-editor 起動位置を探す
    last_cmd = -1
    for i, e in enumerate(entries):
        try:
            if RUN_MARKER in json.dumps(e, ensure_ascii=False):
                last_cmd = i
        except Exception:
            continue
    if last_cmd < 0:
        return 0  # このセッションは myblog-editor ではない

    tail = entries[last_cmd:]

    # レビューに着手したか（対象を Read したか）を確認。未着手ならブロックしない
    proceeded = any(
        tu.get("name") == "Read" for e in tail for tu in iter_tool_uses(e)
    )
    if not proceeded:
        return 0

    # コマンド起動以降に書き出されたファイルパスを収集
    written = []
    for e in tail:
        for tu in iter_tool_uses(e):
            if tu.get("name") in WRITE_TOOLS:
                fp = (tu.get("input") or {}).get("file_path", "")
                if fp:
                    written.append(fp)

    missing = [
        label for suffix, label in REQUIRED
        if not any(p.endswith(suffix) for p in written)
    ]
    if not missing:
        return 0

    reason = (
        "myblog-editor の必須出力が未生成です。完了する前に Write で次を作成してください: "
        + " / ".join(missing)
        + "。チャットでの代替・省略は不可。"
        + "タイトル案とハッシュタグは必ず _review/ 配下の -タイトルとタグ.md に書き出すこと。"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
