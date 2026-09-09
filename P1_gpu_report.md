# P1 GPU environment report

- GPU: NVIDIA GeForce RTX 2070 SUPER, 8192 MiB
- Driver: 560.94
- OS/Python: Windows 64-bit, Python 3.11.9
- PaddlePaddle: 3.2.2, CUDA build: true
- Device count: 1, selected device: gpu:0
- Compute capability: 7.5
- Runtime/API observed: CUDA driver 12.6, runtime 11.8

## Minimal test

A real Paddle Linear forward, loss, backward, synchronization and parameter/gradient device assertions passed on `gpu:0`.

This proves base tensor CUDA and backward only. OCR model forward, image pipeline, postprocess and decoder remain unverified.
