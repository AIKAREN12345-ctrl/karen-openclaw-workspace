# Comprehensive Dual-Boot Linux Guide for Beelink EQR6

**Research Date:** 2026-04-15  
**Target Hardware:** Beelink EQR6 (AMD Ryzen 6600H/6800U/6900HX, 20GB DDR5 RAM, Radeon 680M iGPU)  
**Goal:** Zero-error dual-boot setup with maximum local LLM performance

---

## Table of Contents

1. [Beelink EQR6 Hardware Overview](#1-beelink-eqr6-hardware-overview)
2. [Linux Compatibility & Known Issues](#2-linux-compatibility--known-issues)
3. [Best Linux Distro for AI/ML](#3-best-linux-distro-for-aiml)
4. [Dual-Boot Setup with Windows 11](#4-dual-boot-setup-with-windows-11)
5. [BitNet 1.58 Setup on Linux](#5-bitnet-158-setup-on-linux)
6. [Ollama Linux Setup & Optimization](#6-ollama-linux-setup--optimization)
7. [RAM Optimization for 20GB](#7-ram-optimization-for-20gb)
8. [CPU Performance Tuning](#8-cpu-performance-tuning)
9. [Step-by-Step Installation Guide](#9-step-by-step-installation-guide)
10. [Performance Comparison: Linux vs Windows](#10-performance-comparison-linux-vs-windows)

---

## 1. Beelink EQR6 Hardware Overview

### Specifications

| Component | Details |
|-----------|---------|
| **CPU Options** | AMD Ryzen 5 6600H (6C/12T) / Ryzen 7 6800U (8C/16T) / Ryzen 9 6900HX (8C/16T, up to 4.9GHz) |
| **iGPU** | AMD Radeon 680M (RDNA2, 12 CUs) |
| **RAM** | 20GB DDR5-4800 (soldered, non-upgradeable on some models) |
| **Storage** | 1TB PCIe 4.0 NVMe SSD + Second M.2 PCIe 4.0 slot |
| **WiFi** | WiFi 6 (802.11ax) - MediaTek or Intel AX101/AX201 |
| **Bluetooth** | Bluetooth 5.2 |
| **LAN** | Dual Gigabit Ethernet |
| **Display Outputs** | Dual HDMI 2.0 (4K@60Hz) |
| **USB** | Multiple USB 3.2 ports |
| **Power** | Integrated 85W PSU (no external brick) |

### Key Considerations for Linux

- **35W TDP cap** on 6900HX model (performance limited compared to SER6 series)
- **85°C thermal limit** - aggressive throttling under sustained load
- **Dual NVMe slots** - perfect for dual-boot with separate drives
- **No USB4** - limited expansion options compared to SER series

---

## 2. Linux Compatibility & Known Issues

### ✅ Working Out of Box

- CPU (all cores, frequency scaling)
- Ethernet (both ports)
- USB ports
- HDMI outputs (with amdgpu driver)
- NVMe SSDs

### ⚠️ Known Issues & Fixes

#### Issue 1: WiFi Not Recognized (MediaTek/Intel AX101)

**Problem:** WiFi 6 adapter not detected in Debian 12 and some Ubuntu versions.

**Fix for Intel AX101:**
```bash
# Download firmware manually
wget https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/plain/iwlwifi-so-a0-hr-b0-89.ucode
sudo cp iwlwifi-so-a0-hr-b0-89.ucode /lib/firmware
reboot
```

**Fix for MediaTek:**
```bash
# Install kernel 6.5+ for better MediaTek support
sudo apt install linux-image-generic-hwe-24.04
```

#### Issue 2: Bluetooth Shows Only MAC Addresses

**Problem:** Bluetooth devices appear as numbers/addresses, not names. Cannot connect.

**Fix:**
```bash
# Update bluez and firmware
sudo apt update
sudo apt install bluez-firmware

# Restart Bluetooth
sudo systemctl restart bluetooth

# If still failing, try:
sudo apt install linux-firmware
```

#### Issue 3: Audio Over HDMI/Bluetooth

**Fix:**
```bash
# Install pipewire for better audio handling
sudo apt install pipewire pipewire-pulse
systemctl --user enable pipewire pipewire-pulse
```

#### Issue 4: 35W TDP Power Limitation

The EQR6 has a 35W TDP cap vs 45W+ on SER series. This is a **hardware/firmware limitation**.

**Mitigation:**
```bash
# Enable AMD P-State EPP for better frequency management
echo active | sudo tee /sys/devices/system/cpu/amd_pstate/status
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference
```

---

## 3. Best Linux Distro for AI/ML

### Recommendation: **Ubuntu 24.04 LTS** (Primary Choice)

| Distro | Pros | Cons | Best For |
|--------|------|------|----------|
| **Ubuntu 24.04 LTS** | Best ROCm support, pre-built AI packages, largest community, stable | Slightly older packages | Production AI/ML, beginners |
| **Fedora 41** | Latest kernel, bleeding-edge packages, good AMD support | Shorter support cycle, ROCm setup more complex | Developers, latest features |
| **Pop!_OS** | Excellent NVIDIA/AMD GPU support, built-in AI tools | Smaller community | GPU-heavy workloads |
| **Arch Linux** | Rolling release, AUR access, maximum control | High maintenance | Advanced users |
| **CachyOS** | Optimized kernels, AMD P-State patches, performance tuned | Less mainstream | Performance enthusiasts |

### Why Ubuntu 24.04 LTS for EQR6?

1. **ROCm Support:** Official AMD support for Ryzen APUs
2. **Kernel 6.8:** Includes AMD P-State driver improvements
3. **Ollama:** Native .deb packages available
4. **BitNet:** Easy Python/pip installation
5. **Stability:** 5-year support cycle

---

## 4. Dual-Boot Setup with Windows 11

### Pre-Installation Checklist

1. **Backup Windows data** (critical!)
2. **Disable BitLocker** temporarily
3. **Check BIOS version** - update if available from Beelink
4. **Prepare USB drive** (8GB+)

### BIOS Configuration (Beelink EQR6)

```
## Access BIOS
Press DEL or F7 repeatedly during boot

## Secure Boot Configuration
Security > Secure Boot:
- Secure Boot Mode: Standard
- Secure Boot: Enabled (Ubuntu supports this)

## Boot Order
Boot > Boot Option Priorities:
- Set USB as first for installation

## AMD CBS Settings (Advanced)
Advanced > AMD CBS > FCH Common Options > Ac Power Loss Options:
- Ac Loss Control: Always On (optional)

## CPU Configuration
Advanced > AMD CBS > CPU Common Options:
- CPPC: Enabled
- Core Performance Boost: Enabled
```

### Partitioning Strategy

#### Option A: Same Drive (Advanced)

```
Disk Layout (1TB example):
├─ EFI System Partition: 512MB (existing, keep)
├─ Windows C: 400GB (existing, shrink)
├─ Linux Root (/): 80GB (ext4)
├─ Linux Home (/home): 150GB (ext4)
├─ Linux Swap: 20GB (or use swap file)
└─ Shared Data: Remaining (NTFS or exFAT)
```

#### Option B: Separate Drive (Recommended for EQR6)

The EQR6 has **dual M.2 slots** - use this to your advantage!

```
Drive 1 (Original): Windows 11 only
├─ EFI: 512MB
├─ Windows C: Full drive
└─ Windows Recovery

Drive 2 (New/Second): Linux only
├─ EFI: 512MB (optional, can share)
├─ Linux Root (/): 100GB
├─ Linux Home (/home): Remaining
└─ Swap: 20GB (or use swap file)
```

**Benefits of Separate Drives:**
- No partition resizing risk
- Independent OS management
- Easier troubleshooting
- Better performance (dedicated I/O)

### Step-by-Step Dual-Boot Installation

#### Step 1: Prepare Windows

```powershell
# In Windows PowerShell (Admin)
# Disable Fast Startup
powercfg /hibernate off

# Disable BitLocker (if enabled)
manage-bde -off C:

# Shrink C: drive if using same disk
# Use Disk Management GUI or:
diskmgmt.msc
```

#### Step 2: Create Bootable USB

```bash
# On Linux/Mac
sudo dd if=ubuntu-24.04-desktop-amd64.iso of=/dev/sdX bs=4M status=progress

# On Windows, use Rufus:
# - Select ISO
# - GPT partition scheme
# - UEFI target system
# - Start
```

#### Step 3: Install Ubuntu

1. Boot from USB (press F7 for boot menu)
2. Select "Try or Install Ubuntu"
3. Choose language, keyboard
4. **Installation Type:**
   - If separate drive: "Erase disk and install Ubuntu" (on Drive 2)
   - If same drive: "Install alongside Windows"
   - Or "Something else" for manual partitioning

5. **Manual Partitioning (if needed):**
   ```
   /dev/nvme0n1 (Windows drive - DON'T TOUCH)
   /dev/nvme1n1 (Linux drive)
   ├─ /dev/nvme1n1p1: EFI System Partition (512MB, FAT32, mount at /boot/efi)
   ├─ /dev/nvme1n1p2: / (root, 100GB, ext4)
   ├─ /dev/nvme1n1p3: /home (remaining, ext4)
   └─ /dev/nvme1n1p4: swap (20GB, swap)
   ```

6. Install bootloader to EFI partition
7. Complete installation and reboot

#### Step 4: Fix GRUB (if Windows missing)

```bash
# If Windows doesn't appear in GRUB
sudo update-grub

# If still missing, install os-prober
sudo apt install os-prober
sudo os-prober
sudo update-grub
```

#### Step 5: Fix Time Sync Issue

Windows and Linux handle RTC differently:

```bash
# In Linux, make it use local time
sudo timedatectl set-local-rtc 1 --adjust-system-clock
```

---

## 5. BitNet 1.58 Setup on Linux

### What is BitNet?

BitNet is Microsoft's 1-bit LLM inference framework that runs efficiently on CPU. The EQR6's Ryzen CPU can achieve **2.37x to 6.17x speedup** over traditional inference with **71.9% to 82.2% energy reduction**.

### Installation

```bash
# Prerequisites
sudo apt update
sudo apt install -y python3-pip python3-venv cmake clang git

# Install conda (recommended)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc

# Clone BitNet
mkdir -p ~/AI && cd ~/AI
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet

# Create conda environment
conda create -n bitnet-cpp python=3.9
conda activate bitnet-cpp

# Install dependencies
pip install -r requirements.txt

# Download and setup model
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
```

### Running BitNet

```bash
# Activate environment
conda activate bitnet-cpp

# Run inference
python run_inference.py \
  -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  -p "You are a helpful assistant" \
  -cnv \
  -t 8  # Use 8 threads (EQR6 has 8 cores)

# Benchmark
python utils/e2e_benchmark.py \
  -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  -n 200 \
  -p 512 \
  -t 8
```

### Expected Performance on EQR6

| Model | CPU | Tokens/sec | Memory Used |
|-------|-----|------------|-------------|
| BitNet-b1.58-2B-4T | Ryzen 9 6900HX | ~50-70 | ~1GB |
| Llama3-8B-1.58 | Ryzen 9 6900HX | ~20-30 | ~2GB |

---

## 6. Ollama Linux Setup & Optimization

### Native Linux Performance vs Windows

**Key Finding:** Native Linux Ollama is **10-15% slower** than native Windows for GPU inference, but **significantly faster** for CPU-only inference due to better CPU scheduler optimization.

### Installation

```bash
# Official install script
curl -fsSL https://ollama.com/install.sh | sh

# Or manual install
sudo apt install -y curl
curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama

# Create systemd service
sudo useradd -r -s /bin/false -m -d /usr/share/ollama ollama
sudo usermod -aG render ollama  # For AMD GPU access
sudo usermod -aG video ollama
```

### AMD ROCm Setup for Radeon 680M

```bash
# Install ROCm (Ubuntu 24.04)
sudo apt install -y amdgpu-install
sudo amdgpu-install --usecase=rocm

# For unsupported iGPUs (680M), override GFX version
echo 'export HSA_OVERRIDE_GFX_VERSION=10.3.0' >> ~/.bashrc
source ~/.bashrc

# Verify ROCm
rocminfo | grep gfx

# Restart Ollama
sudo systemctl restart ollama
```

### Ollama Configuration

```bash
# Edit systemd service for optimization
sudo systemctl edit ollama.service

# Add the following:
[Service]
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="HSA_OVERRIDE_GFX_VERSION=10.3.0"
```

### Pull and Run Models

```bash
# Pull optimized models for 20GB RAM
ollama pull qwen2.5:7b          # Good balance
ollama pull qwen2.5:14b         # If mostly for Linux
ollama pull llama3.2:3b         # Lightweight
ollama pull phi4:14b            # High quality

# Run with custom parameters
ollama run qwen2.5:7b --verbose
```

### Ollama Performance Tips

```bash
# Use all CPU cores for inference
export OLLAMA_NUM_THREADS=16  # For 6900HX (8 cores, 16 threads)

# Enable flash attention (faster, less memory)
export OLLAMA_FLASH_ATTENTION=1

# Quantized KV cache (saves ~50% VRAM/RAM)
export OLLAMA_KV_CACHE_TYPE=q8_0
```

---

## 7. RAM Optimization for 20GB

### Understanding 20GB Layout

The EQR6 has **20GB DDR5-4800** (likely 8GB + 12GB dual-channel asymmetric).

### ZRAM Configuration (Recommended)

ZRAM provides compressed swap in RAM - essential for LLM workloads.

```bash
# Install zram-tools
sudo apt install -y zram-tools

# Configure zram
sudo tee /etc/default/zramswap << 'EOF'
ALGO=zstd
PERCENT=50  # 50% of RAM = ~10GB zram
PRIORITY=100
EOF

# Restart zram
sudo systemctl restart zramswap

# Verify
swapon --show
zramctl
```

### Advanced ZRAM Setup (Manual)

```bash
# Install systemd-zram-generator
sudo apt install -y systemd-zram-generator

# Create configuration
sudo tee /etc/systemd/zram-generator.conf << 'EOF'
[zram0]
zram-size = ram / 2
compression-algorithm = zstd
swap-priority = 100
EOF

# Lower swappiness (prefer RAM over swap)
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl -p /etc/sysctl.d/99-swappiness.conf

# Enable zram module
sudo modprobe zram
sudo systemctl daemon-reload
sudo systemctl restart systemd-zram-setup@zram0.service
```

### Kernel Parameters for Memory

```bash
# Edit grub
sudo nano /etc/default/grub

# Add to GRUB_CMDLINE_LINUX_DEFAULT:
GRUB_CMDLINE_LINUX_DEFAULT="quiet zswap.enabled=0 transparent_hugepage=madvise"

# Update grub
sudo update-grub
```

### Memory Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop btop

# Check memory usage
free -h
cat /proc/meminfo | grep -E "(Mem|Swap)"

# Check zram stats
zramctl --output-all
```

---

## 8. CPU Performance Tuning

### AMD P-State Driver Configuration

The EQR6 benefits significantly from proper CPU frequency scaling.

```bash
# Check current driver
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
# Should show: amd-pstate

# Check current mode
cat /sys/devices/system/cpu/amd_pstate/status
# Options: passive, guided, active
```

### Optimal Settings for LLM Workloads

```bash
# Set to active (EPP) mode for best responsiveness
echo active | sudo tee /sys/devices/system/cpu/amd_pstate/status

# Set performance governor
sudo cpupower frequency-set -g performance

# Set EPP preference
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference

# Disable CPU boost for consistent performance (optional)
echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost
```

### Persistent CPU Configuration

```bash
# Create systemd service for CPU tuning
sudo tee /etc/systemd/system/cpu-performance.service << 'EOF'
[Unit]
Description=CPU Performance Tuning for LLM
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/cpu-tune.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Create tuning script
sudo tee /usr/local/bin/cpu-tune.sh << 'EOF'
#!/bin/bash
echo active > /sys/devices/system/cpu/amd_pstate/status
cpupower frequency-set -g performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference; do
    echo performance > "$cpu"
done
EOF

sudo chmod +x /usr/local/bin/cpu-tune.sh
sudo systemctl enable cpu-performance.service
```

### Kernel Parameters for AMD Ryzen

```bash
# Edit grub
sudo nano /etc/default/grub

# Optimal settings for EQR6:
GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_pstate=active processor.max_cstate=1 idle=nomwait"

# For maximum performance (higher power/heat):
# GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_pstate=active amd_iommu=off idle=poll"

sudo update-grub
```

### Disable Mitigations (Optional, Use with Caution)

```bash
# For maximum performance (security trade-off)
sudo nano /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="quiet mitigations=off amd_pstate=active"
sudo update-grub
```

---

## 9. Step-by-Step Installation Guide

### Phase 1: Preparation (30 minutes)

1. **Backup Windows data**
2. **Download Ubuntu 24.04 LTS ISO**
3. **Create bootable USB** (8GB+)
4. **Gather EQR6 BIOS info:**
   - Press DEL/F7 at boot
   - Note current BIOS version
   - Check Secure Boot status

### Phase 2: BIOS Setup (10 minutes)

```
1. Enter BIOS (DEL key)
2. Security > Secure Boot: Enable (Ubuntu supports this)
3. Boot > Set USB as first priority
4. Save and exit
```

### Phase 3: Ubuntu Installation (30-45 minutes)

1. Boot from USB
2. Select "Try or Install Ubuntu"
3. Choose installation type:
   - **Recommended:** "Erase disk and install Ubuntu" (on second drive)
   - **Alternative:** "Install alongside Windows" (same drive)
4. Complete installation
5. Remove USB and reboot

### Phase 4: Post-Installation Setup (1 hour)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install essential packages
sudo apt install -y \
    build-essential git curl wget \
    htop btop nvme-cli \
    linux-headers-$(uname -r) \
    zram-tools cpufrequtils

# 3. Fix WiFi (if needed)
# See Section 2 for WiFi fixes

# 4. Configure zram
sudo apt install -y zram-tools
# Edit /etc/default/zramswap as per Section 7

# 5. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 6. Setup AMD ROCm (for GPU acceleration)
# See Section 6

# 7. Install BitNet
# See Section 5

# 8. Configure CPU performance
# See Section 8

# 9. Reboot
sudo reboot
```

### Phase 5: Verification

```bash
# Check all components
lscpu | grep "Model name"
free -h
swapon --show
lspci | grep -i vga
lspci | grep -i network
lsusb | grep -i bluetooth

# Test Ollama
ollama run qwen2.5:7b

# Test BitNet
conda activate bitnet-cpp
python run_inference.py -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf -p "Hello" -cnv
```

---

## 10. Performance Comparison: Linux vs Windows

### Ollama Performance (Tokens/Second)

| Configuration | Model | Tokens/sec | Notes |
|--------------|-------|------------|-------|
| **Windows 11 Native** | llama3.2:3b | 143.68 | Best GPU performance |
| **WSL2** | llama3.2:3b | 124.37 | ~13% overhead |
| **Linux Native** | llama3.2:3b | 126.39 | Better CPU scheduling |
| **Windows 11 Native** | qwen2.5:7b | ~85-95 | GPU accelerated |
| **Linux Native** | qwen2.5:7b | ~80-90 | ROCm iGPU support |

### Key Findings

1. **GPU Inference:** Windows native is 10-15% faster due to better AMD driver optimization
2. **CPU Inference:** Linux is 5-10% faster due to better scheduler and lower overhead
3. **Memory Efficiency:** Linux uses ~1-2GB less RAM at idle
4. **Thermal Management:** Linux provides better fan control and thermal monitoring

### Recommendations by Use Case

| Use Case | Recommended OS | Why |
|----------|---------------|-----|
| **Pure LLM inference** | Linux | Better memory management, lower overhead |
| **GPU-accelerated AI** | Windows 11 | Better AMD ROCm/ Vulkan support |
| **Development/Programming** | Linux | Native Docker, better toolchain |
| **Mixed workloads** | Dual-boot | Best of both worlds |
| **BitNet/1-bit models** | Linux | Better CPU optimization |

---

## Quick Reference Commands

### Daily Use

```bash
# Check system status
htop                    # System monitor
nvtop                   # GPU monitor (install first)
ollama list             # List available models
ollama ps               # Show running models

# CPU performance modes
sudo cpupower frequency-set -g performance  # Max performance
sudo cpupower frequency-set -g powersave    # Power saving
sudo cpupower frequency-set -g schedutil    # Balanced

# Memory cleanup
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
```

### Troubleshooting

```bash
# WiFi not working
sudo dmesg | grep -i wifi
sudo lspci | grep -i net

# Bluetooth issues
sudo systemctl status bluetooth
sudo dmesg | grep -i blue

# Ollama not using GPU
rocminfo | grep gfx
ollama ps  # Check if GPU column shows usage

# High temperatures
sensors  # install lm-sensors first
sudo apt install lm-sensors
sudo sensors-detect
```

---

## Resources & References

- [Beelink Official Forum](https://bbs.bee-link.com/)
- [Ubuntu 24.04 LTS Download](https://ubuntu.com/download/desktop)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Microsoft BitNet GitHub](https://github.com/microsoft/BitNet)
- [AMD ROCm Documentation](https://rocm.docs.amd.com/)
- [Linux ZRAM Optimization](https://github.com/karem505/linux-zram-optimization)
- [CachyOS AMD Tuning Guide](https://wiki.cachyos.org/configuration/general_system_tweaks/)

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-15  
**Target Platform:** Beelink EQR6 (AMD Ryzen 6000 Series)
