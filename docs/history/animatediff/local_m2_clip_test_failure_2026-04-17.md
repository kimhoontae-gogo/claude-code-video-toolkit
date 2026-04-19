# Experiment: local_m2_clip_test_failure_2026-04-17

## 목적

- 로컬 `Mac mini M2 + MPS` 환경에서 `AnimateDiffPipeline` + `AnimateDiffVideoToVideoPipeline` 기반 2-scene clip 실험이 실제로 질문에 답할 수 있는 품질을 내는지 확인한다.
- 핵심 질문:
  `이전 scene의 마지막 프레임(init image)을 다음 scene 생성에 사용하면 연결이 더 자연스러워지는가?`

## 환경

- machine: Mac mini M2
- os: macOS
- device: MPS
- python: `.venv/bin/python` 3.9
- runtime date: 2026-04-17

## 모델

- base_model: `runwayml/stable-diffusion-v1-5`
- motion_model: `guoyww/animatediff-motion-adapter-v1-5-2`
- pipeline_type:
  - `AnimateDiffPipeline`
  - `AnimateDiffVideoToVideoPipeline`

## 입력

- style goal:
  `minimal 2D line doodle / storyboard`
- scene_count: 2
- scene_1:
  같은 남성이 카페 창가 테이블에서 커피 컵을 든 장면
- scene_2:
  같은 남성이 같은 자리에서 창밖을 바라보는 장면

## 실행 중 관찰된 문제

1. 초기 시도에서는 검은 화면 결과가 발생했다.
2. 이후 MPS 메모리 부족 문제가 발생했다.
3. img2img/video-to-video 단계에서 shape 관련 런타임 에러가 발생했다.
4. 프롬프트 길이가 CLIP 한도를 넘어서 일부 앵커 문구가 잘렸다.
5. 스타일을 단순 선화 방향으로 바꾼 뒤에도 최종 결과가 사람 눈으로 식별 가능한 수준까지 올라오지 않았다.

## 결과

- scene별 이미지와 영상이 생성되더라도 `무슨 장면인지 알아보기 어렵다`는 사용자 평가가 나왔다.
- `without init` / `with init` 비교 이전에, 개별 scene 자체가 식별 불가능한 경우가 많았다.
- 따라서 이 실험은 `init image가 효과가 있는지`를 평가하는 단계까지 도달하지 못했다.

## 판단

- 이번 로컬 clip 실험은 `성공적인 실험`이 아니라 `질문에 답할 수 없는 실패`로 분류한다.
- 실패의 의미는 `init image가 효과 없다`가 아니다.
- 올바른 해석은 아래와 같다.

`현재 로컬 M2 + MPS + AnimateDiff 설정으로는 이번 질문에 답할 수 있는 수준의 clip 품질을 안정적으로 얻기 어렵다.`

## 실패 원인 정리

1. AnimateDiff clip 생성은 로컬 Apple Silicon 환경에서 메모리와 속도 제약을 크게 받는다.
2. 낮은 해상도, 짧은 프레임 수, 낮은 inference step 조합에서는 scene 구조가 무너지기 쉽다.
3. 이번 마일스톤은 `연결성 검증`이 목적이지만, 실제로는 `영상 품질 부족`이 먼저 병목이 되었다.

## 결론

- 로컬 clip 실험은 여기서 중단한다.
- 본 마일스톤의 다음 단계는 `원격 GPU 환경`으로 이동한다.
- 우선순위는 아래와 같다.
  - 1순위: RunPod
  - 2순위: Google Colab

## 다음 액션

1. RunPod 또는 Colab에서 NVIDIA GPU + CUDA 환경을 확보한다.
2. 동일한 2-scene clip 실험을 원격 GPU에서 다시 실행한다.
3. `without init merged` / `with init merged` 결과를 기준으로 다시 평가한다.
