if [[ $(stat -fc %T /sys/fs/cgroup) != "cgroup2fs" ]]; then
  echo "cgroup v2 non attivo – aggiungo kernel param"
  sudo sed -i 's/^GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1 /' /etc/default/grub
  sudo grub-mkconfig -o /boot/grub/grub.cfg   # per GRUB
  # per systemd‑boot:
  # sudo bootctl update
  echo "Riavvia il PC e ritorna qui"
  exit 0
fi
