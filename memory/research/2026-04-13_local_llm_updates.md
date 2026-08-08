# Local LLM Optimization Updates - April 2026

*Research conducted: April 13, 2026*

## Key Findings

### 1. Ollama AMD ROCm Support on Windows - STABLE
Ollama merged comprehensive ROCm support for Windows in PR #2885 (March 2024), with ongoing refinements through April 2026. The implementation:
- Uses ROCm v6 as the single supported version (dropped older gfx900/gfx906, added gfx1200/gfx1201 for RDNA4)
- Bundles ROCm dependencies into the Windows installer (~390MB separate download)
- Dynamically loads `amdhip64.dll` to query GPU info and gracefully degrade to CPU if ROCm is unavailable
- Windows ROCm builds are now standard in releases (see `ollama-windows-amd64-rocm.zip` in v0.6.7/v0.7.0)

### 2. llama.cpp AMD Optimization - SIGNIFICANT PROGRESS
Major performance breakthroughs for AMD RDNA4 (Radeon 9000 series) as of March-April 2026:
- **RDNA4 wave32 optimization**: Commit `3ae5466` (Feb 2026) added scalar flash attention using wave32 on AMD RDNA
- **Vulkan improvements**: PR #19976 (March 2026) improved partial offloading performance on AMD GPUs
- **Community benchmarks**: RDNA4 (R9700) achieves 156+ t/s on MoE models with optimized settings (`rm_kq=1`, PCIe ASPM performance mode)
- **Key optimization**: Setting `uint32_t rm_kq = 1` in `ggml-vulkan.cpp` reduces VGPR pressure, improving occupancy (+13% on AMDVLK dense decode)
- **PCIe ASPM**: Setting `pcie_aspm.policy=performance` eliminates L1 latency, boosting dense model decode by ~11%

### 3. OpenClaw Sandbox Isolation - PARTIAL FIX ATTEMPTED, THEN REVERTED
PR #41808 (March 2026) attempted to fix sandbox browser localhost access via network namespace sharing:
- **Problem**: Subagents couldn't reach localhost services (like Ollama) due to Docker network isolation
- **Solution attempted**: Browser container shares sandbox's network namespace (`--network=container:`)
- **Outcome**: PR was closed March 18, 2026 without merging due to security concerns
  - CDP port exposure on sandbox container created credential leak risk
  - SSRF policy relaxation could expose cloud metadata endpoints
  - Author recommended alternative: connect browser to same Docker network instead of namespace sharing
- **Status**: Subagent localhost access issues remain unresolved as of April 2026

## Recommendations

1. **For AMD GPU users**: Use Ollama's ROCm Windows build for native GPU acceleration. For maximum performance with llama.cpp, use RADV driver with `rm_kq=1` patch and PCIe ASPM performance mode.

2. **For OpenClaw users**: The `local-automation` agent + Ollama localhost issue persists. Continue using `agent:main` for Ollama tasks until OpenClaw implements a secure solution.

---
*Sources: Ollama GitHub releases/PRs, llama.cpp commits/discussions, OpenClaw PR #41808*