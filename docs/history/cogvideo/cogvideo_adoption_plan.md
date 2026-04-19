# CogVideo 전환 계획 문서

## 1. 문서 목적

이 문서는 기존 AnimateDiff 기반 실험을 왜 종료하고 CogVideo를 메인 엔진 후보로 채택했는지, 그리고 앞으로 어떤 방식으로 다시 마일스톤을 구성할지를 설명한다.


## 2. 배경

이전 프로젝트에서 수행한 핵심 실험은 아래 질문을 검증하는 것이었다.

`이전 scene의 마지막 프레임을 다음 scene의 init image로 넣으면 scene 연결이 더 자연스러워지는가?`

AnimateDiff 기반 실험에서 얻은 결론은 아래와 같다.

1. continuity 개선 가능성은 일부 관찰되었다.
2. 하지만 영상 품질과 semantic structure 유지가 충분하지 않았다.
3. 결과적으로 `연결이 자연스러운가`를 보기 전에 `scene 자체가 충분히 읽히는가`가 더 큰 병목이 되었다.

따라서 다음 단계에서는 더 최신의 video-native 오픈소스 모델을 메인 후보로 바꿀 필요가 생겼다.


## 3. 왜 CogVideo인가

현재 CogVideo를 우선 후보로 보는 이유는 아래와 같다.

1. `text-to-video`, `image-to-video`, `video continuation` 흐름을 모두 제공한다.
2. upstream가 최신 `CogVideoX1.5` 계열을 유지하고 있다.
3. diffusers 기반 경로도 제공해 향후 wrapper 개발 난이도가 낮다.
4. AnimateDiff보다 더 직접적으로 video generation 자체를 다루는 모델 계열이다.


## 4. 현재 기준 버전 선택

현재 프로젝트는 upstream `main` 브랜치의 최신 상태를 기준으로 한다.

기준 커밋:

`7a1af7154511e0ce4e4be8d62faa8c5e5a3532d2`

선택 이유:

1. upstream release `v1.0`는 구형 `2B/5B/5B-I2V`용 릴리스다.
2. upstream release note는 `CogVideoX1.5-5B`, `CogVideoX1.5-5B-I2V`는 `main` 또는 더 최신 릴리스를 쓰라고 안내한다.
3. 현재 프로젝트는 구형 모델보다 `1.5` 계열을 우선 검토하므로 `main`이 더 적절하다.


## 5. 새 마일스톤의 방향

CogVideo 전환 이후의 첫 마일스톤은 아래 방향으로 잡는다.

1. `text-only`보다 `reference image + image-to-video`를 우선한다.
2. 짧더라도 읽히는 scene을 먼저 만든다.
3. 그 다음에 scene stitching을 붙인다.
4. continuity 평가는 scene 자체가 읽히는 수준이 확보된 뒤에 수행한다.

즉 순서는 아래와 같다.

1. scene 품질 확보
2. reference image 효과 확인
3. multi-scene 연결
4. 최종 편집 파이프라인 연결


## 6. 1차 구현 후보

첫 번째 구현 후보는 아래 중 하나다.

1. upstream `diffusers` 기반 CLI/스크립트를 감싸는 thin wrapper
2. upstream inference 코드를 직접 호출하는 실험 wrapper

우선 원칙:

1. upstream 구조를 과도하게 깨지 않는다.
2. 별도 wrapper는 `configs/`, `scripts/`, `experiments/` 식으로 최소 범위만 추가한다.
3. scene plan, reference asset, output report를 구조화한다.


## 7. 초기 출력 목표

첫 CogVideo milestone의 최소 성공 기준:

1. reference image를 넣고 scene 1 영상을 생성할 수 있다.
2. 생성 결과가 사람이 장면을 식별 가능한 수준이다.
3. 같은 캐릭터/배경을 유지하는 두 번째 scene 생성 실험까지 갈 수 있다.
4. 실행 방법을 다른 세션 작업자가 재현 가능하게 문서화한다.


## 8. 참고자료

1. CogVideo GitHub README
   https://github.com/zai-org/CogVideo
2. CogVideo Releases
   https://github.com/zai-org/CogVideo/releases
3. CogVideo technical report
   https://arxiv.org/abs/2408.06072
