"""
モデルプリロード用ワーカー (サブプロセスで実行)

指定されたパラメータでWhisperModelの初期化のみを行い、即終了する。
成功時はexit code 0、失敗時は1を返す。
"""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute_type", default="int8")
    parser.add_argument("--cpu_threads", type=int, default=None)
    parser.add_argument("--num_workers", type=int, default=1)
    args = parser.parse_args()

    # 完全オフライン環境変数
    os.environ['no_proxy'] = '*'
    os.environ['NO_PROXY'] = '*'
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''

    try:
        from faster_whisper import WhisperModel

        kwargs = {
            "model_size_or_path": args.model_path,
            "device": args.device,
            "compute_type": args.compute_type,
            "download_root": None,
            "local_files_only": True,
        }
        if args.cpu_threads is not None:
            kwargs["cpu_threads"] = max(1, int(args.cpu_threads))
        kwargs["num_workers"] = max(1, int(args.num_workers))

        # モデル初期化のみ行う（保持しない）
        model = WhisperModel(**kwargs)
        # メタ情報を可能なら返す（失敗しても致命ではない）
        info = {
            "ok": True,
            "device": args.device,
            "compute_type": args.compute_type,
        }
        print(json.dumps(info), flush=True)
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

