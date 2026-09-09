# P1 model verification

- ✅ Detection inference model loaded from the existing `PP-OCRv6_medium_det/inference` and ran on `gpu:0`; output shape `[1,1,128,128]`, GPU place.
- ✅ Recognition inference model loaded from existing `PP-OCRv6_medium_rec/inference` and ran on `gpu:0`; output shape `[1,40,18710]`, GPU place.
- ⏳ CTC loss/backward: blocked for this run because the available artifact is inference-only (`inference.json` + `inference.pdiparams`), with no trainable checkpoint/config wired into the runtime. It cannot provide trainable parameters or gradients.

Observed Paddle warnings: installed Paddle reports cuDNN 8.9 compatibility warning; this must be resolved or explicitly accepted before release.
