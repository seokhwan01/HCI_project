import csv
import os
from datetime import datetime, timezone

LOG_DIR = "log"

def generate_log_filename():
    """게임 시작 시 새로운 로그 파일을 생성하기 위한 파일명 생성"""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(LOG_DIR, f"log_{timestamp}.csv")


def init_log_file(log_file):
    """해당 게임 전용 로그 파일 최초 생성"""
    with open(log_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "N", "trial", "W", "A",
            "red_start_time",
            "cursor_out_time",
            "explode_time",
            "click_time",
            "success"
        ])


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_log(log_file, N, trial, W, A,
              red_start_time,
              cursor_out_time,
              explode_time,
              click_time,
              success):

    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            N, trial, W, A,
            red_start_time,
            cursor_out_time,
            explode_time,
            click_time,
            success
        ])
