<a id="readme-top"></a>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&amp;color=0:1E3A8A,100:2563EB&amp;height=180&amp;section=header&amp;text=GEMILANG%20KINASIH&amp;fontSize=32&amp;fontColor=ffffff&amp;fontAlignY=36&amp;animation=fadeIn&amp;desc=Premium%20VPN%20and%20Tunneling%20Auto%20Installer&amp;descAlignY=58&amp;descSize=14" width="100%" alt="Header banner">

<br>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&amp;weight=500&amp;size=16&amp;pause=1200&amp;color=2563EB&amp;center=true&amp;vCenter=true&amp;width=440&amp;lines=Instalasi+VPN+dan+Tunneling+Otomatis;Cepat+%C2%B7+Stabil+%C2%B7+Aman;Fast+and+Stable+and+Secure" width="100%" style="max-width:440px" alt="Typing animation">

<br>

<img src="https://img.shields.io/badge/version-2.4-3b82f6?style=flat-square" alt="Version">
<img src="https://img.shields.io/badge/status-activated-16a34a?style=flat-square" alt="Activated">
<img src="https://img.shields.io/badge/license-private-e11d48?style=flat-square" alt="License">

<br>

<a href="README.md">
  <img src="https://img.shields.io/badge/Bahasa-Indonesia-DC2626?style=flat-square&amp;logo=googletranslate&amp;logoColor=white" alt="Bahasa Indonesia">
</a>
<a href="info/readme-eng.md">
  <img src="https://img.shields.io/badge/Language-English-2563EB?style=flat-square&amp;logo=googletranslate&amp;logoColor=white" alt="English">
</a>

</div>

<br>

---

## Tentang Script

Gemilang Kinasih Autoscript adalah script instalasi otomatis untuk membangun server VPN dan tunneling (SSH, OpenVPN, VMESS, VLESS, Trojan) dalam satu kali proses. Cocok digunakan oleh reseller maupun pengelola VPS pribadi yang ingin server siap pakai tanpa konfigurasi manual satu per satu.

### Instalasi

Salin dan jalankan perintah berikut di terminal VPS (root access):

```bash
apt update -y && apt upgrade -y && \
sysctl -w net.ipv6.conf.all.disable_ipv6=1 && \
wget https://raw.githubusercontent.com/gemilangkinasih/autoscript/main/setup.sh && \
chmod +x setup.sh && ./setup.sh
```

Proses instalasi berjalan otomatis. Setelah selesai, menu utama script akan tampil dan siap digunakan.

### Hubungi Kami

<div align="center">

<a href="https://wa.me/+6285196156105">
  <img src="https://img.shields.io/badge/WhatsApp-25D366?style=flat-square&amp;logo=whatsapp&amp;logoColor=white" alt="WhatsApp">
</a>
<a href="https://t.me/gemilangkinasih">
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=flat-square&amp;logo=telegram&amp;logoColor=white" alt="Telegram">
</a>

</div>

### Kompatibilitas Sistem Operasi

Script telah diuji dan berjalan stabil pada sistem operasi berikut:

| Sistem Operasi | Versi | Dropbear | Haproxy |
|:---|:---:|:---:|:---:|
| Ubuntu | 20, 22, 24 | Ya | Ya |
| Debian | 10, 11, 12 | Ya | Ya |

### Fitur Script Premium

**Manajemen Sistem**
- Instalasi dinamis, menyesuaikan spesifikasi VPS
- Auto-reboot terjadwal (tingkat keberhasilan 95%)
- Auto-fix Xray jika terjadi error
- Backup & restore konfigurasi

**Kontrol Pengguna**
- Manajemen akun pengguna dari menu
- Penghapusan otomatis akun expired
- Lock & unlock akun tertentu
- Pembatasan IP & kuota per akun

**Jaringan & Keamanan**
- Monitoring penggunaan bandwidth
- Proteksi brute-force dengan Fail2Ban
- Kontrol server via bot Telegram
- Notifikasi aktivitas server ke Telegram

### Informasi Multiport

Berikut daftar protokol dan port yang aktif secara default setelah instalasi:

| Layanan | Protokol | Port |
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

### Pengaturan Cloudflare

Jika domain diarahkan melalui Cloudflare, gunakan pengaturan berikut agar seluruh protokol berjalan normal:

| Pengaturan | Status |
|:---|:---:|
| SSL/TLS | `FULL` |
| SSL/TLS Recommender | `OFF` |
| gRPC | `ON` |
| WebSocket | `ON` |
| Always Use HTTPS | `OFF` |
| Under Attack Mode | `OFF` |

### Tampilan Menu Script

<div align="center">
<img width="100%" alt="Tampilan menu autoscript" src="https://github.com/gemilangkinasih/autoscript/raw/main/images/image-1.jpg">
<br>
<img width="100%" alt="Tampilan SSH premium" src="https://github.com/gemilangkinasih/autoscript/raw/main/images/image-2.jpg">
</div>

### Mekanisme Penyewaan

Versi terbaru script ini adalah `Version 2.4`. Seluruh fitur pada menu utama telah dioptimalkan agar minim bug dan stabil digunakan jangka panjang.

Langkah untuk menyewa/mengaktifkan script pada VPS Anda:

1. Hubungi admin melalui WhatsApp atau Telegram di atas
2. Kirimkan alamat IP VPS Anda
3. Lakukan pembayaran sesuai paket yang dipilih
4. Admin akan mengaktifkan IP Anda dan script siap digunakan

<div align="right"><a href="#readme-top"><sub>Kembali ke atas</sub></a></div>

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
