import os
import requests
import json
from typing import Dict, Any

class Notifier:
    """
    Unified notification sender.
    Currently supports: Console, Lark (Feishu) Webhook.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.notification_config = self.config.get('notifications', {})
        
    def send(self, title: str, message: str, level: str = "INFO", key: str = "default"):
        """
        Sends a notification. 
        Uses 'key' (Business Domain) to look up channels in 'notifications.business_domains'.
        """
        # 1. Console (Always)
        color = "32" if level == "INFO" else "31" # Green or Red
        print(f"\n\033[{color}m[{level}] Notification (Domain: {key}): {title}\n{message}\033[0m\n")
        
        # 2. Resolve Target Channels
        channels_cfg = self.notification_config.get('channels', {})
        domains_cfg = self.notification_config.get('business_domains', {})
        default_channels = self.notification_config.get('default_channels', [])
        
        # Lookup Logic: Hierarchical Fallback
        # Key: "marketing.creative" -> ["marketing.creative", "marketing", "default"]
        
        parts = key.split('.')
        potential_keys = []
        
        # Generator: a.b.c -> a.b.c, a.b, a
        for i in range(len(parts), 0, -1):
            potential_keys.append('.'.join(parts[:i]))
        
        potential_keys.append("default") # Always verify default last
        
        target_channel_ids = []
        used_key = None
        
        for k in potential_keys:
            if k in domains_cfg:
                target_channel_ids = domains_cfg[k]
                used_key = k
                break
        
        if not target_channel_ids:
             # Fallback to hard-failed default_channels
             target_channel_ids = default_channels
             used_key = "HARD_DEFAULT"
        
        if not target_channel_ids:
            return

        # 3. Broadcast
        print(f"   -> Routing: Key '{key}' resolved to '{used_key}' -> {target_channel_ids}")
        for ch_id in target_channel_ids:
            if ch_id not in channels_cfg:
                print(f"[Warn] Notification channel '{ch_id}' not defined in channels config.")
                continue
                
            channel_cfg = channels_cfg[ch_id]
            c_type = channel_cfg.get('type')
            
            try:
                if c_type == 'lark_webhook':
                    self._send_lark(channel_cfg.get('url'), title, message)
                elif c_type == 'telegram_bot':
                    self._send_telegram(
                        channel_cfg.get('token'), 
                        channel_cfg.get('chat_id'), 
                        title, 
                        message
                    )
            except Exception as e:
                print(f"[Warn] Notification send failed for {ch_id}: {e}")

    def _resolve_env(self, value: str) -> str:
        if value and value.startswith("${") and value.endswith("}"):
            return os.environ.get(value[2:-1], "")
        return value

    def _send_lark(self, url: str, title: str, text: str):
        raw_url = url
        url = self._resolve_env(url)
        
        if not url: 
            print(f"[Warn] Lark URL is empty! Raw: '{raw_url}'")
            return

        print(f"[Debug] Sending to Lark: {url[:30]}... (Len: {len(url)})")
        
        payload = {
            "msg_type": "text",
            "content": {"text": f"[{title}]\n{text}"}
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code != 200:
                print(f"[Error] Lark Webhook failed ({resp.status_code}): {resp.text}")
            else:
                # print(f"[Debug] Lark sent successfully.") # Optional
                pass
        except Exception as e:
            print(f"[Error] Lark request exception: {e}")

    def _send_telegram(self, token: str, chat_id: str, title: str, text: str):
        token = self._resolve_env(token)
        chat_id = self._resolve_env(chat_id)
        
        if not token or not chat_id:
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"*{title}*\n{text}",
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
