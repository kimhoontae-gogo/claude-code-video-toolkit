# 실행 커맨드 치트시트

이 문서는 RunPod에서 milestone1을 반복 실행할 때 필요한 커맨드만 모아둔 문서다.

## 1) 가장 자주 쓰는 기본 실행

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/run_milestone1_fixed.sh b1g4k7cdxgeoof
```

Pod ID를 생략하면 실행 중인 Pod가 1개라고 가정하고 자동 선택한다.

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/run_milestone1_fixed.sh
```

기본 동작:

1. 실행 전에 `upload_and_bootstrap.sh`를 자동 호출해 최신 코드 반영을 확인한다.
2. 번들/requirements 변경이 없으면 내부 해시 체크로 업로드/설치를 자동 스킵한다.
3. 기본 video 모델은 `THUDM/CogVideoX1.5-5B-I2V`다.
4. 기본 scene image source는 `prev_last_frame`이며, scene N의 마지막 프레임을 scene N+1 조건 입력으로 사용한다.
5. 기본 video condition source도 `prev_last_frame`이라서 scene 2+는 이미지 편집 단계를 건너뛰고 이전 씬 마지막 프레임을 I2V에 직접 입력한다.
6. baseline 해상도는 `1360x768`이며, scene image 생성과 I2V 렌더 해상도를 동일하게 유지한다.

동기화 생략(정말 빠른 재실행만 필요할 때):

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/run_milestone1_fixed.sh --no-sync b1g4k7cdxgeoof
```

## 2) 결과 다운로드

최신 1회 실행 결과만 압축 다운로드:

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/download_outputs.sh --latest-run b1g4k7cdxgeoof ~/Downloads/cogvideo_fullrun
```

전체 outputs를 압축 다운로드:

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/download_outputs.sh --archive b1g4k7cdxgeoof ~/Downloads/cogvideo_fullrun
```

## 2.1) End-to-End 한 번에 실행 (배포/실행/다운로드/Pod stop)

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/run_milestone1_e2e.sh b1g4k7cdxgeoof
```

설명:
1. Pod ID를 넘기면 스크립트가 먼저 `pod start`를 수행한다(이미 실행 중이면 skip).
2. 이어서 실행/다운로드/stop까지 자동 처리한다.

Pod를 유지하고 싶으면:

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/run_milestone1_e2e.sh --keep-pod b1g4k7cdxgeoof
```

## 3) 첫 실행 또는 복구용 전체 자동 실행

Pod 생성/업로드/부트스트랩/실행/다운로드를 한 번에 수행:

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/provision_milestone1_fixed.sh b1g4k7cdxgeoof
```

Pod ID 생략 가능:

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/provision_milestone1_fixed.sh
```

## 4) baseline 파라미터 수정 위치

고정 baseline 값은 아래 파일을 수정한다.

1. [deployments/runpod/milestone1.fixed.env](/Users/kimtaehoon/workspace/CogVideo/deployments/runpod/milestone1.fixed.env)

임시 값으로만 실행하려면:

```bash
cd /Users/kimtaehoon/workspace/CogVideo && ./deployments/runpod/run_milestone1_fixed.sh --env-file /absolute/path/to/override.env b1g4k7cdxgeoof
```

## 5) 스크립트 역할 정리

1. `deployments/runpod/run_milestone1_fixed.sh`: baseline 파라미터로 빠른 반복 실행
2. `deployments/runpod/provision_milestone1_fixed.sh`: baseline 파라미터로 Pod 준비부터 실행/다운로드까지 전체 자동화
3. `deployments/runpod/provision_and_run.sh`: 임의 명령을 직접 넘길 때 쓰는 범용 자동화 스크립트
4. `scripts/run_milestone1_pipeline.py`: 실제 추론 로직 본체 (삭제 대상 아님)
