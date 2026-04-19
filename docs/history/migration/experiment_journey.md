# 실험 이력 통합 문서 (AnimateDiff -> CogVideo)

## 1. 문서 목적

이 문서는 이전 저장소(AnimateDiff, CogVideo)에서 수행한 마일스톤 실험의 목표/과정/결과를 한 곳에서 복원하기 위한 통합 기록이다.

원문 문서는 `docs/history/animatediff/`, `docs/history/cogvideo/`에 보존한다.


## 2. 최종 상위 목표

실험 전 과정의 최종 목표는 동일했다.

1. 사용자 스토리 텍스트 입력
2. scene 단위 분해
3. scene별 영상 생성
4. scene들을 자연스럽게 연결해 짧은 스토리 영상 완성
5. 장기적으로 음성/배경음/자막까지 통합


## 3. 1단계: AnimateDiff 실험

### 3.1 목표

1. `init image`(이전 scene 마지막 프레임)를 다음 scene 조건으로 넣으면 연결이 개선되는지 검증
2. 로컬(M2) 및 저가 GPU 환경에서 실험 재현성 확인

### 3.2 과정

1. 로컬 Mac M2에서 diffusers/AnimateDiff 기반 quick test 실행
2. Colab/RunPod로 환경 이동해 GPU 실험 반복
3. scene 수, 프롬프트, init image 전략을 바꾸며 비교

주요 원문:

1. [scene_transition_milestone_plan.md](../animatediff/scene_transition_milestone_plan.md)
2. [remote_gpu_execution_plan.md](../animatediff/remote_gpu_execution_plan.md)
3. [local_m2_clip_test_failure_2026-04-17.md](../animatediff/local_m2_clip_test_failure_2026-04-17.md)
4. [colab_python312_failure_2026-04-18.md](../animatediff/colab_python312_failure_2026-04-18.md)
5. [milestone2_runpod_quality_result_2026-04-18.md](../animatediff/milestone2_runpod_quality_result_2026-04-18.md)

### 3.3 결과

1. 실행 자체는 가능했지만 scene readability가 낮았음
2. init image가 continuity에 일부 도움은 있었으나 품질 붕괴가 잦았음
3. 최종적으로 AnimateDiff 단독 전략은 목표 품질 달성에 한계가 있다고 판단


## 4. 2단계: CogVideo 전환 실험

### 4.1 목표

1. 더 최신 video-native 모델(CogVideo)로 전환해 scene 가독성과 품질 개선
2. 파이프라인을 `text -> anchor image -> scene image -> I2V`로 재정의
3. RunPod 운영 자동화(start/run/download/stop) 확립

### 4.2 과정

1. CogVideo 메인 브랜치 기준 전환 계획 수립
2. milestone1 실험 wrapper/스크립트 구현
3. `prev_last_frame` 조건 전달 방식 실험
4. 해상도/모델/프롬프트 제약을 고정하고 반복 검증

주요 원문:

1. [cogvideo_adoption_plan.md](../cogvideo/cogvideo_adoption_plan.md)
2. [milestone1_reference_i2v_plan.md](../cogvideo/milestone1_reference_i2v_plan.md)
3. [runbook_snapshot.md](../cogvideo/runbook_snapshot.md)
4. [commands_snapshot.md](../cogvideo/commands_snapshot.md)
5. [project_status_snapshot.md](../cogvideo/project_status_snapshot.md)

### 4.3 결과

1. 실행 자동화와 재현 가능한 운영 흐름은 확보
2. scene 2+에서 `prev_last_frame` 직접 I2V 입력 경로까지 구현
3. 다만 특정 scene에서 후반 프레임 붕괴(맥락 충돌 + 모션 제약 충돌) 발생
4. 다음 단계는 모델 교체만이 아니라 scene 설계/검수/retry 자동화가 핵심이라고 결론


## 5. 현재까지의 핵심 교훈

1. 단일 모델/단일 프롬프트로는 스토리 continuity 확보가 어렵다.
2. 품질 문제는 모델 한계와 scene 설계 문제가 함께 작동한다.
3. 실험 속도와 재현성 확보를 위해 운영 자동화(runbook/script)는 필수다.
4. 다음 실험은 `scene spec 구조화 + QC + retry`를 기본 축으로 가야 한다.

