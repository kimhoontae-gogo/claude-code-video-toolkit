# Milestone 2 RunPod 결과 기록

## 1. 문서 목적

이 문서는 2차 마일스톤의 RunPod 실행 결과와 해석을 기록한다.


## 2. 실험 목적

검증 질문:

1. 원본 AnimateDiff + thin wrapper 구조가 RunPod 환경에서 실제로 동작하는가
2. `reference image + init image chaining + quality ladder` 구조로 scene continuity를 확보할 수 있는가
3. 현재 접근이 최종 목표로 이어질 정도의 품질을 낼 수 있는가


## 3. 실행 환경

- platform: RunPod
- gpu: NVIDIA A40 권장 기준으로 진행
- template family: RunPod PyTorch Python 3.10 계열
- python: 3.10 계열
- execution path:
  - `scripts/run_reference_quality_ladder.py`
  - 내부적으로 `python -m scripts.animate --config ...`


## 4. 실행 중 확인한 기술적 이슈

### 4.1 RunPod 환경 준비

아래 항목은 문서와 코드에 반영했다.

1. 일부 템플릿에는 `unzip`이 기본 설치되어 있지 않았다.
2. `huggingface_hub` 버전 충돌이 있었다.
3. `snapshot_download(..., local_dir=...)` 호환성 문제를 코드 fallback으로 보완했다.


### 4.2 quality ladder 한계

`level_04_30s_lowres_try` 에서 아래 에러가 발생했다.

- `RuntimeError: The size of tensor a (48) must match the size of tensor b (32)`

원인:

1. 현재 설정의 temporal positional encoding max length는 `32`
2. quality ladder의 일부 level은 `48 frames`
3. 따라서 `48 frames` 구간은 구조적으로 실패했다


## 5. 결과 요약

### 5.1 실행 자체

1. RunPod에서 원본 AnimateDiff 경로는 실제로 동작했다.
2. wrapper 구조도 실행되었다.
3. 마지막 성공 레벨은 `level_03_more_motion` 이다.


### 5.2 품질 평가

결과 평가는 부정적이며, 단순한 "연결성 부족"보다 더 근본적인 문제를 보였다.

관찰:

1. `scene_01_first` 프레임은 reference image와 매우 유사하게 시작했다.
2. 하지만 `scene_01_mid` 시점부터 이미 캐릭터/테이블/컵 구조가 사라지고 회색/베이지 질감처럼 붕괴했다.
3. 이후 scene들은 이 붕괴된 마지막 프레임을 다음 control image로 사용했기 때문에, 의미 있는 캐릭터 continuity가 아니라 무의미한 텍스처가 연쇄적으로 전달되었다.
4. `last_frames.png` 기준으로 scene 1~5 마지막 프레임은 거의 전부 식별 불가능한 평면적 질감으로 보였다.
5. 즉 현재 결과는 "scene continuity가 약하다"가 아니라, `scene readability 자체가 붕괴했다`고 보는 것이 더 정확하다.

직접 확인한 대표 파일:

1. `best/reports/last_frames.png`
2. `best/scenes/scene_01/last_frame.png`
3. `best/scenes/scene_05/last_frame.png`
4. `frame_samples/scene_01_first.png`
5. `frame_samples/scene_01_mid.png`


## 6. 결론

2차 마일스톤은 아래 의미에서 종료한다.

1. 실행 환경과 wrapper 구조는 RunPod 기준으로 검증되었다.
2. 현재 접근은 `기술적으로 실행 가능`하다.
3. 그러나 현재 접근은 `결과 품질 측면에서 목표 미달` 수준을 넘어, 현재 실험 질문을 평가하기 어려운 수준으로 장면이 붕괴했다.

즉 이번 마일스톤의 결론은 아래와 같다.

- `원본 AnimateDiff + SparseCtrl RGB + single reference image + init image chaining` 만으로는
  현재 기대하는 수준의 scene continuity와 캐릭터 일관성을 확보하기 어렵다.
- 더 정확히는, 현재 조합에서는 첫 장면 시작 직후부터 semantic structure가 유지되지 않아
  `init image chaining`의 유효성을 평가할 수 있는 안정된 장면 자체를 확보하지 못했다.


## 7. 다음 단계에 대한 시사점

현재 결론상 다음 단계는 단순 GPU 상향보다 아래 쪽이 더 중요하다.

1. conditioning 전략 변경
2. 더 짧고 더 강하게 통제된 clip 설계
3. reference image 외 추가 제어 입력 검토
4. scene continuity를 영상 모델 하나에 전부 맡기지 않는 방향 검토

다만 구체적인 3차 마일스톤 내용은 별도 논의 후 확정한다.
