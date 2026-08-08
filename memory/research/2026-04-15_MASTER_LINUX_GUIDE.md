# MASTER COMPILATION: Beelink EQR6 Linux Dual-Boot for Local LLMs

## Complete Research Summary for Review

### Your System Specifications
- **PC:** Beelink EQR6 (AZW EQ mini PC)
- **CPU:** AMD Ryzen 7 7735HS (8 cores, 16 threads, 3.2-4.75 GHz, Zen 3+)
- **RAM:** 20GB DDR5 (~12GB available after Windows overhead)
- **GPU:** Integrated AMD Radeon 680M (12 CUs, 2200MHz)
- **Storage:** NVMe SSD (2x M.2 slots available)
- **OS:** Windows 11 Pro (current)
- **Goal:** Dual-boot with Linux for maximum local LLM performance

---

## PART 1: DUAL-BOOT SETUP GUIDE

### Phase 1: Pre-Installation (Windows Preparation)

**Step 1: Backup Recovery Key**
```powershell
# Run in Windows PowerShell (Admin)
manage-bde -protectors -get C:
# Save this 48-digit recovery key to USB/external device
```

**Step 2: Suspend BitLocker (Critical)**
```powershell
# Suspend BitLocker (re-enables after reboot unless disabled)
Suspend-BitLocker -MountPoint "C:" -RebootCount 0

# Or disable completely (takes hours to decrypt)
manage-bde -off C:
```

**Step 3: Disable Fast Startup**
Control Panel → Power Options → "Choose what the power buttons do" → "Change settings unavailable" → Uncheck "Turn on fast startup"

**Step 4: Shrink Windows Partition**
Disk Management → C: Drive → Shrink Volume
- Allocate 120-150GB for Linux (minimum 100GB for LLM models + system)
- 20GB RAM means aggressive swap/compression needed

### Phase 2: BIOS Configuration (Beelink EQR6)

Press ESC repeatedly at boot to enter AMI BIOS:
- Boot → Boot List Option: Set to UEFI (disable CSM/Legacy)
- Security → Secure Boot: Disable (or set to "Other OS")
- Security → TPM: Enabled (required for Windows 11, Linux can use it)
- Advanced → CPU Configuration → SVM Mode: Enabled (for virtualization if needed)
- Save & Exit → F4 → Yes

### Phase 3: Linux Installation

**Recommended Distro:** Ubuntu 24.04 LTS (best hardware support for Beelink mini PCs)

1. Create bootable USB with Rufus (Windows) or balenaEtcher
2. Boot from USB (F7 for Beelink boot menu, or ESC → Boot Override)
3. Select "Try or Install Ubuntu"
4. Language/Keyboard → Connect WiFi (Intel AX200 should work immediately)
5. Installation Type: Select "Install Ubuntu alongside Windows Boot Manager"
6. Advanced Features → "Use LVM and encryption" (for LUKS full-disk encryption)
7. Set encryption passphrase (different from user password)
8. Complete installation, reboot

**Post-Installation BitLocker Re-enable:**
```powershell
# In Windows, re-enable BitLocker after successful Linux boot
Resume-BitLocker -MountPoint "C:"
```

### Phase 4: Post-Installation Setup (1 hour)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install build-essential git cmake htop neofetch lm-sensors

# Install AMD microcode updates
sudo apt install amd64-microcode

# Configure zram (CRITICAL for 20GB systems)
sudo apt install zram-tools
sudo nano /etc/default/zramswap
# Set: ALGO=zstd, PERCENT=50

# Apply kernel parameters
sudo nano /etc/sysctl.d/99-llm-optimization.conf
# Add: vm.swappiness=10, vm.max_map_count=1048576
sudo sysctl --system

# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

---

## PART 2: OLLAMA & BITNET 1.58 SETUP

### Ollama Native Linux Installation

```bash
# Official Ollama install script (Linux native)
curl -fsSL https://ollama.com/install.sh | sh

# Verify AVX2 support (Ryzen 7735HS supports AVX2)
grep avx2 /proc/cpuinfo  # Should return multiple lines

# Check service status
sudo systemctl status ollama
```

### CPU-Only Optimization for 20GB RAM

Create optimized environment configuration:
```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

Add this configuration:
```ini
[Service]
Environment="OLLAMA_NUM_THREADS=16"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_MAX_MEMORY=18"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="OLLAMA_CPU_ONLY=true"
Environment="OLLAMA_AVX2=1"
Environment="OLLAMA_SCHED_SPREAD=true"
```

Explanation for 7735HS + 20GB:
- `OLLAMA_NUM_THREADS=16`: Use all 16 threads (8 cores SMT)
- `OLLAMA_MAX_MEMORY=18`: Reserve 18GB for models (2GB for Linux system + zram overhead)
- `OLLAMA_SCHED_SPREAD=true`: Spread load across all NUMA nodes (beneficial for Zen 3+)

```bash
# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### BitNet 1.58 Setup

**Available Models (HF1BitLLM):**
| Model | Parameters | HuggingFace Repo |
|-------|------------|------------------|
| Llama3-8B-1.58-100B-tokens | 8B | `HF1BitLLM/Llama3-8B-1.58-100B-tokens` |
| Llama3-8B-1.58-Linear-10B-tokens | 8B | `HF1BitLLM/Llama3-8B-1.58-Linear-10B-tokens` |

**Build from Source:**
```bash
# Install dependencies
sudo apt install build-essential cmake python3-pip git
pip install torch transformers huggingface-hub

# Clone and build
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet

# Setup environment (downloads model automatically)
python setup_env.py --hf-repo HF1BitLLM/Llama3-8B-1.58-100B-tokens -q i2_s

# Build optimized binary
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

**Run Inference:**
```bash
# Interactive mode
./build/bin/bitnet -m models/Llama3-8B-1.58-100B-tokens/ggml-model-i2_s.gguf -cnv

# Specific prompt
./build/bin/bitnet \
  -m models/Llama3-8B-1.58-100B-tokens/ggml-model-i2_s.gguf \
  -p "Explain quantum computing" \
  -n 256 \
  -t 16 \
  -c 4096
```

**Performance Expectations:**
- Llama3-8B-1.58: ~18-25 t/s on Ryzen 7735HS (vs ~8-12 t/s for Q4_K_M)
- RAM usage: ~1.6GB for 8B 1.58-bit model (vs ~5.5GB for Q4_K_M)
- Quality: Equivalent to Q4_K_M or slightly better (100B tokens fine-tuned)

**Important:** BitNet uses custom GGUF format (i2_s) that Ollama doesn't natively support. Use `bitnet.cpp` directly or convert to Q4_K_M for Ollama (loses speed benefits).

---

## PART 3: MODEL RECOMMENDATIONS FOR 20GB RAM

### Tier 1: 7B-9B Class (Primary Workhorses)

| Model | Size (Q4_K_M) | Tokens/s (Expected) | Best For | Priority |
|-------|---------------|---------------------|----------|----------|
| Qwen 2.5 7B | ~4.7 GB | 15-25 | Coding, multilingual | ⭐ Must-have |
| Llama 3.1 8B | ~5.5 GB | 12-20 | General English, reasoning | ⭐ Must-have |
| Gemma 3 8B | ~5.0 GB | 18-30 | Speed, Google ecosystem | ⭐ Must-have |
| Mistral 7B v0.3 | ~4.5 GB | 20-35 | Fast iteration, instruction following | Nice-to-have |

### Tier 2: 14B Class (Quality Leap)

| Model | Size (Q4_K_M) | VRAM/RAM Need | Tokens/s | Best For |
|-------|---------------|---------------|----------|----------|
| Qwen 2.5 14B | ~9.0 GB | 10.7 GB total | 8-15 | Complex coding, reasoning |
| Phi-4 14B | ~9.0 GB | 11 GB total | 8-12 | Microsoft's best small model |
| Qwen 3 14B | ~9.3 GB | 11 GB total | 8-14 | Hybrid thinking mode |

### Decision Matrix for 20GB RAM:

**Maximum versatility:** Qwen 2.5 14B Q4_K_M (~9GB) + Llama 3.1 8B Q4_K_M (~5.5GB) = ~14.5GB (fits with room for system)

**Maximum speed:** Gemma 3 8B Q4_K_M (~5GB) at 25-35 t/s

**Maximum coding quality:** Qwen 2.5 Coder 14B Q4_K_M (~9GB) scores 85%+ on HumanEval

**Best for reasoning:** Qwen 3 14B with thinking mode (~9.3GB)

### Quantization Recommendations

For 20GB RAM system:

| Model Size | Recommended Quant | Quality Retention | RAM Needed |
|------------|-------------------|-------------------|------------|
| 7B-8B | Q5_K_M | ~97% | 15-20% more than Q4 |
| 7B-8B | Q4_K_M (default) | ~92% | Baseline |
| 14B | Q4_K_M | ~92% | ~9-10 GB |
| 14B | Q5_K_M | ~97% | ~10.5-12 GB (tight fit) |

**Rule:** Prefer larger model at Q4 over smaller model at Q8. A 14B Q4_K_M beats 7B Q8_0 on most tasks.

### Context Length Trade-offs

Each additional 1K tokens adds ~0.5-0.8GB for 14B models:

| Context | RAM Overhead (14B) | Use Case |
|---------|-------------------|----------|
| 4K | +0 GB (baseline) | Chat, short code |
| 8K | +0.8-1.2 GB | Document analysis |
| 16K | +2-2.5 GB | Long code review |
| 32K | +4-5 GB | Book summarization (tight on 20GB) |

**Recommendation for 20GB:** Run 8B models at 8K context, 14B models at 4K context.

---

## PART 4: PERFORMANCE COMPARISON (Linux vs Windows)

### Expected Token Speeds (Native Linux, CPU-Only)

Based on llama.cpp benchmarks on Ryzen 7 7735HS (Zen 3+, AVX2):

| Model | Quantization | Context | Prompt t/s | Generation t/s | RAM Used |
|-------|--------------|---------|------------|----------------|----------|
| Llama 3.1 8B | Q4_K_M | 4K | ~10-15 | 8-12 | ~5-6 GB |
| Llama 3.1 8B | Q5_K_M | 4K | ~9-13 | 7-10 | ~6-7 GB |
| Qwen 2.5 14B | Q4_K_M | 4K | ~6-9 | 4-6 | ~9-10 GB |
| Qwen 2.5 14B | Q5_K_M | 4K | ~5-8 | 3.5-5 | ~11-12 GB |
| Llama 3.1 70B | Q4_K_M | 2K | N/A | Won't fit | >38 GB |

### Windows 11 Comparison

Same hardware, different OS:

| Configuration | Llama 3.1 8B Q4_K_M | Qwen 2.5 14B Q4_K_M | Notes |
|---------------|---------------------|---------------------|-------|
| Native Linux | 8-12 t/s | 4-6 t/s | ✅ Baseline |
| Windows 11 Native | 6-9 t/s | 3-4.5 t/s | Worse thread scheduling, Defender overhead |
| WSL2 | 7-10 t/s | 3.5-5 t/s | Good, but 5-10% virtualization overhead |
| Windows + GPU (ROCm) | 10-15 t/s | 5-8 t/s | 680M iGPU with ROCm, memory bandwidth limited |

**Recommendation:** Native Linux provides lowest latency and best memory efficiency for CPU-bound inference with 20GB RAM.

---

## PART 5: TESTING & MIGRATION STRATEGY

### Testing Phase Overview

**Strategy:** Run identical Ollama + OpenClaw configurations on both OSes for 3-7 days each.

**Important Context:**
- Two Karen systems will NOT overlap or sync — they are separate instances
- After evaluation, migrate FULLY to whichever OS performs better
- Timeline: 1-2 weeks testing, then commit to one OS

### Ollama Model Migration (Windows ↔ Linux)

**Option A: Direct Copy (Fastest for same network)**
```bash
# On Linux (destination), create the models directory
mkdir -p ~/.ollama/models

# From Windows (source), copy via network share or USB
# Windows path: C:\Users\Karen\.ollama\models\
# Copy both 'blobs' and 'manifests' directories

# After copying, fix permissions
sudo chown -R $USER:$USER ~/.ollama/models
```

**Option B: Archive/Export (For external transfer)**
```bash
# On source machine (creates portable archive)
cd ~/.ollama/models
tar -czvf ~/ollama-models-backup.tar.gz manifests/ blobs/

# Transfer to new machine via USB/scp
# On destination:
cd ~/.ollama/models
tar -xzvf /path/to/ollama-models-backup.tar.gz
```

**Critical:** Ollama must be stopped during copy to prevent database corruption:
```bash
# Linux
sudo systemctl stop ollama

# Windows (PowerShell Admin)
Stop-Process -Name "ollama" -Force
```

### OpenClaw Configuration Migration

OpenClaw stores all state in `~/.openclaw/` (Linux) or `%USERPROFILE%\.openclaw\` (Windows).

**Migration Checklist:**
```bash
# 1. Stop OpenClaw on source
openclaw gateway stop

# 2. Archive the entire directory
tar -czvf ~/openclaw-migration.tar.gz ~/.openclaw/

# 3. Transfer to destination

# 4. Extract on destination (Linux)
tar -xzvf ~/openclaw-migration.tar.gz -C ~/

# 5. Fix path differences in openclaw.json
nano ~/.openclaw/openclaw.json
# Replace Windows paths: C:\Users\Karen\ → /home/karen/
# Use double backslashes for JSON escaping

# 6. Update allowed origins if IP changed
# Edit gateway.controlUi.allowedOrigins

# 7. Run doctor to verify
openclaw doctor --fix
```

### Evaluation Metrics

| Metric | How to Measure | Target (Linux Native) | Windows Baseline |
|--------|----------------|----------------------|------------------|
| Prompt Processing | `llama-bench -p 512` | ~40-60 t/s | ~35-50 t/s |
| Token Generation | `llama-bench -n 128` | ~8-12 t/s (8B) | ~6-9 t/s (8B) |
| RAM Usage | `free -h` during run | <16GB for 14B | Similar |
| CPU Temp | `sensors` | <85°C sustained | <85°C sustained |
| Stability | 24-hour uptime test | 100% | 100% |

### Testing Protocol (3-7 Days Each OS)

- **Day 1:** Installation + basic benchmark
- **Day 2-3:** Daily driver usage (coding, writing, analysis)
- **Day 4:** Stress test (continuous inference for 2 hours)
- **Day 5:** Memory leak test (check `free -h` over time)
- **Day 6:** Suspend/resume stability (if enabled)
- **Day 7:** Final benchmark comparison

**Decision Criteria:**
- Performance: >15% speed advantage = significant
- Stability: Any crash = major penalty
- Convenience: Model availability, tool integration

---

## PART 6: AUTOMATION & DAILY WORKFLOW

### Systemd Service for Ollama (Auto-start with Optimizations)

Create `/etc/systemd/system/ollama-optimized.service`:
```ini
[Unit]
Description=Ollama Optimized for EQR6 20GB
After=network.target

[Service]
Type=simple
User=karen
Environment="OLLAMA_NUM_THREADS=16"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_MAX_MEMORY=18"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="OLLAMA_SCHED_SPREAD=true"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl disable ollama  # Disable default
sudo systemctl enable ollama-optimized
sudo systemctl start ollama-optimized
```

### Performance/Powersave Toggle Script

Create `~/toggle-performance.sh`:
```bash
#!/bin/bash
# Toggle between performance (LLM inference) and powersave (daily use)

MODE=${1:-performance}

if [ "$MODE" = "performance" ]; then
    echo "Setting PERFORMANCE mode for LLM inference..."
    
    # CPU governor
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
    
    # ZRAM priority (ensure compressed swap is active)
    sudo swapon -p 100 /dev/zram0
    
    # Ollama optimized service
    sudo systemctl restart ollama-optimized
    
    # Disable sleep/suspend
    sudo systemctl mask sleep.target suspend.target
    
    echo "Performance mode active. CPU locked at high frequency, sleep disabled."
    
elif [ "$MODE" = "powersave" ]; then
    echo "Setting POWERSAVE mode for daily use..."
    
    # CPU governor
    echo schedutil | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
    
    # Re-enable sleep
    sudo systemctl unmask sleep.target suspend.target
    
    # Standard Ollama service
    sudo systemctl restart ollama
    
    echo "Powersave mode active. CPU scaling enabled, sleep available."
else
    echo "Usage: $0 [performance|powersave]"
    exit 1
fi
```

Usage:
```bash
# Before heavy LLM work
~/toggle-performance.sh performance

# When done
~/toggle-performance.sh powersave
```

### Complete Benchmark Suite

Create `~/eqr6-test-suite.sh`:
```bash
#!/bin/bash
# Complete EQR6 Testing Suite for Windows vs Linux comparison

RESULTS_DIR="$HOME/eqr6-benchmarks-$(date +%Y%m%d)"
mkdir -p $RESULTS_DIR

# Test Configuration
MODELS=("llama3.1:8b" "qwen2.5:14b")
DURATION=300  # 5 minutes per test

echo "Starting EQR6 Test Suite..."

# Pull models if not present
for model in "${MODELS[@]}"; do
    echo "Ensuring $model is available..."
    ollama pull $model
done

# Run benchmarks
for model in "${MODELS[@]}"; do
    echo "Testing $model..."
    
    # Warm-up
    ollama run $model "Hello" > /dev/null 2>&1
    
    # Actual test
    time (ollama run $model "Write a detailed analysis of climate change impacts on agriculture:" --verbose) \
        > "$RESULTS_DIR/${model//:/-}.log" 2>&1
    
    sleep 30  # Cool down between tests
done

echo "All tests complete. Results in $RESULTS_DIR"
```

---

## PART 7: BACKUP & RECOVERY

### Timeshift Configuration (System Snapshots)

```bash
# Install
sudo apt install timeshift

# Configure via CLI (for 20GB system)
sudo timeshift --create --comments "Initial clean install"

# Recommended: Keep 5 daily, 3 weekly, 2 monthly
sudo nano /etc/timeshift/timeshift.json
# Modify retention policy
```

**Critical Exclusions (add to `/etc/timeshift/timeshift.json`):**
```json
"exclude": [
    "/home/karen/.ollama/models/**",
    "/home/karen/.openclaw/sessions/**",
    "/mnt/shared/**"
]
```

### Automated Model Backup Script

Create `~/backup-models.sh`:
```bash
#!/bin/bash
# Weekly backup of Ollama models to external drive

SOURCE="$HOME/.ollama/models"
DEST="/mnt/external/ollama-backup-$(date +%Y%m%d).tar.gz"
LOG="$HOME/backup.log"

echo "[$(date)] Starting model backup..." >> $LOG

# Check if external drive mounted
if [ ! -d "/mnt/external" ]; then
    echo "[$(date)] ERROR: External drive not mounted" >> $LOG
    exit 1
fi

# Stop Ollama to ensure consistency
sudo systemctl stop ollama

# Create backup
tar -czf $DEST -C "$SOURCE" .

# Restart Ollama
sudo systemctl start ollama

# Verify
if [ -f "$DEST" ]; then
    size=$(du -h $DEST | cut -f1)
    echo "[$(date)] Backup complete: $size" >> $LOG
else
    echo "[$(date)] ERROR: Backup failed" >> $LOG
fi

# Keep only last 3 backups
ls -t /mnt/external/ollama-backup-*.tar.gz | tail -n +4 | xargs -r rm
```

Cron job:
```bash
# Weekly at 2 AM
0 2 * * 0 /home/karen/backup-models.sh
```

### Emergency "Nuke Linux" Recovery

If Linux fails catastrophically and you need to revert to Windows-only:

1. Boot from Windows 11 USB installer
2. Choose "Repair your computer" → "Troubleshoot" → "Command Prompt"
3. Execute:
```cmd
diskpart
list disk
select disk 0  # Your NVMe
list partition
select partition X  # Your Linux partition
delete partition override
select partition Y  # Your EFI partition
assign letter=S:
exit

bcdboot C:\Windows /s S: /f UEFI
bootrec /fixmbr
bootrec /fixboot
bootrec /rebuildbcd
```

4. Remove Linux bootloader entries from BIOS
5. Expand Windows partition via Disk Management

---

## PART 8: TROUBLESHOOTING

### Common EQR6 + Linux Problems

| Issue | Fix |
|-------|-----|
| WiFi 6 (AX200) dropping connection | Disable power saving: `sudo nano /etc/NetworkManager/NetworkManager.conf` → add `wifi.powersave = 2` |
| Audio crackling over Bluetooth 5.2 | Use PipeWire instead of PulseAudio |
| HDMI audio not detected | `sudo apt install alsa-firmware-sof` |
| Sleep/Suspend not working | Beelink EQR6 has S3 sleep issues: `sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target` |
| High idle power consumption | Enable AMD P-State and ASPM: add `amd_pstate=active pcie_aspm=force` to GRUB_CMDLINE_LINUX_DEFAULT |

### Specific Error Messages & Fixes

| Error | Meaning | Fix |
|-------|---------|-----|
| `out of memory` | zram insufficient or model too large | Increase zram PERCENT to 60, or use smaller model |
| `illegal instruction` | CPU doesn't support AVX2 | Run `grep avx2 /proc/cpuinfo` (7735HS does, check virtualized?) |
| `failed to create context` | Ollama can't allocate RAM | Check `OLLAMA_MAX_MEMORY` not exceeding 18 |
| `BitLocker recovery` | Windows sees boot change | Enter 48-digit key, suspend BitLocker before Linux updates |
| `no such file or directory` (OpenClaw) | Path mismatch after migration | Run `openclaw doctor --fix` |

### GRUB Rescue Commands

If you see `grub rescue>` prompt:
```bash
# Find boot partition
ls  # List partitions
ls (hd0,gpt1)/  # Check contents

# Set prefix and root
set prefix=(hd0,gpt2)/boot/grub
set root=(hd0,gpt2)
insmod normal
normal  # Should show GRUB menu

# Boot to Linux and repair
sudo update-grub
sudo grub-install /dev/nvme0n1
```

---

## SUMMARY: PRIORITY CHECKLIST

### Must-Have (Before Testing Starts)
- [ ] Dual-boot installation complete
- [ ] Ollama installed on both OSes with identical models
- [ ] BitNet 1.58 built and tested on Linux
- [ ] Benchmark script copied to both systems
- [ ] Temperature monitoring working (`sensors` command)
- [ ] zram configured at 50% (10GB)

### Nice-to-Have (During Testing)
- [ ] Timeshift snapshots enabled
- [ ] Automated backup script configured
- [ ] Performance/powersave toggle script
- [ ] OpenClaw migrated with session history
- [ ] Shared partition auto-mounted

### Decision Point (After 1-2 Weeks)
- [ ] Benchmark reports compared
- [ ] Subjective daily usage experience logged
- [ ] Stability issues documented
- [ ] Migration plan executed to chosen OS

---

**Final Recommendation:** Given your 20GB constraint and the 7735HS's strong AVX2 performance, expect Linux native to win by 15-25% on token throughput. The critical differentiator will be memory management—Linux's zram + OOM handling should provide more consistent performance under heavy 14B model load versus Windows' memory compression.

**Expected Timeline:** 3-4 hours for complete setup, 1-2 weeks for testing, then full migration to winning OS.

**Risk Level:** Medium (BitLocker recovery key required, backup critical data)
