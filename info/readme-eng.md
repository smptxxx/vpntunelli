<a id="readme-top"></a>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&amp;color=0:1E3A8A,100:2563EB&amp;height=180&amp;section=header&amp;text=GEMILANG%20KINASIH&amp;fontSize=32&amp;fontColor=ffffff&amp;fontAlignY=36&amp;animation=fadeIn&amp;desc=Premium%20VPN%20and%20Tunneling%20Auto%20Installer&amp;descAlignY=58&amp;descSize=14" width="100%" alt="Header banner">

<br>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&amp;weight=500&amp;size=16&amp;pause=1200&amp;color=2563EB&amp;center=true&amp;vCenter=true&amp;width=440&amp;lines=Automated+VPN+and+Tunneling+Setup;Fast+%C2%B7+Stable+%C2%B7+Secure" width="100%" style="max-width:440px" alt="Typing animation">

<br>

<img src="https://img.shields.io/badge/version-2.4-3b82f6?style=flat-square" alt="Version">
<img src="https://img.shields.io/badge/status-activated-16a34a?style=flat-square" alt="activated">
<img src="https://img.shields.io/badge/license-private-e11d48?style=flat-square" alt="License">

<br>

<a href="../README.md">
  <img src="https://img.shields.io/badge/Bahasa-Indonesia-DC2626?style=flat-square&amp;logo=googletranslate&amp;logoColor=white" alt="Bahasa Indonesia">
</a>
<a href="readme-eng.md">
  <img src="https://img.shields.io/badge/Language-English-2563EB?style=flat-square&amp;logo=googletranslate&amp;logoColor=white" alt="English">
</a>

</div>

<br>

---

## About This Script

Gemilang Kinasih Autoscript is an automated installer for building a VPN and tunneling server (SSH, OpenVPN, VMESS, VLESS, Trojan) in a single run. It's built for resellers and VPS administrators who want a ready-to-use server without manually configuring each service.

### Installation

Copy and run the following command on your VPS terminal (root access required):

```bash
apt update -y && apt upgrade -y && \
sysctl -w net.ipv6.conf.all.disable_ipv6=1 && \
wget https://raw.githubusercontent.com/gemilangkinasih/autoscript/main/setup.sh && \
chmod +x setup.sh && ./setup.sh
```

The installation runs automatically. Once finished, the main menu will appear and the script is ready to use.

### Contact Us

<div align="center">

<a href="https://wa.me/+6285196156105">
  <img src="https://img.shields.io/badge/WhatsApp-25D366?style=flat-square&amp;logo=whatsapp&amp;logoColor=white" alt="WhatsApp">
</a>
<a href="https://t.me/gemilangkinasih">
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=flat-square&amp;logo=telegram&amp;logoColor=white" alt="Telegram">
</a>

</div>

### OS Compatibility

The script has been tested and runs stably on the following operating systems:

| OS | Versions | Dropbear | Haproxy |
|:---|:---:|:---:|:---:|
| Ubuntu | 20, 22, 24 | Yes | Yes |
| Debian | 10. 11, 12 | Yes | Yes |

### Premium Script Features

**System Management**
- Dynamic installation, adapts to VPS specs
- Scheduled auto-reboot (95% success rate)
- Auto-fix Xray on error
- Configuration backup & restore

**User Control**
- Manage user accounts from the menu
- Automatic removal of expired accounts
- Lock & unlock specific accounts
- IP & quota limits per account

**Network & Security**
- Bandwidth usage monitoring
- Brute-force protection via Fail2Ban
- Server control through a Telegram bot
- Server activity notifications on Telegram

### Multiport Info

Below are the protocols and ports enabled by default after installation:

| Service | Protocol | Port |
|:---|:---:|:---:|
| SSH | WS/TLS | 443 |
| SSH | Non-TLS | 8880, 80 |
| SSH | UDP | 1–65535 |
| OpenVPN | SSL/TCP | 1194 |
| VMESS | WS | 443 |
| VMESS | gRPC | 443 |
| VMESS | Non-TLS | 80 |
| VLESS | WS | 443 |
| VLESS | gRPC | 443 |
| VLESS | Non-TLS | 80 |
| Trojan | WS | 443 |
| Trojan | gRPC | 443 |

### Cloudflare Settings

If your domain is proxied through Cloudflare, use the following settings so every protocol works correctly:

| Setting | Status |
|:---|:---:|
| SSL/TLS | `FULL` |
| SSL/TLS Recommender | `OFF` |
| gRPC | `ON` |
| WebSocket | `ON` |
| Always Use HTTPS | `OFF` |
| Under Attack Mode | `OFF` |

### Script Menu Preview

<div align="center">
<img width="100%" alt="Autoscript menu preview" src="https://github.com/gemilangkinasih/autoscript/raw/main/images/image-1.jpg">
<br>
<img width="100%" alt="SSH premium preview" src="https://github.com/gemilangkinasih/autoscript/raw/main/images/image-2.jpg">
</div>

### Rental Mechanism

The current release is `Version 2.4`. All features in the main menu have been optimized for stability and minimal bugs over long-term use.

Steps to rent/activate the script on your VPS:

1. Contact the admin via WhatsApp or Telegram above
2. Send your VPS IP address
3. Complete payment for your chosen package
4. The admin will activate your IP and the script will be ready to use

<div align="right"><a href="#readme-top"><sub>Back to top</sub></a></div>

<br>

---

<div align="center">

<sub><b>CONTACT &amp; SUPPORT</b></sub>

<a href="https://wa.me/+6285196156105">
  <img src="https://img.shields.io/badge/WhatsApp-25D366?style=flat-square&amp;logo=whatsapp&amp;logoColor=white" alt="WhatsApp">
</a>
<a href="https://t.me/gemilangkinasih">
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=flat-square&amp;logo=telegram&amp;logoColor=white" alt="Telegram">
</a>

</div>

<img src="https://capsule-render.vercel.app/api?type=waving&amp;color=0:2563EB,100:1E3A8A&amp;height=150&amp;section=footer&amp;animation=fadeIn" width="100%" alt="Footer banner">
