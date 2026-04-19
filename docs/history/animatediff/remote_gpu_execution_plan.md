# 원격 GPU 실행 계획 문서

## 1. 문서 목적

이 문서는 로컬 `Mac mini M2 + MPS` 실험 실패 이후,
현재 마일스톤을 원격 GPU 환경에서 다시 실행하기 위한 기준 계획서다.

대상 독자:

- 다음 세션의 작업자
- RunPod 또는 Colab에서 직접 실험을 수행할 사람
- 이후 Docker 기반 재현 환경을 만들 작업자


## 2. 현재 상황 요약

현재 마일스톤의 핵심 질문은 아래와 같다.

`이전 scene의 마지막 프레임(init image)을 다음 scene 생성에 사용하면 연결이 더 자연스러워지는가?`

로컬 결론:

- 로컬 `Mac mini M2 + MPS`에서는 clip 품질이 너무 낮아 질문에 답할 수 없었다.
- 따라서 이번 실험은 원격 GPU 환경으로 이동해야 한다.

관련 실패 기록:

- [로컬 M2 clip 실험 실패 기록](../experiments/local_m2_clip_test_failure_2026-04-17.md)


## 3. 플랫폼 추천

### 3.1 1순위: RunPod

추천 이유:

1. 최종 목표 환경이 `NVIDIA GPU + CUDA` 기반이므로, 중간 검증도 같은 계열 환경에서 하는 편이 낫다.
2. Pod 기반으로 SSH, JupyterLab, 웹 터미널을 바로 사용할 수 있어 개발과 디버깅이 쉽다.
3. 향후 Docker image/template로 고정하면 재현성과 팀 공유가 좋아진다.

적합한 용도:

- 현재 마일스톤의 실제 clip 실험
- 이후 RunPod 본환경 구축
- 최종 서비스용 추론 환경 실험

공식 문서:

- RunPod Quickstart: https://docs.runpod.io/get-started
- Custom Pod Template: https://docs.runpod.io/pods/templates/create-custom-template
- Pricing: https://www.runpod.io/pricing


### 3.2 2순위: Google Colab

추천 이유:

1. 공식 FAQ 기준으로 Colab은 설정 없이 사용할 수 있는 hosted Jupyter 환경이며, 무료로 GPU/TPU 접근을 제공한다.
2. 로컬에서 안 되는 실험을 임시로 빨리 확인하는 용도로는 유용하다.

제약:

1. 무료 티어 자원은 보장되지 않는다.
2. GPU availability, usage limit, VM lifetime이 동적으로 바뀐다.
3. 콘텐츠 생성 용도로 notebook UI를 우회한 web UI 사용은 무료 티어에서 종료될 수 있다.
4. 장시간 안정 실행이나 운영 환경 기준으로는 적합하지 않다.

적합한 용도:

- 임시 테스트
- 빠른 프로토타이핑
- 아주 짧은 2-scene 재검증

공식 문서:

- Colab FAQ: https://research.google.com/colaboratory/intl/en-GB/faq.html


## 4. 추천 결론

이번 프로젝트 기준 추천 결론은 아래와 같다.

1. `무료로 한 번만 빨리 확인`이 목적이면 Colab을 먼저 시도할 수 있다.
2. `실제 결과를 믿고 다음 단계 설계까지 이어갈 실험`이라면 RunPod가 맞다.
3. 최종 목표가 RunPod 기반이므로, 가능하면 곧바로 RunPod에서 검증하는 편이 전체 비용과 시간을 줄인다.


## 5. Docker가 지금 당장 필요한가

결론:

`지금 당장은 필수 아니다.`

이유:

1. 현재 목표는 제품 배포가 아니라 `실험 재수행과 결과 검증`이다.
2. RunPod 공식 PyTorch template만으로도 Jupyter/SSH 기반 실험을 바로 시작할 수 있다.
3. 아직 패키지 조합, 모델 조합, 실행 명령이 완전히 고정되지 않았으므로 Docker를 먼저 만들면 오히려 반복 작업이 늘 수 있다.

따라서 단계는 아래처럼 가는 것이 맞다.

1. 1단계: RunPod 기본 Pod에서 수동 검증
2. 2단계: 실험이 통과하면 Docker image/template로 고정
3. 3단계: 필요 시 RunPod API 또는 서버리스/서비스 구조로 이동


## 6. 권장 실행 전략

### 6.1 Stage 1: RunPod 기본 Pod에서 직접 실행

목표:

- Docker 없이 가장 빨리 NVIDIA GPU에서 실험을 재실행한다.

권장 이유:

- 문제를 빨리 분리할 수 있다.
- 환경 문제인지, 모델/스크립트 문제인지 먼저 확인할 수 있다.
- 실패 시 바로 터미널에서 수정하고 다시 실행하기 쉽다.

권장 GPU 시작점:

- 1차 후보: `RTX 4090 24GB` 또는 `L4 24GB`
- 여유가 필요하면: `A40 48GB`, `RTX A6000 48GB`, `L40S 48GB`

참고:

- RunPod 공식 pricing 페이지에는 `L4 24GB`, `RTX 4090 24GB`, `A40 48GB`, `L40S 48GB` 등 다양한 선택지가 나와 있다.
- 현재 마일스톤은 2-scene 짧은 clip 실험이므로, 보통은 24GB급부터 시작해보고 부족하면 48GB로 올리는 접근이 합리적이다.


### 6.2 Stage 2: 환경이 안정되면 Docker image 도입

목표:

- 실험을 재현 가능하게 만들고, 다음 세션 작업자가 같은 환경을 즉시 재사용하게 한다.

도입 조건:

1. 패키지 목록이 안정되었을 때
2. 실행 명령이 고정되었을 때
3. 모델 다운로드 전략이 정리되었을 때

공식 RunPod 문서 기준:

- custom template는 Docker image를 기반으로 만들 수 있다.
- Mac에서 빌드할 때는 `docker build --platform linux/amd64 ...`를 사용해야 한다.


## 7. RunPod 실행 절차

### 7.1 가장 빠른 방법: 콘솔에서 Pod 생성

1. RunPod 계정 생성 및 결제 수단 등록
2. Pods 페이지에서 Deploy
3. GPU 선택
   - 시작 추천: `RTX 4090 24GB` 또는 `L4 24GB`
4. Template는 먼저 공식 `PyTorch` 계열 이미지 사용
5. Pod 실행 후 JupyterLab 또는 SSH 접속

공식 문서 기준:

- RunPod는 Pod에서 JupyterLab과 SSH 실행 경로를 제공한다.
- Quickstart 문서는 웹 UI와 CLI 둘 다 안내한다.


### 7.2 CLI 기반 예시

RunPod 공식 quickstart에는 아래 예시가 있다.

```bash
bash <(wget -qO- cli.runpod.io)
runpodctl config --apiKey "YOUR_API_KEY"
runpodctl pod create \
  --name "scene-transition-test" \
  --gpu-id "NVIDIA A40" \
  --image "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
```

이후:

```bash
export RUNPOD_POD_ID="YOUR_POD_ID"
runpodctl ssh info $RUNPOD_POD_ID
```

접속 후:

```bash
ssh root@YOUR_PUBLIC_IP -p YOUR_PORT
```


## 8. RunPod Pod 내부 권장 실행 절차

### 8.1 저장소 준비

```bash
git clone <REPO_URL>
cd AnimateDiff
```

### 8.2 Python 환경 준비

공식 PyTorch 이미지에는 Python과 PyTorch가 이미 들어 있는 경우가 많다.
실험 재현성을 위해 프로젝트 내부 가상환경을 다시 만드는 편이 안전하다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 8.3 최소 패키지 설치

현재 실험 스크립트 기준 최소 권장 패키지:

```bash
pip install \
  diffusers \
  transformers \
  accelerate \
  imageio \
  imageio-ffmpeg \
  safetensors \
  sentencepiece \
  pillow
```

주의:

- 기존 `requirements.txt`는 로컬 Mac에서 실패 이력이 있었으므로, 현재 마일스톤 검증에서는 `전체 requirements`보다 `실험에 필요한 최소 패키지`부터 설치하는 편이 안전하다.


### 8.4 1차 실행 권장 명령

처음부터 너무 높게 올리지 말고 2-scene 기준으로 시작한다.

```bash
python scripts/run_scene_transition_clip_test.py \
  --scene-count 2 \
  --width 384 \
  --height 384 \
  --num-frames 8 \
  --steps 12 \
  --fps 6
```

품질이 괜찮고 메모리 여유가 있으면 다음처럼 확장한다.

```bash
python scripts/run_scene_transition_clip_test.py \
  --scene-count 2 \
  --width 512 \
  --height 512 \
  --num-frames 12 \
  --steps 16 \
  --fps 8
```

확인 우선순위:

1. `reports/without_init_merged.mp4`
2. `reports/with_init_merged.mp4`
3. `reports/transition_comparison.mp4`


## 9. Colab 실행 절차

### 9.1 Colab을 언제 쓰는가

아래 조건이면 Colab을 임시 대안으로 쓸 수 있다.

1. 당장 무료로 한 번만 검증하고 싶다.
2. 세션 종료나 리소스 제한을 감수할 수 있다.
3. notebook 기반 수동 실험이 가능하다.

### 9.2 Colab에서 주의할 점

공식 FAQ 기준:

1. 무료 티어는 무료이지만 자원이 보장되지 않는다.
2. GPU availability와 usage limits가 변동적이다.
3. free tier는 최대 12시간 이내 런타임 제약이 있고 idle timeout이 있다.
4. free tier에서 notebook UI를 우회한 web UI 기반 content generation은 종료될 수 있다.

따라서 Colab에서는 아래 방식이 맞다.

1. notebook 셀에서 직접 명령 실행
2. 웹 UI를 띄우지 않음
3. 실험 결과를 Drive 또는 외부 저장소로 즉시 백업

### 9.3 Colab 셀 예시

```bash
!git clone <REPO_URL>
%cd AnimateDiff
!pip install --upgrade pip
!pip install diffusers transformers accelerate imageio imageio-ffmpeg safetensors sentencepiece pillow
!python scripts/run_scene_transition_clip_test.py --scene-count 2 --width 384 --height 384 --num-frames 8 --steps 12 --fps 6
```


## 10. 성공 기준

원격 GPU 전환 이후 이번 단계의 성공 기준은 아래와 같다.

1. scene 자체가 사람이 식별 가능한 수준으로 생성된다.
2. `without init` / `with init` merged clip을 비교할 수 있다.
3. init image가 인물/장소/구도 유지에 실제 도움을 주는지 정성 평가가 가능하다.
4. 결과를 문서로 남기고, 이후 3-scene 이상으로 확장할지 판단할 수 있다.


## 11. 다음 단계

원격 GPU 실험이 성공하면 다음 단계는 아래 순서가 적절하다.

1. scene 수를 3개 이상으로 늘린다.
2. 해상도와 프레임 수를 점진적으로 올린다.
3. 환경이 안정되면 Docker image와 RunPod custom template를 만든다.
4. 그 다음 story-to-scene 자동화, 실험 배치 실행, 최종 파이프라인 구조로 확장한다.
