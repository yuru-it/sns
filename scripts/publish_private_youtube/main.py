#!/usr/bin/env python3
import os
from datetime import datetime, timezone
from typing import List, Dict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CLIENT_ID = os.environ["YT_CLIENT_ID"]
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"]
MAX_VIDEOS = int(os.environ.get("MAX_VIDEOS", "10"))
SKIP_SCHEDULED = os.environ.get("SKIP_SCHEDULED", "true").lower() == "true"
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

def now_utc():
    return datetime.now(timezone.utc)

def parse_rfc3339(s: str) -> datetime:
    # e.g. "2025-08-29T12:34:56Z"
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)

def build_youtube():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube"],
    )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)

def get_uploads_playlist_id(youtube) -> str:
    res = youtube.channels().list(part="contentDetails", mine=True).execute()
    items = res.get("items", [])
    if not items:
        raise RuntimeError("No channel found for the authorized account.")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_latest_video_ids(youtube, uploads_playlist_id: str, limit: int) -> List[str]:
    # uploads プレイリストは新しい順で返る
    res = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=min(limit, 50),
    ).execute()
    items = res.get("items", [])
    return [it["contentDetails"]["videoId"] for it in items][:limit]

def fetch_videos_status(youtube, video_ids: List[str]) -> Dict[str, Dict]:
    if not video_ids:
        return {}
    res = youtube.videos().list(
        part="status,snippet",
        id=",".join(video_ids)
    ).execute()
    out = {}
    for it in res.get("items", []):
        out[it["id"]] = it
    return out

def publish_video(youtube, video):
    vid = video["id"]
    status = video["status"].copy()  # 既存の status を丸ごと取得し、privacyStatus だけ変更
    status["privacyStatus"] = "public"

    if DRY_RUN:
        print(f"[DRY_RUN] would publish: {vid} (title='{video['snippet'].get('title','')}')")
        return

    youtube.videos().update(
        part="status",
        body={
            "id": vid,
            "status": status,
        },
    ).execute()
    print(f"[OK] published: {vid} (title='{video['snippet'].get('title','')}')")

def main():
    try:
        youtube = build_youtube()
        uploads_id = get_uploads_playlist_id(youtube)
        ids = get_latest_video_ids(youtube, uploads_id, MAX_VIDEOS)
        if not ids:
            print("No recent videos found.")
            return

        videos = fetch_videos_status(youtube, ids)
        target_count = 0
        now = now_utc()

        for vid in ids:
            v = videos.get(vid)
            if not v:
                continue
            st = v.get("status", {})
            privacy = st.get("privacyStatus")
            publish_at = st.get("publishAt")

            # 予約公開のスキップ判定
            if SKIP_SCHEDULED and publish_at:
                try:
                    pa = parse_rfc3339(publish_at)
                    if pa > now:
                        print(f"skip (scheduled in future): {vid} publishAt={publish_at}")
                        continue
                except Exception:
                    # 解析失敗時はスキップせず続行
                    pass

            if privacy == "private":
                target_count += 1
                publish_video(youtube, v)
            else:
                print(f"skip (privacy={privacy}): {vid}")

        print(f"done. changed {target_count} video(s).")

    except HttpError as e:
        print(f"HTTP Error: {e}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()