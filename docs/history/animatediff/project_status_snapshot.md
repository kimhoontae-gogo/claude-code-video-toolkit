# 프로젝트 상태 문서

## 1. 문서 목적

이 문서는 현재 프로젝트가 어디까지 진행되었는지, 지금 무엇이 결정되었는지, 다음에 무엇을 해야 하는지를 빠르게 파악하기 위한 상태 문서다.

다른 세션의 작업자는 이 문서를 먼저 읽고 현재 상태를 파악한 뒤 작업을 시작해야 한다.


## 2. 현재 상태 요약

현재 프로젝트는 최종 영상 생성 서비스 구현 단계가 아니라, `2차 마일스톤 종료 후 3차 마일스톤 논의 전` 단계에 있다.

현재 핵심 질문:

`2차 마일스톤 결과를 바탕으로 3차 마일스톤에서는 어떤 conditioning 전략 변경을 우선 검토할 것인가?`

현재 실행 환경:

- 로컬: `Mac mini M2 + MPS`
- 최종 목표 환경: `Runpod + NVIDIA GPU + CUDA`

현재 상태 메모:

- 현재 마일스톤 계획 문서는 사용자와 논의를 거쳐 clip-based 방향으로 재정리되었다.
- 대표 이미지 기반 quick test 방식은 폐기되었다.
- 로컬 `Mac mini M2 + MPS` clip 실험은 질문에 답할 수 없는 실패로 정리되었다.
- Colab T4 실험으로 `with init`이 구조를 더 유지하는 경향을 확인했고, 1차 마일스톤은 완료로 정리되었다.
- Colab Python 3.12 환경에서는 원본 AnimateDiff 의존성 조합이 불안정하다는 점을 확인했다.
- RunPod에서는 원본 AnimateDiff + thin wrapper 구조가 실제로 실행되는 것을 확인했다.
- 다만 산출물은 continuity 부족 수준이 아니라 scene 자체가 질감 형태로 붕괴했고, 현재는 3차 마일스톤 논의 전 상태다.


## 3. 완료된 것

1. 프로젝트의 최종 목표와 현재 마일스톤이 문서화되었다.
2. `docs/`를 프로젝트 문서의 공식 위치로 정했다.
3. 문서 인덱스 체계를 만들었다.
4. `AGENTS.md`를 만들고 문서 현행화를 최우선 지침으로 정의했다.
5. clip-based 기준으로 마일스톤 계획 문서를 다시 작성했다.
6. 로컬 A 전략을 위한 2-scene clip test 스크립트 초안을 추가했다.
7. 실험 산출물에 branch별 merged clip과 side-by-side comparison clip을 포함하도록 보강했다.
8. 로컬 기본 스타일 가이드를 `minimal 2D line doodle / storyboard` 기준으로 구체화했다.
9. 로컬 clip 실험 실패를 문서화하고 원격 GPU 전환 계획을 수립했다.
10. Colab T4에서 `with init`이 continuity를 더 유지하는 경향을 확인했고, 1차 마일스톤을 종료했다.
11. 2차 마일스톤용 `with init` 전용 quality ladder wrapper를 추가했다.
12. `configs/experiments/milestone2/` 아래에 base config, scene plan, quality ladder를 추가했다.
13. 로컬에서 wrapper `--dry-run` 검증을 완료했고 temp yaml 및 summary 구조가 생성되는 것을 확인했다.
14. Colab Python 3.12 실패 원인을 문서화했고 RunPod 우선 전략으로 전환했다.
15. RunPod에서 milestone 2를 실제 실행했고, 실행 구조는 검증했지만 유효 장면 생성에는 실패했다.


## 4. 진행 중인 것

1. 2차 마일스톤 결과 정리 완료
2. 3차 마일스톤 전략 논의


## 5. 아직 시작하지 않은 것

1. 3차 마일스톤 계획 확정
2. Docker 기반 RunPod template 고정 여부 판단
3. RunPod 운영 자동화 초안 검증


## 6. 현재 결정된 기술 방향

1. 1차 마일스톤 결론은 `with init`이 continuity에 도움을 줄 가능성이 있다는 것이다.
2. 2차 마일스톤에서는 user-provided reference image를 첫 scene 스타일 기준으로 사용한다.
3. 2차 마일스톤의 기본 실행 엔진은 원본 AnimateDiff `scripts.animate`다.
4. 품질 ladder와 scene chaining은 별도 생성기가 아니라 thin wrapper에서 담당한다.
5. Colab은 보조 경로로만 남기고, 2차 마일스톤 기본 실행 환경은 RunPod로 본다.
6. 초기 원격 검증은 Docker 없이 직접 실행한다.
7. 환경이 안정되면 Docker image와 RunPod custom template로 고정한다.
8. 모든 코드/실험은 향후 RunPod 자동화로 확장 가능한 구조를 유지해야 한다.
9. 2차 마일스톤 결론은 `실행 구조는 가능하지만 현재 conditioning 전략으로는 semantic structure를 유지하지 못한다`는 것이다.


## 7. 현재 주요 리스크

1. reference image를 넣어도 현재 파이프라인이 그 형태를 충분히 따라가지 못할 수 있다.
2. init image가 캐릭터 구조가 아니라 붕괴된 텍스처만 다음 scene으로 전달할 수 있다.
3. 현재 접근은 GPU 증설만으로는 해결되지 않을 가능성이 높다.
4. 문서와 실제 구현이 어긋나면 다른 세션의 생산성이 급격히 떨어진다.


## 8. 다음 작업 추천

가장 우선순위가 높은 다음 작업:

1. milestone 2 결과를 바탕으로 3차 마일스톤 목표를 명확히 정의
2. conditioning 전략 변경 후보를 추림
3. 다음 실험 범위를 작게 고정


## 9. 갱신 규칙

아래 항목 중 하나라도 바뀌면 이 문서를 갱신해야 한다.

1. 현재 마일스톤 상태
2. 완료된 작업
3. 진행 중인 작업
4. 다음 작업 우선순위
5. 기술 방향 결정
6. 핵심 리스크
