# Dual Boot Setup Guide: Arch Linux + Windows 11
## System Configuration: Ryzen 9 9900X | MSI Pro B850M-P WiFi | 32GB DDR5 | RTX 5070

---

## Table of Contents
1. [Pre-Installation Planning](#pre-installation-planning)
2. [Partitioning Strategy](#partitioning-strategy)
3. [Windows 11 Installation](#windows-11-installation)
4. [Arch Linux Installation](#arch-linux-installation)
5. [Hiding SATA Drives from Arch Linux](#hiding-sata-drives-from-arch-linux)
6. [Bootloader Configuration](#bootloader-configuration)
7. [Post-Installation Steps](#post-installation-steps)
8. [Potential Issues & Solutions](#potential-issues--solutions)

---

## Pre-Installation Planning

### ⚠️ Important Notes
- **Your concern about drive corruption is valid**: Windows Fast Startup and Hibernate can cause issues with shared drives
- **SATA drive visibility**: We'll configure Arch to ignore SATA drives at the kernel level
- **Backup everything**: Before proceeding, backup all important data
- **UEFI mode required**: Ensure your system boots in UEFI mode (not Legacy/CSM)

### What You'll Need
- [ ] Windows 11 installation USB (created with Rufus or Media Creation Tool)
- [ ] Arch Linux installation USB (use dd or Rufus in DD mode)
- [ ] 8GB+ USB drives for installation media
- [ ] Internet connection (Ethernet recommended for Arch installation)
- [ ] This guide accessible on another device

---

## Partitioning Strategy

### NVMe Drive Layout (1TB total)
```
/dev/nvme0n1
├── nvme0n1p1  512MB   EFI System Partition (ESP) - Shared
├── nvme0n1p2  16MB    Microsoft Reserved (MSR)
├── nvme0n1p3  500GB   Windows 11 (NTFS)
├── nvme0n1p4  200GB   Shared Data (exFAT)
├── nvme0n1p5  2GB     Linux Swap
├── nvme0n1p6  50GB    Arch Root (ext4)
└── nvme0n1p7  ~248GB  Arch Home (ext4)
```

**Note**: Adjust partition sizes based on your needs. The shared exFAT partition size is a suggestion.

---

## Windows 11 Installation

### Step 1: Boot from Windows USB
1. Insert Windows 11 USB and boot from it
2. Press DEL or F2 to enter BIOS
3. Verify UEFI mode is enabled and Secure Boot is enabled
4. Set USB as first boot device

### Step 2: Custom Partitioning
1. At Windows setup, select "Custom: Install Windows only (advanced)"
2. Delete all existing partitions on the NVMe drive (if starting fresh)
3. Click "New" and Windows will create:
   - EFI System Partition (100-512MB)
   - MSR (Microsoft Reserved) partition
   - Windows partition

4. **Manually adjust the Windows partition size**:
   - Select the Windows partition
   - Delete it
   - Click "New" and enter 512000 MB (500GB)
   - Leave the rest as unallocated space

### Step 3: Complete Windows Installation
1. Install Windows on the ~500GB partition you created
2. Complete the Windows setup process
3. **IMPORTANT**: Disable Fast Startup and Hibernation

### Step 4: Disable Fast Startup & Hibernate
Open PowerShell as Administrator and run:
```powershell
# Disable Fast Startup
powercfg /hibernate off

# Verify it's disabled
powercfg /availablesleepstates
```

Alternatively, via GUI:
1. Control Panel → Power Options → Choose what the power buttons do
2. Click "Change settings that are currently unavailable"
3. Uncheck "Turn on fast startup (recommended)"
4. Save changes

### Step 5: Create Shared exFAT Partition (Optional - do now or in Arch)
1. Press Win+X → Disk Management
2. Right-click on unallocated space
3. Create new simple volume (200GB suggested)
4. Format as exFAT
5. Label it "Shared" or "Data"

### Step 6: Update Windows
1. Run Windows Update completely
2. Install all drivers (chipset, GPU, etc.)
3. Restart if needed

---

## Arch Linux Installation

### Step 1: Boot Arch Linux USB
1. Insert Arch USB
2. Reboot and select USB from boot menu (F11 or F12)
3. Select "Arch Linux install medium" from the menu

### Step 2: Verify UEFI Mode
```bash
ls /sys/firmware/efi/efivars
```
If you see files listed, you're in UEFI mode. ✓

### Step 3: Connect to Internet
```bash
# For Ethernet (should work automatically)
ping -c 3 archlinux.org

# For WiFi
iwctl
[iwd]# device list
[iwd]# station wlan0 scan
[iwd]# station wlan0 get-networks
[iwd]# station wlan0 connect "YOUR_SSID"
[iwd]# exit

# Test connection
ping -c 3 archlinux.org
```

### Step 4: Update System Clock
```bash
timedatectl set-ntp true
timedatectl status
```

### Step 5: Partition the Remaining Space

**⚠️ CRITICAL**: Do NOT delete or modify the EFI, MSR, or Windows partitions!

```bash
# List all disks to identify your NVMe
lsblk

# Use gdisk for partitioning (better for UEFI)
gdisk /dev/nvme0n1
```

In gdisk:
```
# Create swap partition
Command: n
Partition number: 5 (or next available)
First sector: (press Enter - use default)
Last sector: +2G
Hex code: 8200 (Linux swap)

# Create root partition
Command: n
Partition number: 6
First sector: (press Enter)
Last sector: +50G
Hex code: 8304 (Linux x86-64 root)

# Create home partition
Command: n
Partition number: 7
First sector: (press Enter)
Last sector: (press Enter - use remaining space)
Hex code: 8302 (Linux /home)

# Write changes
Command: w
Type 'Y' to confirm
```

### Step 6: Format Partitions
```bash
# Format swap
mkswap /dev/nvme0n1p5
swapon /dev/nvme0n1p5

# Format root
mkfs.ext4 -L "Arch_Root" /dev/nvme0n1p6

# Format home
mkfs.ext4 -L "Arch_Home" /dev/nvme0n1p7

# Verify the EFI partition (DO NOT FORMAT IT)
lsblk -f | grep nvme0n1p1
# Should show vfat filesystem - leave it as is!
```

### Step 7: Mount Partitions
```bash
# Mount root
mount /dev/nvme0n1p6 /mnt

# Create mount points
mkdir -p /mnt/boot
mkdir -p /mnt/home

# Mount EFI partition (the one Windows created)
mount /dev/nvme0n1p1 /mnt/boot

# Mount home
mount /dev/nvme0n1p7 /mnt/home

# Verify mounts
lsblk
```

### Step 8: Install Base System
```bash
# Update package database
pacman -Sy

# Install base system and essential packages
pacstrap -K /mnt base base-devel linux linux-firmware \
  intel-ucode \
  networkmanager \
  vim nano \
  sudo \
  git \
  grub efibootmgr os-prober \
  ntfs-3g exfat-utils
```

**Note**: Replace `intel-ucode` with `amd-ucode` for AMD CPUs (you have Ryzen, so use `amd-ucode`)

Corrected command:
```bash
pacstrap -K /mnt base base-devel linux linux-firmware \
  amd-ucode \
  networkmanager \
  vim nano \
  sudo \
  git \
  grub efibootmgr os-prober \
  ntfs-3g exfat-utils
```

### Step 9: Generate fstab
```bash
genfstab -U /mnt >> /mnt/etc/fstab

# Verify it looks correct
cat /mnt/etc/fstab
```

### Step 10: Chroot into New System
```bash
arch-chroot /mnt
```

### Step 11: Configure System

#### Set Timezone
```bash
ln -sf /usr/share/zoneinfo/Region/City /etc/localtime
# Example: ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime
hwclock --systohc
```

#### Configure Locale
```bash
# Edit locale.gen
vim /etc/locale.gen

# Uncomment your locale, e.g.:
# en_US.UTF-8 UTF-8

# Generate locales
locale-gen

# Set system locale
echo "LANG=en_US.UTF-8" > /etc/locale.conf
```

#### Set Hostname
```bash
echo "archlinux" > /etc/hostname

# Edit hosts file
vim /etc/hosts
```

Add these lines:
```
127.0.0.1    localhost
::1          localhost
127.0.1.1    archlinux.localdomain archlinux
```

#### Set Root Password
```bash
passwd
```

#### Create User Account
```bash
useradd -m -G wheel,storage,power -s /bin/bash yourusername
passwd yourusername

# Enable sudo for wheel group
EDITOR=vim visudo

# Uncomment this line:
%wheel ALL=(ALL:ALL) ALL
```

### Step 12: Configure Bootloader (GRUB)

#### Enable os-prober to detect Windows
```bash
vim /etc/default/grub
```

Add or modify these lines:
```bash
GRUB_DISABLE_OS_PROBER=false
GRUB_TIMEOUT=5
GRUB_DEFAULT=saved
GRUB_SAVEDEFAULT=true
```

#### Install GRUB
```bash
# Install GRUB to EFI partition
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB

# Generate GRUB config
grub-mkconfig -o /boot/grub/grub.cfg
```

**Expected output**: Should detect Windows Boot Manager

### Step 13: Enable NetworkManager
```bash
systemctl enable NetworkManager
```

### Step 14: Exit and Reboot
```bash
exit           # Exit chroot
umount -R /mnt # Unmount all partitions
reboot         # Remove USB before system restarts
```

---

## Hiding SATA Drives from Arch Linux

After successfully booting into Arch Linux, follow these steps to prevent Arch from accessing SATA drives.

### Method 1: Using Kernel Parameters (Recommended)

This method prevents the kernel from even detecting SATA drives.

#### Step 1: Identify SATA Controller
```bash
# Find your SATA controller
lspci | grep -i sata

# Example output:
# 00:17.0 SATA controller: Advanced Micro Devices, Inc. [AMD] Device 1234
```

#### Step 2: Get PCI ID
```bash
# Get the PCI ID (e.g., 00:17.0)
lspci -nn | grep -i sata

# Example output:
# 00:17.0 SATA controller [0106]: Advanced Micro Devices, Inc. [AMD] Device [1022:43b8]
# The important part is [1022:43b8] - this is vendor:device ID
```

#### Step 3: Blacklist AHCI Module (Aggressive Approach)
```bash
# Edit GRUB config
sudo vim /etc/default/grub
```

Find the line starting with `GRUB_CMDLINE_LINUX_DEFAULT` and add:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet libahci.skip_host=0xffff"
```

Or to disable AHCI entirely:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet modprobe.blacklist=ahci"
```

Update GRUB:
```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

Reboot:
```bash
sudo reboot
```

**⚠️ Warning**: This will prevent ALL SATA devices from being detected, including optical drives.

### Method 2: Using udev Rules (Selective)

This method is more granular - it prevents automatic mounting but devices are still visible.

#### Step 1: Identify SATA Drives
```bash
# List all block devices
lsblk -o NAME,TRAN,SIZE,TYPE,MOUNTPOINT

# Identify drives with TRAN=sata
# Example:
# sda    sata   1T   disk
# sdb    sata   2T   disk
```

#### Step 2: Get Drive Serial Numbers
```bash
# Get detailed info for each SATA drive
for drive in /dev/sd?; do
    echo "=== $drive ==="
    udevadm info --query=property --name=$drive | grep -E 'ID_SERIAL|ID_MODEL'
done
```

#### Step 3: Create udev Rule
```bash
sudo vim /etc/udev/rules.d/99-hide-sata.rules
```

Add rules to ignore SATA drives:
```bash
# Block SATA drives from being auto-mounted or accessed
ACTION=="add|change", KERNEL=="sd[a-z]", ENV{ID_BUS}=="ata", ENV{UDISKS_IGNORE}="1"
ACTION=="add|change", KERNEL=="sd[a-z][0-9]*", ENV{ID_BUS}=="ata", ENV{UDISKS_IGNORE}="1"

# Alternative: Block by serial number (more specific)
# ACTION=="add|change", ATTR{serial}=="YOUR_SERIAL_HERE", ENV{UDISKS_IGNORE}="1"
```

#### Step 4: Reload udev Rules
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Method 3: Prevent Auto-Mounting in fstab

Edit `/etc/fstab` and add noauto for SATA drives:

```bash
sudo vim /etc/fstab
```

Add these lines to prevent mounting (use actual UUIDs):
```bash
# SATA drives - do not auto-mount
# UUID=xxxx-xxxx  /mnt/sata1  ext4  noauto,user  0  0
```

### Method 4: Disable in BIOS (Hardware Level)

**Most Reliable Method**:

1. Boot into BIOS/UEFI (DEL or F2 during startup)
2. Navigate to Storage Configuration or SATA Configuration
3. Look for options like:
   - SATA Port Enable/Disable
   - AHCI Controller settings
4. Disable individual SATA ports or the entire SATA controller
5. Save and exit

**Note**: You'll need to re-enable when booting to Windows if Windows uses SATA drives.

### Verification

After applying any method:
```bash
# Check if SATA drives are detected
lsblk | grep sd

# Check if they're mounted
mount | grep sd

# Verify only NVMe is accessible
lsblk -o NAME,TRAN,SIZE,MOUNTPOINT
```

---

## Bootloader Configuration

### Dual Boot Configuration

#### Option 1: GRUB Boot Menu (Default)
GRUB should automatically detect Windows. When you boot:
1. GRUB menu appears
2. Choose "Arch Linux" or "Windows Boot Manager"
3. Both OSes are accessible

#### Option 2: BIOS Boot Menu
You can also use BIOS boot menu:
1. Press F11 (or F12) during startup
2. Select boot device directly
3. Choose Windows Boot Manager or GRUB

### Set Default Boot OS

To set Arch as default:
```bash
sudo vim /etc/default/grub
```

Set:
```bash
GRUB_DEFAULT=0          # 0 = first entry (usually Arch)
GRUB_TIMEOUT=5          # Wait 5 seconds
GRUB_SAVEDEFAULT=true   # Remember last choice
```

Update GRUB:
```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

---

## Post-Installation Steps

### 1. Install Graphics Drivers (NVIDIA RTX 5070)

```bash
# Install NVIDIA proprietary drivers
sudo pacman -S nvidia nvidia-utils nvidia-settings

# For 32-bit support (gaming)
sudo pacman -S lib32-nvidia-utils

# Edit mkinitcpio to add nvidia modules
sudo vim /etc/mkinitcpio.conf
```

Find the MODULES line and add nvidia modules:
```bash
MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)
```

Regenerate initramfs:
```bash
sudo mkinitcpio -P
```

Add kernel parameter for DRM:
```bash
sudo vim /etc/default/grub
```

Add to GRUB_CMDLINE_LINUX_DEFAULT:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet nvidia-drm.modeset=1"
```

Update GRUB:
```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
sudo reboot
```

### 2. Install Desktop Environment

#### KDE Plasma (Recommended for gaming/NVIDIA)
```bash
sudo pacman -S plasma-meta kde-applications-meta
sudo systemctl enable sddm
sudo reboot
```

#### GNOME
```bash
sudo pacman -S gnome gnome-extra
sudo systemctl enable gdm
sudo reboot
```

#### Xfce (Lightweight)
```bash
sudo pacman -S xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
sudo systemctl enable lightdm
sudo reboot
```

### 3. Setup Shared exFAT Partition

```bash
# Create mount point
sudo mkdir /mnt/shared

# Get UUID of exFAT partition
sudo blkid | grep exfat

# Edit fstab
sudo vim /etc/fstab
```

Add this line (replace UUID):
```bash
UUID=xxxx-xxxx  /mnt/shared  exfat  defaults,uid=1000,gid=1000,dmask=027,fmask=137  0  0
```

Mount it:
```bash
sudo mount -a
```

### 4. Install AUR Helper (yay)
```bash
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

### 5. Essential Software
```bash
# Browser
sudo pacman -S firefox chromium

# Development tools
sudo pacman -S code  # VS Code (if available), or use yay

# System monitoring
sudo pacman -S htop neofetch

# File managers
sudo pacman -S dolphin thunar

# Media
sudo pacman -S vlc
```

---

## Potential Issues & Solutions

### Issue 1: GRUB Doesn't Detect Windows

**Solution**:
```bash
# Ensure os-prober is installed and enabled
sudo pacman -S os-prober
sudo vim /etc/default/grub

# Set:
GRUB_DISABLE_OS_PROBER=false

# Remount Windows EFI if needed
sudo mkdir /mnt/windows
sudo mount /dev/nvme0n1p3 /mnt/windows

# Regenerate GRUB config
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### Issue 2: Windows Updates Breaking GRUB

**Symptom**: After Windows update, system boots directly to Windows

**Solution**:
1. Boot from Arch USB
2. Mount your Arch partitions:
```bash
mount /dev/nvme0n1p6 /mnt
mount /dev/nvme0n1p1 /mnt/boot
mount /dev/nvme0n1p7 /mnt/home
arch-chroot /mnt
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
exit
reboot
```

### Issue 3: Secure Boot Issues

**Symptom**: System won't boot Arch with Secure Boot enabled

**Solution**:
1. Disable Secure Boot in BIOS
2. Or sign GRUB/kernel with your own keys (advanced)
3. Or use PreLoader/shim (check Arch Wiki)

### Issue 4: Time Difference Between Windows and Linux

**Symptom**: Clock shows wrong time after switching between OSes

**Solution** (Make Linux use local time like Windows):
```bash
timedatectl set-local-rtc 1 --adjust-system-clock
```

Or make Windows use UTC (recommended):
In Windows, run as Administrator:
```powershell
reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f
```

### Issue 5: NVIDIA Driver Issues

**Symptom**: Black screen, no display after installing drivers

**Solution**:
1. Boot with `nomodeset` kernel parameter (edit in GRUB menu)
2. Add `nvidia-drm.modeset=1` to GRUB config
3. Ensure nvidia modules are in mkinitcpio.conf
4. Check `/var/log/Xorg.0.log` for errors

### Issue 6: SATA Drives Still Visible

**Symptom**: SATA drives appear despite configuration

**Solution**:
1. Verify udev rules are correct: `sudo udevadm control --reload-rules`
2. Check kernel parameters: `cat /proc/cmdline`
3. Use BIOS method to disable SATA controller
4. Check if drives are mounted: `mount | grep sd`

### Issue 7: Cannot Access Shared exFAT Partition

**Symptom**: Permission denied on /mnt/shared

**Solution**:
```bash
# Ensure exfat-utils is installed
sudo pacman -S exfat-utils

# Fix fstab entry with proper permissions
sudo vim /etc/fstab

# Use these options:
UUID=xxxx  /mnt/shared  exfat  defaults,uid=1000,gid=1000,dmask=027,fmask=137  0  0

# Remount
sudo umount /mnt/shared
sudo mount -a
```

### Issue 8: Ethernet/WiFi Not Working

**Symptom**: No internet connection in Arch

**Solution**:
```bash
# Check network interfaces
ip link

# Enable and start NetworkManager
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

# Use nmtui for easy configuration
nmtui

# For WiFi drivers, install linux-firmware
sudo pacman -S linux-firmware
```

---

## Maintenance Tips

### Regular Arch Updates
```bash
# Full system update
sudo pacman -Syu

# Clean package cache
sudo pacman -Sc
```

### Kernel Updates
When Linux kernel updates:
```bash
# Regenerate GRUB config to update boot entries
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### Backup Important Files
- `/etc/fstab` - Mount points
- `/etc/default/grub` - GRUB configuration
- `/boot/grub/grub.cfg` - GRUB menu
- `/home/` - Your personal files

### Windows Fast Startup Reminder
**NEVER re-enable Fast Startup or Hibernate in Windows** - it will cause corruption on shared drives!

---

## Summary Checklist

- [x] Windows 11 installed on 500GB partition
- [x] Fast Startup and Hibernate disabled in Windows
- [x] Arch Linux installed on 500GB partition
- [x] GRUB configured to dual-boot
- [x] SATA drives hidden from Arch (choose method)
- [x] Shared exFAT partition accessible
- [x] NVIDIA drivers installed and working
- [x] Desktop environment installed
- [x] Time synchronization fixed
- [x] NetworkManager working
- [x] All partitions properly mounted

---

## Additional Resources

- [Arch Wiki: Dual Boot with Windows](https://wiki.archlinux.org/title/Dual_boot_with_Windows)
- [Arch Wiki: GRUB](https://wiki.archlinux.org/title/GRUB)
- [Arch Wiki: NVIDIA](https://wiki.archlinux.org/title/NVIDIA)
- [Arch Wiki: udev](https://wiki.archlinux.org/title/Udev)

---

## Notes for Your Specific Hardware

### Ryzen 9 9900X (Zen 5 Architecture)
- Use `amd-ucode` for microcode updates
- Latest kernel recommended (you may need `linux-zen` for better performance)
- Consider installing `zenpower3-dkms` for better CPU monitoring

### MSI Pro B850M-P WiFi
- BIOS should be updated to latest version
- Enable IOMMU if you plan to use virtualization
- XMP/EXPO profile for RAM (6000MHz)

### NVIDIA RTX 5070
- Use proprietary drivers (`nvidia` package)
- Install `nvidia-settings` for GPU configuration
- Consider `nvidia-prime` if you have integrated graphics

### DDR5 6000MHz
- Enable XMP/EXPO in BIOS for rated speeds
- May need to adjust timings manually if unstable

---

## Final Words

This setup gives you:
✅ Clean dual-boot with shared bootloader
✅ SATA drives protected from accidental access
✅ Shared exFAT partition for cross-OS files  
✅ Windows won't interfere with Linux partitions
✅ Easy to maintain and update

**Good luck with your installation! Take your time and read each step carefully.**

If you encounter issues not covered here, check the Arch Wiki or forums.
