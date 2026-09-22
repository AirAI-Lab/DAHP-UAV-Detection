# Highlights

1. **An exposure-aware regime-dependent rebalancing principle**: data-level rebalancing helps only when learnability and data-exposure headroom permit. Exact controls show a volume-dominated regime at 960 px, volume saturation with a targeted residual at 1280 px, a positive-sum window at 1600 px, and an exposure-limited apparent gain at 1920 px.

2. **A controlled negative-result study**: seven audited feature-module generations increase validation DFL and fail to provide a reliable AP improvement on the strong baselines used here.

3. **A label-only profiling mechanism followed by a bounded policy search**: DAHP maps long-tail, scale, and structural-confusion statistics to resolution/configuration and union-sampling policies without changing the detector's stock loss or inserting an inference-time module. The recipe transfers to UAVDT without retuning.

4. **Bounded, protocol-separated evidence**: DAHP-L reaches 38.16 md100 AP / 40.06 native AP on VisDrone val under the disclosed 1600-px/P2 policy. Same-input DAHP-M, modern DETR baselines, a negative matched RT-DETR probe, volume/exposure controls, and UAVDT transfer are reported separately to prevent overgeneralization.

5. **A complete latency audit**: on an exclusive desktop RTX 3090, DAHP-L measures 38.0 ms end-to-end and 26.3 FPS over 300 images, with preprocessing, inference, post-processing, pipeline residual, CUDA memory, and host-load provenance.
