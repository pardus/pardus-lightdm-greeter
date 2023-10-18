import gi
import subprocess
gi.require_version('NM', '1.0')
from gi.repository import NM
import os

class wifi_object:
    def __init__(self,ap):
        self.bssid = ap.get_bssid()
        self.ssid = self._ssid_to_utf8(ap)
        self.signal = ap.get_strength()
        self.security = self.flags_to_security(ap.get_flags(), ap.get_wpa_flags(), ap.get_rsn_flags())
        self.connected = False

    def _ssid_to_utf8(self, ap):
        ssid = ap.get_ssid()
        if not ssid:
            return ""
        return NM.utils_ssid_to_utf8(ap.get_ssid().get_data())

    def flags_to_security(self,flags, wpa_flags, rsn_flags):
        str = ""
        if (
            (flags & getattr(NM, "80211ApFlags").PRIVACY)
            and (wpa_flags == 0)
            and (rsn_flags == 0)
        ):
            str = str + " WEP"
        if wpa_flags != 0:
            str = str + " WPA1"
        if rsn_flags != 0:
            str = str + " WPA2"
        if (wpa_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_802_1X) or (
            rsn_flags & getattr(NM, "80211ApSecurityFlags").KEY_MGMT_802_1X
        ):
            str = str + " 802.1X"
        return str.lstrip()

    def need_password(self):
        if os.path.exists("/etc/NetworkManager/system-connections/{}.nmconnection".format(self.ssid)):
            return False
        elif self.security == "":
            return False
        return True

    def connect(self,password=""):
        if not self.need_password():
            0 == os.system("nmcli device wifi connect '{}'".format(self.bssid))
        elif self.security in ["WPA2", "WPA1 WPA2"]:
            0 == os.system("nmcli device wifi connect '{}' password '{}'".format(self.bssid,password))
        else:
            print("Fixme")
            return False
    def disconnect(self):
        return 0 == os.system("nmcli con down '{}'".format(self.ssid))

def available():
    for adapter in os.listdir("/sys/class/net/"):
        if os.path.exists("/sys/class/net/{}/wireless".format(adapter)):
            return True
    if len(list_wifi()) != 0:
        return True
    return False

def list_wifi():
    wifis = []
    nmc = NM.Client.new(None)
    devs = nmc.get_devices()
    cache = []

    for dev in devs:
        if dev.get_device_type() == NM.DeviceType.WIFI:
            for ap in dev.get_access_points():
                wo = wifi_object(ap)
                if wo.ssid not in cache:
                    wifis.append(wo)
                    cache.append(wo.ssid)

    ac = nmc.get_active_connections()
    for aa in ac:
        for w in wifis:
            if w.ssid == aa.get_id():
                print(w.bssid, aa.get_uuid())
                w.connected = True
    
    return wifis
