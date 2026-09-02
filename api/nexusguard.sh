#!/usr/bin/env bash
# NEXUS TUNNELING - Guardian
# 1) Auto-del trial expired (menit-presisi, via /etc/xray/trial-expiry)
# 2) Auto-lock IP melebihi limit (dari access.log + /etc/kyt/limit/<proto>/ip/<user>)
# 3) Kuota tetap via limit.vmess/vless/trojan services (sudah ada)
# 4) Log semua aksi
LOCKLOG=/var/log/nexus-guardian.log

log() { echo "$(date '+%F %T') $1" >> $LOCKLOG; }

# ---------- helper: lock/unlock user di SEMUA marker ----------
lock_user() {  # $1 proto $2 user $3 exp $4 key(uuid/pass)
  local p=$1 u=$2 e=$3 k=$4
  local locked entry_prefix
  entry_prefix="###"
  [ "$p" = "vless" ] && entry_prefix="#&"
  [ "$p" = "trojan" ] && entry_prefix="#!"
  case $p in
    vmess)  locked="xrayvmess$(tr -dc 'a-zA-Z0-9' </dev/urandom | fold -w 15 | head -n1)LOCKED";;
    vless)  locked="xrayvless$(tr -dc 'a-zA-Z0-9' </dev/urandom | fold -w 15 | head -n1)LOCKED";;
    trojan) locked="xraytrojan$(tr -dc 'a-zA-Z0-9' </dev/urandom | fold -w 15 | head -n1)LOCKED";;
  esac
  # db: simpan key asli di kolom 4 (untuk unlock); db selalu prefix ###
  sed -i "/^### $u /d" /etc/$p/.$p.db
  echo "### $u $e $k $locked" >> /etc/$p/.$p.db
  # config: hapus entry user lalu insert LOCKED di SEMUA marker proto tsb
  sed -i "/^$entry_prefix $u $e/,/^},{/d" /etc/xray/config.json
  local markers
  markers=$(grep -oE "^#$p[a-z-]*" /etc/xray/config.json | sort -u)
  while IFS= read -r m; do
    [ -z "$m" ] && continue
    if [[ "$p" == "trojan" ]]; then
      sed -i "/^${m}\$/a\\$entry_prefix $u $e\n},{\"password\": \"$locked\",\"email\" : \"$u\"" /etc/xray/config.json
    else
      sed -i "/^${m}\$/a\\$entry_prefix $u $e\n},{\"id\": \"$locked\",\"email\" : \"$u\"" /etc/xray/config.json
    fi
  done <<< "$markers"
  echo "$locked" > /etc/limit/$p/.lock-$u 2>/dev/null
  log "LOCK $p/$u (exp $e)"
}

unlock_user() {  # $1 proto $2 user
  local p=$1 u=$2
  local row e k entry_prefix
  entry_prefix="###"
  [ "$p" = "vless" ] && entry_prefix="#&"
  [ "$p" = "trojan" ] && entry_prefix="#!"
  row=$(grep "^### $u " /etc/$p/.$p.db | head -1)
  e=$(echo "$row" | awk '{print $3}')
  k=$(echo "$row" | awk '{print $4}')
  [ -z "$k" ] && { log "UNLOCK FAIL $p/$u: key tidak ada"; return 1; }
  sed -i "/^$entry_prefix $u $e/,/^},{/d" /etc/xray/config.json
  local markers
  markers=$(grep -oE "^#$p[a-z-]*" /etc/xray/config.json | sort -u)
  while IFS= read -r m; do
    [ -z "$m" ] && continue
    if [[ "$p" == "trojan" ]]; then
      sed -i "/^${m}\$/a\\$entry_prefix $u $e\n},{\"password\": \"$k\",\"email\" : \"$u\"" /etc/xray/config.json
    else
      sed -i "/^${m}\$/a\\$entry_prefix $u $e\n},{\"id\": \"$k\",\"email\" : \"$u\"" /etc/xray/config.json
    fi
  done <<< "$markers"
  rm -f /etc/limit/$p/.lock-$u
  log "UNLOCK $p/$u"
}

# ---------- 1) TRIAL AUTO-DELETE ----------
# format file: <proto> <user> <epoch_expiry>
EXPFILE=/etc/xray/trial-expiry
if [ -f "$EXPFILE" ]; then
  now=$(date +%s)
  while read -r proto user exp_epoch; do
    [ -z "$proto" ] && continue
    if [ "$now" -ge "$exp_epoch" ]; then
      case $proto in
        vmess|vless|trojan)
          e=$(grep "^### $user " /etc/$proto/.$proto.db | head -1 | awk '{print $3}')
          sed -i "/^### $user $e/,/^},{/d" /etc/xray/config.json
          sed -i "/^### $user /d" /etc/$proto/.$proto.db
          rm -f /etc/vmess/$user /etc/limit/$proto/$user /etc/kyt/limit/$proto/ip/$user /var/www/html/$proto-$user.txt /var/www/html/$proto-$user.html
          log "TRIAL-DEL $proto/$user (expired)"
          ;;
        ssh)
          userdel -r "$user" &>/dev/null
          sed -i "/^### $user /d" /etc/ssh/.ssh.db 2>/dev/null
          rm -f /var/www/html/ssh-$user.txt /var/www/html/ssh-$user.html
          log "TRIAL-DEL ssh/$user (expired)"
          ;;
      esac
      sed -i "/^$proto $user /d" $EXPFILE
    fi
  done < <(grep -v '^#' $EXPFILE)
fi

# ---------- 2) IP LIMIT AUTO-LOCK ----------
# hitung IP unik per user dari access.log (window ~5 menit terakhir)
LOG=/var/log/xray/access.log
[ -s "$LOG" ] || exit 0
for proto in vmess vless trojan; do
  IPDIR=/etc/kyt/limit/$proto/ip
  [ -d "$IPDIR" ] || continue
  for limitfile in "$IPDIR"/*; do
    [ -e "$limitfile" ] || continue
    u=$(basename "$limitfile")
    lim=$(cat "$limitfile" 2>/dev/null); lim=${lim:-1}
    # sudah locked? skip
    grep -q "^### $u .*LOCKED" /etc/$proto/.$proto.db 2>/dev/null && continue
    # ip unik user (prefix /16 dianggap sama? tidak — pakai IP penuh, prefix /24 utk mobile)
    n=$(grep "accepted" "$LOG" | grep -w "\[$u " | awk -F'from ' '{print $2}' | cut -d: -f1 | sort -u | wc -l)
    [ "$n" -gt "$lim" ] && [ "$n" -gt 0 ] && {
      row=$(grep "^### $u " /etc/$proto/.$proto.db | head -1)
      e=$(echo "$row" | awk '{print $3}')
      k=$(echo "$row" | awk '{print $4}')
      if [ -n "$e" ] && [ -n "$k" ]; then
        lock_user "$proto" "$u" "$e" "$k"
        systemctl restart xray >/dev/null 2>&1
      fi
    }
  done
done

exit 0
