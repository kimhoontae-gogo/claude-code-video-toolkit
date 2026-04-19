# 프로젝트 상태 문서

## 1. 문서 목적

이 문서는 CogVideo 기반 프로젝트가 현재 어디까지 진행되었는지, 왜 AnimateDiff에서 전환했는지, 다음에 무엇을 해야 하는지를 빠르게 파악하기 위한 상태 문서다.

다른 세션의 작업자는 이 문서를 먼저 읽고 작업을 시작해야 한다.


## 2. 현재 상태 요약

현재 프로젝트는 `AnimateDiff 실험 종료 후 CogVideo를 메인 후보 엔진으로 채택했고, Milestone 1(Text-to-Image-to-Video) 실험을 종료한 상태`다.

현재 핵심 질문:

`Milestone 1에서 확인한 scene 전환 붕괴 이슈를 다음 실험에서 어떤 전략으로 완화할 것인가?`

현재 저장소 기준:

- 저장소 위치: `/Users/kimtaehoon/workspace/CogVideo`
- upstream 기반: `zai-org/CogVideo`
- 현재 기준 브랜치: `main`
- 현재 기준 커밋: `7a1af7154511e0ce4e4be8d62faa8c5e5a3532d2`
- git remote: 제거 완료

버전 선택 이유:

1. upstream release `v1.0`는 구형 `CogVideoX-2B`, `CogVideoX-5B`, `CogVideoX-5B-I2V`용 릴리스다.
2. upstream release note는 `CogVideoX1.5-5B`, `CogVideoX1.5-5B-I2V`에 대해 `main` 브랜치 또는 더 최신 릴리스를 사용하라고 안내한다.
3. 따라서 현재 프로젝트는 `CogVideoX1.5` 계열 기준의 최신 안정 축으로 `main`을 채택한다.


## 3. 왜 AnimateDiff에서 전환했는가

이전 AnimateDiff 프로젝트에서 확인한 핵심 결론은 아래와 같다.

1. 로컬 `Mac mini M2 + MPS`에서는 실험 품질이 너무 낮았다.
2. Colab `T4`에서는 `init image`가 continuity에 약간 도움을 줄 가능성은 보였다.
3. RunPod + AnimateDiff wrapper 구조는 실행은 되었지만, 결과물이 scene 자체를 알아보기 어려울 정도로 붕괴했다.
4. 즉 병목은 단순한 GPU 부족이 아니라, `현재 AnimateDiff conditioning 전략으로는 의미 있는 장면 구조를 안정적으로 유지하지 못한다`는 점이었다.

따라서 현재 판단은 아래와 같다.

1. AnimateDiff는 과거 실험 기록으로는 유지 가치가 있다.
2. 하지만 유튜브 업로드를 목표로 한 최종 엔진 후보로는 우선순위를 내린다.
3. 메인 후보는 더 최신의 video-native open source 모델인 CogVideo로 전환한다.


## 4. 완료된 것

1. CogVideo 저장소를 `~/workspace/CogVideo`에 clone 했다.
2. upstream remote를 제거했다.
3. 이 프로젝트용 `AGENTS.md`를 추가했다.
4. `docs/` 문서 구조를 추가했다.
5. AnimateDiff 시절 핵심 milestone/experiment 문서를 `docs/history/animatediff_import/`로 이관했다.
6. CogVideo 기준 현재 상태와 전환 계획 문서를 새로 만들었다.
7. 첫 마일스톤 방향을 `text -> character anchor image -> scene images -> CogVideo I2V`로 정리했다.
8. image generation 기본 후보를 `Qwen-Image`, `Qwen-Image-Edit-2511`로 정리했다.
9. RunPod 배포 방향을 `bundle + scp + remote bootstrap`로 정리했다.
10. `Pod 생성 -> 업로드 -> bootstrap -> 실행 -> 다운로드`를 묶는 RunPod 스크립트 초안을 추가했다.
11. 샘플 story text와 5-scene sample plan을 추가했다.
12. sample scene plan을 읽는 milestone1 wrapper 초안을 추가했다.
13. scene별 motion 오해를 줄이기 위해 sample scene plan을 `단일 동작 + 금지 동작` 형태로 정제했다.
14. RunPod에서 baseline 파라미터를 고정 실행하는 `run_milestone1_fixed.sh` 스크립트를 추가했다.
15. scene_01 모션을 `자세 조정`에서 `눈깜빡임/호흡만`으로 더 제한해 목/얼굴 터치 오동작을 줄이도록 수정했다.
16. RunPod 첫 실행/복구를 파라미터 없이 처리하는 `provision_milestone1_fixed.sh` 스크립트를 추가했다.
17. `run_milestone1_fixed.sh` 실행 시 최신 코드가 자동 반영되도록 업로드/부트스트랩 체크를 기본 동작으로 변경했다.
18. baseline video 모델을 `CogVideoX1.5-5B-I2V`로 전환하고, scene N의 마지막 프레임을 scene N+1 이미지 생성에 쓰는 체인 방식을 적용했다.
19. scene image(예: 768x768)와 video 출력 해상도를 일치시키도록 I2V 렌더 인자를 수정해 종횡비 왜곡 가능성을 낮췄다.
20. baseline 해상도를 `1360x768`로 상향해 CogVideoX1.5 권장 비율과 입력/출력 해상도를 통일했다.
21. `run_milestone1_e2e.sh`를 추가해 배포/실행/다운로드/Pod stop을 한 번에 수행할 수 있게 했다.
22. `run_milestone1_e2e.sh`가 pod-id 입력 시 자동 `pod start`까지 수행하도록 보강했다.
23. scene 2+에서 `prev_last_frame`을 scene image 재생성 없이 I2V에 직접 입력하는 경로(`video_condition_source=prev_last_frame`)를 적용했다.
24. Milestone 1 결과를 문서에 종료 상태로 확정했다.


## 5. 진행 중인 것

1. Milestone 1 결과 기반 실패 패턴 정리
2. scene 전환 안정화 실험 조건 정리
3. 다음 마일스톤 계획 확정 준비


## 6. 아직 시작하지 않은 것

1. 다음 마일스톤 실험 wrapper 구현
2. 자동 QC 규칙 추가
3. 비교 실험 실행


## 7. 현재 결정된 기술 방향

1. 최종 목표는 여전히 `스토리 텍스트 -> scene 분할 -> scene별 영상 생성 -> 연결 -> 최종 짧은 영상`이다.
2. 초기 AnimateDiff 접근은 과거 실험 기록으로 유지하되, 메인 엔진 후보는 CogVideo로 전환한다.
3. 최종 목표에서는 `story text -> scene texts` 단계를 LLM이 담당한다.
4. 기본 scene 수는 `5개`다.
5. image generation 기본 후보는 `Qwen-Image`, `Qwen-Image-Edit-2511`이다.
6. 짧은 장면 여러 개를 scene 단위로 생성하고, 이후 stitching/편집으로 연결하는 방향은 유지한다.
7. 현재 마일스톤의 실제 입력은 `story text에서 파생된 scene texts`다.
8. 내부 파이프라인에는 `scene texts -> character anchor image -> scene images -> video` 전략을 도입한다.
9. RunPod 배포는 `bundle + scp + remote bootstrap` 전략을 우선 사용한다.
10. 문서에는 과거 실험과 현재 계획을 명확히 분리해서 기록한다.


## 8. 현재 주요 리스크

1. CogVideo도 단일 prompt만으로 scene 일관성을 충분히 보장하지 못할 수 있다.
2. `Qwen-Image` 계열이 24GB GPU 환경에서 얼마나 실용적인지 아직 검증되지 않았다.
3. 원격 bootstrap 방식의 설치 시간과 안정성이 아직 검증되지 않았다.
4. upstream CogVideo의 SAT 경로와 diffusers 경로 중 어떤 것을 메인 실행 경로로 삼을지 아직 확정되지 않았다.


## 9. 다음 작업 추천

가장 우선순위가 높은 다음 작업:

1. Milestone 1 결과 리포트 확정
2. 다음 마일스톤 실험 범위/완료 기준 확정
3. 비교 지표(QC) 포맷 확정


## 10. 갱신 규칙

아래 항목 중 하나라도 바뀌면 이 문서를 갱신해야 한다.

1. 메인 엔진 후보
2. 기준 커밋 또는 운영 브랜치
3. 현재 마일스톤 상태
4. 다음 작업 우선순위
5. 기술 방향 결정
