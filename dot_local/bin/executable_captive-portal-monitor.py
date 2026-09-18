#!/usr/bin/env python3
"""
Captive Portal Monitor for NetworkManager
- Event-driven via libnm (PyGObject / NM.Client) - zero CPU polling
- Accurately detects NM_CONNECTIVITY_PORTAL and misclassified LIMITED states
- Probes HTTP 302/307 redirect Location or standard generate_204 endpoint
- Automatically opens browser via xdg-open (debounced per connection)
- Displays desktop notifications via notify-send (Noctalia)
- Temporary periodic check only while in PORTAL state to detect login success, stops once FULL
"""

import os
import sys
import time
import signal
import subprocess
import threading
import urllib.request
import urllib.error
import gi

gi.require_version("NM", "1.0")
from gi.repository import NM, GLib, GLibUnix

PROBE_URLS = [
    "http://connectivitycheck.gstatic.com/generate_204",
    "http://detectportal.firefox.com/canonical.html",
    "http://captive.apple.com/hotspot-detect.html",
    "http://ping.archlinux.org/nm-check.txt",
]


def probe_portal_url():
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            return fp

        http_error_301 = http_error_302
        http_error_303 = http_error_302
        http_error_307 = http_error_302
        http_error_308 = http_error_302

    opener = urllib.request.build_opener(NoRedirect)
    for url in PROBE_URLS:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
            )
            with opener.open(req, timeout=2.5) as resp:
                if resp.status in (301, 302, 303, 307, 308):
                    loc = resp.headers.get("Location")
                    if loc and (loc.startswith("http://") or loc.startswith("https://")):
                        return loc
                if "generate_204" in url and resp.status == 200:
                    return url
        except Exception:
            continue
    return "http://connectivitycheck.gstatic.com/generate_204"


def send_notification(title, message, urgency="normal"):
    try:
        subprocess.run(
            [
                "notify-send",
                "-u",
                urgency,
                "-i",
                "network-wireless",
                "-a",
                "Captive Portal",
                title,
                message,
            ],
            timeout=5,
            check=False,
        )
    except Exception as e:
        print(f"Error sending notification: {e}", file=sys.stderr)


def open_browser(url):
    try:
        subprocess.Popen(["xdg-open", url])
    except Exception as e:
        print(f"Error opening browser: {e}", file=sys.stderr)


class CaptivePortalMonitor:
    def __init__(self):
        self.client = NM.Client.new(None)
        self.loop = GLib.MainLoop()
        self.was_in_portal = False
        self.portal_handled = False
        self.poll_timer_id = None
        self.settle_timer_id = None
        self.last_active_id = None

    def handle_portal_detection(self, force_open=False):
        if self.portal_handled and not force_open:
            return

        self.portal_handled = True
        self.was_in_portal = True

        def _worker():
            url = probe_portal_url()
            send_notification(
                "需要网络认证",
                "检测到当前网络需要网页登录认证，正在打开登录页面...",
                urgency="critical",
            )
            open_browser(url)

        threading.Thread(target=_worker, daemon=True).start()
        self.start_periodic_check()

    def handle_limited_detection(self):
        def _worker():
            url = probe_portal_url()
            # If a distinct redirect URL is found, it's actually a portal
            if url != "http://connectivitycheck.gstatic.com/generate_204":
                self.handle_portal_detection()
                return

            if not self.portal_handled:
                self.portal_handled = True
                send_notification(
                    "网络受限",
                    "已连接到网络，但无法访问互联网",
                    urgency="normal",
                )

        threading.Thread(target=_worker, daemon=True).start()

    def start_periodic_check(self):
        if self.poll_timer_id is not None:
            return

        def _poll():
            if not self.was_in_portal:
                self.poll_timer_id = None
                return False
            self.client.check_connectivity_async(None, self._on_connectivity_check_done, None)
            return True

        self.poll_timer_id = GLib.timeout_add_seconds(5, _poll)

    def stop_periodic_check(self):
        if self.poll_timer_id is not None:
            GLib.source_remove(self.poll_timer_id)
            self.poll_timer_id = None

    def _on_connectivity_check_done(self, client, res, user_data=None):
        try:
            client.check_connectivity_finish(res)
        except Exception:
            pass

    def on_connectivity_changed(self, client, param=None):
        conn = client.get_connectivity()
        if conn == NM.ConnectivityState.PORTAL:
            self.handle_portal_detection()
        elif conn == NM.ConnectivityState.FULL:
            if self.was_in_portal:
                send_notification(
                    "网络已连接",
                    "网络认证成功，已正常访问互联网",
                    urgency="normal",
                )
                self.was_in_portal = False
            self.portal_handled = False
            self.stop_periodic_check()
        elif conn == NM.ConnectivityState.LIMITED:
            self.handle_limited_detection()
        elif conn in (NM.ConnectivityState.NONE, NM.ConnectivityState.UNKNOWN):
            self.stop_periodic_check()
            self.portal_handled = False

    def on_primary_connection_changed(self, client, param=None):
        primary = client.get_primary_connection()
        conn_id = primary.get_id() if primary else None
        if conn_id != self.last_active_id:
            self.last_active_id = conn_id
            self.portal_handled = False
            self.was_in_portal = False
            self.stop_periodic_check()
            if self.settle_timer_id is not None:
                GLib.source_remove(self.settle_timer_id)
            self.settle_timer_id = GLib.timeout_add(1500, self._delayed_check)

    def _delayed_check(self):
        self.settle_timer_id = None
        self.client.check_connectivity_async(None, self._on_connectivity_check_done, None)
        return False

    def run(self):
        self.client.connect("notify::connectivity", self.on_connectivity_changed)
        self.client.connect("notify::primary-connection", self.on_primary_connection_changed)

        primary = self.client.get_primary_connection()
        if primary:
            self.last_active_id = primary.get_id()

        initial_conn = self.client.get_connectivity()
        if initial_conn == NM.ConnectivityState.PORTAL:
            self.handle_portal_detection()
        elif initial_conn == NM.ConnectivityState.LIMITED:
            self.handle_limited_detection()

        def _sig_handler():
            self.stop_periodic_check()
            self.loop.quit()
            return False

        GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, _sig_handler)
        GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, _sig_handler)

        self.loop.run()


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--open", "-o", "open"):
        url = probe_portal_url()
        print(f"Opening portal URL: {url}")
        open_browser(url)
        return

    monitor = CaptivePortalMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
