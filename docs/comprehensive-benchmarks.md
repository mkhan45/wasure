# Comprehensive Benchmark Selection

This document describes a curated set of 34 benchmarks designed to provide broad coverage of computational patterns relevant to WebAssembly runtime evaluation.

## Design Principles

1. **Minimize redundancy** - Avoid multiple benchmarks testing the same computational pattern
2. **Fill gaps** - Ensure coverage of patterns not represented by standard numerical suites
3. **Bias toward longer runtimes** - When benchmarks are redundant, prefer the longer-running one
4. **Real-world relevance** - Include actual applications, not just synthetic microbenchmarks

## Benchmark Categories

### wasm-r3: Real-World Applications (11 benchmarks)

These benchmarks are traces from real web-based WebAssembly applications. They have no WASI dependencies.

| Benchmark | Description | What It Tests |
|-----------|-------------|---------------|
| **jsc** | JavaScriptCore engine compiled to Wasm | Interpreter/JIT workload, complex control flow |
| **commanderkeen** | DOS game (Commander Keen) | Game loop, emulation, mixed workload |
| **funky-kart** | Racing game | Game physics, rendering logic |
| **sandspiel** | Falling sand physics simulation | Particle simulation, cellular automata |
| **ffmpeg** | Video/audio codec initialization | Media processing, codec startup |
| **pathfinding** | Graph pathfinding algorithm | Graph traversal, priority queues |
| **heatmap** | Heatmap visualization computation | Numerical computation, visualization |
| **figma-startpage** | Figma UI rendering | Real web application, UI framework |
| **sqlgui** | SQLite-based GUI application | Database operations, query processing |
| **uarm** | ARM CPU emulator | CPU emulation, instruction decoding |
| **visual6502remix** | 6502 CPU visual simulator | Hardware simulation, digital logic |

### PolyBench: Dense Numerical Computation (12 benchmarks)

Selected subset of PolyBench/C focusing on distinct computational patterns. Uses polybench-standalone (no WASI) or polybench (with WASI) versions.

| Benchmark | Category | Description | Runtime (wasmtime) |
|-----------|----------|-------------|-------------------|
| **gemm** | Matrix multiply | General matrix-matrix multiplication | 516ms |
| **2mm** | Matrix chain | D=A*B; E=D*C matrix chain | 935ms |
| **syr2k** | Matrix ops | Symmetric rank-2k update | 1.1s |
| **symm** | Matrix ops | Symmetric matrix-matrix multiply | 801ms |
| **lu** | Decomposition | LU decomposition | 9.2s |
| **cholesky** | Decomposition | Cholesky decomposition | 8.0s |
| **gramschmidt** | Orthogonalization | Gram-Schmidt orthogonalization | 2.1s |
| **jacobi-2d** | Stencil | 2D Jacobi stencil computation | 1.3s |
| **heat-3d** | Stencil | 3D heat equation solver | 2.3s |
| **adi** | Stencil | Alternating Direction Implicit solver | 5.5s |
| **floyd-warshall** | Dynamic programming | All-pairs shortest paths | 10.1s |
| **nussinov** | Dynamic programming | RNA secondary structure prediction | 1.6s |

**Removed for redundancy:**
- 3mm, syrk, trmm (redundant with gemm/2mm/syr2k)
- atax, bicg, gemver, gesummv, mvt (all <35ms, similar vector operations)
- ludcmp (nearly identical to lu)
- jacobi-1d, seidel-2d (similar to jacobi-2d)
- correlation, covariance (both <20ms, similar statistical ops)
- durbin, trisolv, doitgen (short runtime, less distinct patterns)

### Gap-Filling Benchmarks (11 benchmarks)

These benchmarks cover computational patterns not well-represented by wasm-r3 or PolyBench.

#### Pointer Chasing / Linked Structures

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **coremark** | CoreMark | Industry-standard embedded CPU benchmark. Internally tests linked list operations (insert, find, reverse, sort), matrix operations, state machine, and CRC. The linked list component provides pointer-chasing workload not covered elsewhere. |
| **coremark-5000** | CoreMark | CoreMark with 5000 iterations for longer runtime. Provides more stable measurements on fast runtimes. |

#### Sparse/Irregular Memory Access

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **spmv** | Ostrich | Sparse matrix-vector multiply. Tests indirect indexing and irregular memory access patterns - fundamentally different from dense PolyBench operations. |
| **page-rank** | Ostrich | PageRank graph algorithm. Iterative computation over graph structure with irregular access patterns. |

#### Backtracking and Recursion

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **nqueens** | Ostrich | N-Queens constraint satisfaction. Heavy recursion and backtracking - tests call stack and branch prediction. |

#### Machine Learning

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **back-propagation** | Ostrich | Neural network training. Different computational pattern from dense BLAS - includes activation functions, gradient computation. |

#### Bit Manipulation and Byte Processing

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **bitcnts-large** | MiBench | Population count algorithms. Tests bit manipulation operations. |
| **crc-large** | MiBench | CRC checksum computation. Byte-stream processing with table lookups. |

#### String and Text Processing

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **search-large** | MiBench | String pattern search. Text processing workload common in real applications. |

#### Cryptography

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **chacha20** | libsodium | ChaCha20 stream cipher. Crypto workload with bit operations, constant-time patterns. |

#### N-Body Physics

| Benchmark | Source | Description |
|-----------|--------|-------------|
| **nbody** | Cython-benchmarks | N-body gravitational simulation. O(n^2) all-pairs interaction - different from PolyBench stencils which have local neighborhoods. |

## Pattern Coverage Matrix

| Computational Pattern | Benchmarks |
|-----------------------|------------|
| Dense matrix operations | gemm, 2mm, syr2k, symm, lu, cholesky, gramschmidt |
| Stencil (regular neighbor access) | jacobi-2d, heat-3d, adi, heatmap |
| Dynamic programming | floyd-warshall, nussinov |
| Sparse/irregular memory | spmv, page-rank |
| Pointer chasing / linked structures | coremark, coremark-5000 |
| Graph algorithms | pathfinding, page-rank, floyd-warshall |
| Backtracking/recursion | nqueens |
| Bit manipulation | bitcnts-large, chacha20 |
| String/byte processing | crc-large, search-large |
| N-body/particle simulation | nbody, sandspiel |
| Machine learning | back-propagation |
| Emulation/interpretation | jsc, uarm, visual6502remix, commanderkeen |
| Game loops | funky-kart, sandspiel |
| Real web applications | figma-startpage, sqlgui, ffmpeg |

## Removed Benchmarks and Rationale

### From wasm-r3 (12 removed)

| Benchmark | Reason |
|-----------|--------|
| boa | Redundant with jsc (both JS engines; jsc runs longer) |
| fib | Trivial microbenchmark - only tests call overhead |
| multiplyInt | Pure arithmetic microbenchmark - not representative |
| multiplyDouble | Pure arithmetic microbenchmark - not representative |
| game-of-life | Redundant with sandspiel (sandspiel is longer, more complex) |
| kittygame | Redundant with other games |
| ogv | Redundant with ffmpeg (both video codecs) |
| video | Redundant with ffmpeg |
| riconpacker | Redundant with guiicons |
| rtexviewer | Redundant with guiicons |
| guiicons | Less unique than other benchmarks |
| handy-tools | Unclear workload |

### From PolyBench (17 removed)

| Benchmark | Reason |
|-----------|--------|
| 3mm | Redundant with 2mm (2mm is longer: 935ms vs 143ms) |
| syrk | Redundant with syr2k (syr2k is longer: 1.1s vs 410ms) |
| trmm | Redundant with gemm family |
| atax | Too fast (28ms), redundant vector operation |
| bicg | Too fast (24ms), redundant vector operation |
| gemver | Too fast (30ms), redundant vector operation |
| gesummv | Too fast (6ms), redundant vector operation |
| mvt | Too fast (30ms), redundant vector operation |
| ludcmp | Nearly identical to lu |
| jacobi-1d | Too fast (13ms), redundant with jacobi-2d |
| seidel-2d | Redundant with jacobi-2d |
| correlation | Too fast (18ms) |
| covariance | Too fast (17ms), similar to correlation |
| durbin | Too fast (14ms) |
| trisolv | Too fast (20ms) |
| doitgen | Medium priority, cut for space |
| deriche | Not in test results |

### Other Suites Not Included

| Suite | Reason |
|-------|--------|
| Dhrystone | Dated benchmark, integer performance covered by emulators |
| FFT (MiBench/Ostrich) | Partially redundant with PolyBench stencils |
| Most libsodium | 70+ benchmarks with heavy redundancy; chacha20 is representative |

## Potential Future Additions

If additional coverage is needed, consider:

| Benchmark | Source | Gap It Would Fill |
|-----------|--------|-------------------|
| binary-trees | Shootout | Allocation-heavy tree construction/destruction |
| bzip2 | Embench/SPEC | Compression algorithms |
| json-parse | Custom | Parsing (common web workload) |
| regex | Shootout | Regular expression matching |
| quicksort | Embench | Comparison-based sorting |
| hmm | Ostrich | Hidden Markov Models |

## Running the Benchmarks

```bash
# Run all comprehensive benchmarks on a specific runtime
wasure run -b wasm-r3 polybench-standalone ostrich mibench coremark -r wasmtime

# Run specific gap-filling benchmarks
wasure run -b coremark/coremark coremark/coremark-5000 \
           ostrich/spmv ostrich/nqueens ostrich/page-rank ostrich/back-propagation \
           mibench/bitcnts-large mibench/crc-large mibench/search-large \
           libsodium/chacha20 cython-benchmarks/nbody -r wasmtime
```

## Summary

| Category | Count | Source |
|----------|-------|--------|
| Real-world applications | 11 | wasm-r3 |
| Dense numerical | 12 | PolyBench |
| Gap-filling | 11 | CoreMark, Ostrich, MiBench, libsodium, Cython |
| **Total** | **34** | |

This selection reduces the original 52+ benchmarks to 34 while maintaining comprehensive coverage of computational patterns relevant to WebAssembly runtime evaluation.
