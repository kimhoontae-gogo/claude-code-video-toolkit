# 실행 런북

## 1. 문서 목적

이 문서는 CogVideo 프로젝트를 로컬 또는 원격 GPU 환경에서 실행할 때 필요한 운영 메모를 관리한다.

현재 상태:

1. 저장소 clone 완료
2. upstream remote 제거 완료
3. CogVideo 기준 실험 wrapper는 아직 작성 전
4. RunPod Pod 배포는 `SSH + scp + bootstrap script` 방향으로 정리 중


## 2. 현재 기준 버전

- 브랜치: `main`
- 커밋: `7a1af7154511e0ce4e4be8d62faa8c5e5a3532d2`

선택 근거:

1. upstream release note상 `CogVideoX1.5` 계열은 `main` 또는 더 최신 릴리스 사용 권장
2. 따라서 이 프로젝트는 `main` 기준으로 시작


## 3. 앞으로 이 문서에 추가할 것

1. 로컬 환경 세팅 절차
2. Colab 실행 절차
3. RunPod 실행 절차
4. 결과물 다운로드/비교 절차


## 4. RunPod 기본 방향

RunPod Pod 환경에서는 `docker compose`를 Pod 내부에서 직접 실행하는 방식을 기본 경로로 두지 않는다.

현재 기본 방향:

1. 로컬에서 프로젝트 번들 생성
2. `scp`로 Pod에 업로드
3. 원격 bootstrap 스크립트로 `.venv`, Python 의존성, 디렉토리 구조 준비
4. 원격에서 shell command로 실험 실행
5. `scp`로 결과 다운로드

현재 배포 리소스 위치:

1. [deployments/runpod/README.md](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/README.md)
2. [deployments/runpod/create_pod.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/create_pod.sh)
3. [deployments/runpod/create_bundle.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/create_bundle.sh)
4. [deployments/runpod/upload_and_bootstrap.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/upload_and_bootstrap.sh)
5. [deployments/runpod/remote_exec.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/remote_exec.sh)
6. [deployments/runpod/download_outputs.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/download_outputs.sh)
7. [deployments/runpod/provision_and_run.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/provision_and_run.sh)
8. [deployments/runpod/fast_run.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/fast_run.sh)
9. [deployments/runpod/run_milestone1_fixed.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/run_milestone1_fixed.sh)
10. [deployments/runpod/provision_milestone1_fixed.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/provision_milestone1_fixed.sh)
11. [deployments/runpod/run_milestone1_e2e.sh](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/run_milestone1_e2e.sh)
12. [deployments/runpod/milestone1.fixed.env](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/milestone1.fixed.env)

가장 단순한 진입점:

```bash
./deployments/runpod/provision_and_run.sh "<pipeline command>"
```

이 스크립트는 아래를 순서대로 수행한다.

1. Pod가 없으면 새로 생성
2. SSH 준비 대기
3. 번들 업로드
4. 원격 bootstrap
5. 파이프라인 실행
6. 결과 다운로드


## 4.1 RunPod 장애 메모

최근 RunPod 실험에서 확인된 핵심 이슈는 아래 두 가지다.

1. Hugging Face 모델 캐시가 `/root/.cache/huggingface`로 내려가면서 루트 디스크가 먼저 가득 참
2. Pod 템플릿과 별도로 `torch`를 다시 설치하면 CUDA, `transformers`, `diffusers` 조합이 다시 깨질 수 있음

현재 대응:

1. 캐시 경로를 `workspace/cache/huggingface`로 강제 고정
2. RunPod bootstrap은 일반 `requirements.txt` 대신 [deployments/runpod/requirements.runpod.txt](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/requirements.runpod.txt)를 사용
3. RunPod 기본 템플릿은 `runpod-torch-v280`를 사용
4. bootstrap venv는 `--system-site-packages`로 생성해 템플릿에 포함된 PyTorch/CUDA 조합을 그대로 사용
5. Qwen-Image-Edit-2511 지원을 위해 RunPod 전용 requirements는 `diffusers==0.36.0`으로 고정
6. RunPod 전용 requirements는 현재 milestone 실행에 필요한 최소 패키지만 설치하도록 축소

추가 메모:

1. 현재 milestone 실행 기준으로 `gradio`, `openai`, `moviepy`, `scikit-video`, `pydantic`, `SwissArmyTransformer`는 RunPod bootstrap에서 제외했다.
2. 이유는 이번 경로가 웹 UI 실행이 아니라 `scripts/run_milestone1_pipeline.py` 단일 실험 실행이기 때문이다.
3. 불필요한 패키지를 빼면 설치 충돌과 bootstrap 시간이 함께 줄어든다.
4. bootstrap 마지막에 `torch`, `transformers`, `diffusers` import preflight를 실행해, 실제 추론 전에 버전 문제를 먼저 잡는다.
5. preflight에서 `scaled_dot_product_attention`의 `enable_gqa` 지원 여부를 확인해, Qwen 추론 전 호환성 실패를 즉시 탐지한다.
6. 24GB VRAM 환경에서는 이미지 파이프라인을 GPU에 통째로 올리지 않고 CPU offload로 동작하도록 스크립트 기본값을 설정했다.
7. 이미지 기본 해상도는 `1024x1024`이며 필요 시 `--image-width`, `--image-height`로 조절한다.
8. `python scripts/run_milestone1_pipeline.py` 실행 시 `inference` 모듈 import 실패를 막기 위해 스크립트가 프로젝트 루트를 `sys.path`에 강제로 추가한다.
9. bootstrap은 `.venv`와 모델 캐시를 재사용하며, requirements 해시가 변하지 않으면 `pip install`을 건너뛴다.
10. 반복 실험 시에는 `fast_run.sh` 또는 `RUNPOD_SKIP_BOOTSTRAP=1 RUNPOD_SKIP_DOWNLOAD=1`을 사용해 불필요한 단계(업로드/부트스트랩/다운로드)를 생략한다.
11. `upload_and_bootstrap.sh`는 번들 SHA256이 이전과 같으면 기본적으로 업로드/부트스트랩을 건너뛴다.
12. 필요하면 `RUNPOD_REUSE_EXISTING_BUNDLE=1`로 tar 재생성도 생략한다.
13. 실제 실행 결과는 `workspace/outputs/milestone1/<timestamp>/`에 저장된다.
14. dry-run 결과는 `workspace/outputs/milestone1/_dry_run/<timestamp>/` 아래에 생성되며, 기본값으로 실행 종료 시 자동 삭제된다.
15. dry-run 산출물을 남겨야 하면 `--keep-dry-run-artifacts`를 사용한다.
16. 다운로드 스크립트는 `--archive`(전체 outputs)와 `--latest-run`(최신 milestone run만) 압축 다운로드 옵션을 지원한다.
17. milestone1 baseline 재현은 `run_milestone1_fixed.sh`를 사용한다.
18. `run_milestone1_fixed.sh`는 실행 전에 `upload_and_bootstrap.sh`를 자동 호출해 최신 코드 반영을 확인한다.
19. milestone1 첫 실행/복구는 `provision_milestone1_fixed.sh`를 사용한다.
20. baseline 파라미터는 사용자 합의 없이 변경하지 않는다.
21. `run_milestone1_pipeline.py`는 Qwen 로드 시 `torch_dtype`를 우선 사용하고, 필요 시 `dtype`로 fallback한다.
22. Qwen image edit 단계에서 무의미하게 무시되던 `guidance_scale` 전달은 제거했다.
23. milestone1 baseline은 `video_model=THUDM/CogVideoX1.5-5B-I2V`를 사용한다.
24. milestone1 baseline은 `scene_image_source=prev_last_frame`를 사용해 씬 체인을 적용한다.
25. milestone1 baseline은 `video_condition_source=prev_last_frame`를 사용해 scene 2+에서 이전 씬 마지막 프레임을 I2V에 직접 입력한다.
26. I2V 렌더 시 `width/height`를 scene image와 동일하게 전달해(예: 768x768) 씬 이미지-비디오 비율 불일치로 인한 인물 왜곡을 줄인다.

즉, RunPod에서는 반드시 `provision_and_run.sh` 또는 `upload_and_bootstrap.sh`를 통해 bootstrap 해야 한다.
로컬과 동일하게 Pod 안에서 임의로 `pip install -r requirements.txt`만 실행하면 다시 같은 문제가 날 수 있다.


## 4.2 RunPod 디스크 조절

RunPod Pod의 디스크 크기는 웹 콘솔이 아니라 스크립트에서 바로 조절할 수 있다.

기본값:

1. `CONTAINER_DISK_GB=60`
2. `VOLUME_GB=160`

예시:

```bash
CONTAINER_DISK_GB=80 VOLUME_GB=200 ./deployments/runpod/create_pod.sh
```

구분:

1. `container disk`는 시스템 디스크 성격이다.
2. `volume`은 `/workspace`에 붙는 영속 볼륨이다.
3. 이 프로젝트는 모델 캐시와 출력물을 `/workspace` 아래에 두므로, 보통 `volume`을 더 크게 잡는 쪽이 효과적이다.


## 5. 참고자료

1. CogVideo README
   https://github.com/zai-org/CogVideo
2. CogVideo Releases
   https://github.com/zai-org/CogVideo/releases
3. Qwen-Image
   https://huggingface.co/Qwen/Qwen-Image
4. Qwen-Image-Edit-2511
   https://huggingface.co/Qwen/Qwen-Image-Edit-2511
5. RunPod CLI overview
   https://docs.runpod.io/runpodctl
6. RunPod file transfer
   https://docs.runpod.io/runpodctl/transfer-files
