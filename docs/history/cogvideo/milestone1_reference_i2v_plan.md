# Milestone 1 Text-to-Image-to-Video 계획 문서

## 상태

`완료 (2026-04-19)`

이번 문서는 계획 문서이면서, Milestone 1 종료 시점의 결과 요약을 함께 보관한다.

종료 결론:

1. 파이프라인(`anchor -> scene image or prev_last_frame -> I2V`)은 실행 가능함을 확인했다.
2. RunPod 자동화(start/run/download/stop) 실행 흐름을 확보했다.
3. scene 전환 품질은 여전히 불안정했고, 일부 scene(특히 scene 4)에서 후반 프레임 붕괴가 발생했다.
4. 원인은 주로 장면 전환 맥락과 motion 제약 간 충돌로 판단했다.
5. 따라서 다음 마일스톤의 핵심은 모델 변경 단독이 아니라 `scene text 구조화 + review + retry` 체계 도입이다.

## 1. 문서 목적

이 문서는 CogVideo 전환 이후 첫 번째 실제 마일스톤의 목표, 구현 전략, 실행 환경, 검증 기준을 정의한다.

이번 마일스톤의 핵심 질문은 아래와 같다.

`하나의 짧은 스토리를 5개 scene text로 정리한 뒤, 먼저 캐릭터 기준 이미지와 scene 시작 이미지를 만들고 CogVideo image-to-video를 적용하면, 읽을 수 있는 짧은 영상 구조를 만들 수 있는가?`


## 2. 확정된 전제

이번 마일스톤에서는 아래 전제를 확정한다.

1. 시작 입력은 `text only`다.
2. 외부 `reference image`는 없다고 가정한다.
3. scene 수는 `5개`다.
4. CogVideo는 주로 `image-to-video` 엔진으로 사용한다.
5. scene 시작 이미지는 CogVideo가 아니라 `별도 text-to-image 단계`에서 만든다.
6. image generation 기본 후보는 `Qwen/Qwen-Image`, `Qwen/Qwen-Image-Edit-2511`이다.
7. 실행 환경은 가능하면 처음부터 `Docker 중심`으로 잡는다.
8. 최종 목표에서는 `story text -> scene texts` 분할 단계를 LLM이 담당한다.
9. 이번 마일스톤에서는 그 단계를 별도 구현하지 않고, 샘플 story와 샘플 scene texts를 고정 입력으로 사용한다.

최종 목표 기준의 상위 파이프라인:

`story text -> scene texts -> character anchor image -> 5 scene start images -> CogVideo I2V -> merged preview`

이번 마일스톤의 실제 실험 파이프라인:

`sample story text -> sample scene texts -> character anchor image -> 5 scene start images -> CogVideo I2V -> merged preview`


## 3. 왜 이렇게 가는가

AnimateDiff 실험에서 확인한 핵심 문제는 아래와 같았다.

1. scene 자체가 잘 안 읽혔다.
2. 이전 scene 마지막 프레임만 다음 scene에 넘기면 오류도 같이 누적됐다.
3. continuity를 보기 전에 scene readability와 character consistency를 먼저 확보해야 했다.

따라서 이번에는 업계에서 많이 쓰는 아래 개념을 현재 프로젝트에 맞게 도입한다.

1. `character anchor`
   먼저 주인공 기준 이미지를 만든다.
2. `scene start keyframe`
   각 scene의 시작 이미지를 먼저 만든다.
3. `image-to-video`
   scene 시작 이미지를 짧은 video clip으로 바꾼다.
4. `optional continuity hint`
   이전 마지막 프레임 활용은 후순위 옵션으로 둔다.

이번 마일스톤의 우선순위는 `scene 연결`보다 `같은 캐릭터가 읽히는 scene 5개를 만드는 것`이다.


## 4. 쉬운 말로 설명한 전체 구조

### 4.1 최종 목표의 유저 입력

유저는 story text만 입력한다.

예:

1. 주인공이 누구인지
2. 어디에서 무슨 일이 일어나는지
3. scene이 어떻게 흘러가는지

최종 목표에서는 이 story text를 LLM이 scene texts로 분해한다.

### 4.2 이번 마일스톤의 시작 입력

이번 마일스톤에서는 `story text -> scene texts` 단계를 구현 범위에서 제외한다.

대신 아래를 사용한다.

1. 내가 미리 작성한 샘플 story text
2. 그 story를 5개 scene으로 나눈 샘플 scene texts

즉 이번 마일스톤은 `LLM 기반 scene splitting` 실험이 아니라, `scene texts 이후의 image/video pipeline` 검증이 목적이다.

### 4.3 시스템 내부 1단계: character anchor image 생성

텍스트를 보고 먼저 "이 이야기의 주인공은 대충 이렇게 생겼다"라는 기준 이미지를 1장 만든다.

이 이미지는 유저가 준 reference image가 아니라, 시스템이 내부적으로 새로 만드는 `internal reference image`다.

쉽게 말하면:

1. 유저는 글만 준다.
2. 시스템이 먼저 주인공의 표준 얼굴/복장/스타일 기준 이미지를 만든다.
3. 이후 모든 scene은 이 기준 이미지를 참고한다.

### 4.4 시스템 내부 2단계: scene 시작 이미지 생성

story를 5개 scene으로 나눈 뒤, 각 scene의 시작 이미지를 만든다.

중요한 점:

1. scene마다 그냥 텍스트만 따로 넣어서 이미지를 만들면 같은 사람처럼 안 보일 수 있다.
2. 그래서 `character anchor image + scene text`를 함께 사용한다.

### 4.5 시스템 내부 3단계: CogVideo I2V

각 scene 시작 이미지를 CogVideo `image-to-video`에 넣어서 scene별 짧은 clip을 만든다.

즉 CogVideo의 역할은:

1. text-to-image가 아니다.
2. image-to-video 엔진이다.
3. scene 시작 이미지를 짧은 움직임이 있는 clip으로 바꾸는 역할이다.


## 5. 각 모델의 역할

이번 파이프라인에서 각 모델과 LLM의 역할은 아래와 같이 분리한다.

### 5.1 LLM

역할:

1. 최종 목표에서 `story text -> scene texts` 분할을 담당한다.

이번 마일스톤에서의 처리:

1. 이 역할은 실제 코드로 구현하지 않는다.
2. 대신 샘플 story와 샘플 scene texts를 문서와 config로 고정한다.

### 5.2 Qwen-Image

역할:

1. story text에서 `character anchor image`를 생성한다.

이 모델을 쓰는 이유:

1. text-only 시작 조건에 맞는다.
2. 상업 허용 관점에서 Apache-2.0 축을 우선할 수 있다.

### 5.3 Qwen-Image-Edit-2511

역할:

1. `character anchor image`를 기반으로 5개 scene의 시작 이미지를 생성한다.

이 모델을 쓰는 이유:

1. 같은 캐릭터를 유지한 채 scene variation을 만드는 방향에 더 적합하다.
2. 단순 text-only 반복보다 character consistency를 높일 가능성이 있다.

### 5.4 CogVideo

역할:

1. scene 시작 이미지를 scene clip으로 변환한다.

즉 CogVideo는 이번 프로젝트에서 `video generation` 담당이다.


## 6. 같은 남자가 5개 scene에서 유지되게 하려면

이 질문이 이번 마일스톤의 핵심이다.

텍스트만으로 scene 1 이미지, scene 2 이미지, scene 3 이미지를 각각 만들면 같은 남자로 유지되기 어렵다.

그래서 아래 전략을 쓴다.

### 6.1 Character anchor image 전략

먼저 캐릭터 기준 이미지를 1장 만든다.

이 이미지에는 아래 정보를 최대한 고정한다.

1. 성별
2. 대략적인 나이대
3. 헤어스타일
4. 얼굴형
5. 의상
6. 전체 스타일

### 6.2 Scene image generation 전략

각 scene 이미지는 아래 입력으로 만든다.

1. character anchor image
2. scene 텍스트
3. 전체 스타일 고정 prompt

즉 같은 캐릭터를 유지하는 기본 방법은 `text only 반복`이 아니라 `anchor image + scene variation`이다.


## 7. Docker 전략

### 7.1 왜 Docker를 기본으로 보는가

이 프로젝트는 단순한 1회 실험이 아니라, 향후 최종 목표까지 확장 가능한 실행 구조를 가져야 한다.

Docker를 기본으로 두는 이유:

1. 로컬, RunPod, 향후 다른 GPU 환경에서 동일한 실행 단위를 유지하기 쉽다.
2. Python 패키지 충돌을 줄이기 쉽다.
3. image generation과 video generation 의존성을 분리할 수 있다.
4. 모델 캐시와 결과물을 volume bind로 관리하기 쉽다.

### 7.2 권장 컨테이너 분리

초기에는 아래 2개 컨테이너 구조를 권장한다.

1. `image-gen` 컨테이너
   - `Qwen-Image`
   - `Qwen-Image-Edit-2511`
2. `video-gen` 컨테이너
   - `CogVideo`

### 7.3 권장 volume bind 구조

```text
host:
  ./workspace/models
  ./workspace/inputs
  ./workspace/outputs
  ./workspace/cache/huggingface

container:
  /workspace/models
  /workspace/inputs
  /workspace/outputs
  /workspace/cache/huggingface
```

### 7.4 최종 목표까지 고려한 확장 방향

이 구조는 이후 아래 방향으로 확장하기 쉽다.

1. RunPod custom image
2. docker compose 또는 단순 shell wrapper
3. image generation worker / video generation worker 분리
4. 향후 음성, 배경음 생성 컨테이너 추가


## 8. 샘플 story와 scene texts

이번 마일스톤에서는 아래와 같은 약 25초 내외 분량의 샘플 story를 기준 입력으로 사용한다.

샘플 story:

`퇴근 후 조용한 카페에 들어온 한 남자가 창가 자리에 앉아 커피를 받는다. 그는 잠시 컵을 바라보다가 천천히 한 모금 마시고, 창밖을 보며 생각에 잠긴다. 휴대폰 화면에 짧은 메시지가 도착하자 표정이 조금 누그러지고, 남자는 잔잔하게 미소를 지은 뒤 컵을 내려놓고 자리에서 일어난다.`

이 story를 아래 5개 scene texts로 나눈다.

1. Scene 1:
   `A young man in a dark navy shirt enters a quiet cafe at dusk and settles into a window seat, with a warm lamp and a coffee cup on the wooden table.`
2. Scene 2:
   `The same man sits still and looks down at the coffee cup, his posture calm and slightly tired, as the evening light reflects on the window beside him.`
3. Scene 3:
   `The man lifts the cup, takes a slow sip, and lowers it while remaining seated at the same table near the window.`
4. Scene 4:
   `A phone on the table lights up with a short new message, and the man turns his gaze from the window to the phone with a softened expression.`
5. Scene 5:
   `The man gives a small relieved smile, places the cup down, and rises from the chair as if ready to leave the cafe.`

샘플 scene plan 파일:

1. [configs/experiments/milestone1/sample_scene_plan.yaml](../../configs/experiments/milestone1/sample_scene_plan.yaml)


## 9. GPU 실행 목표

이번 마일스톤의 목표 GPU는 `24GB VRAM 수준`으로 잡는다.

권장 후보:

1. `RTX 4090 24GB`
2. `L4 24GB`
3. `RTX 3090 24GB`
4. `RTX A5000 24GB`

운영 원칙:

1. 첫 테스트는 1 scene 단독 생성
2. 그 다음 5 scene 이미지 생성
3. 그 다음 5 scene video generation
4. 마지막에 merged preview 생성
5. 모든 단계는 가능하면 동일한 Docker 런타임 규칙으로 실행


## 10. 구현 제안

### 9.1 권장 파일 구조

```text
configs/experiments/milestone1/
docker/
scripts/
experiments/
assets/reference/
assets/generated/
workspace/
```

### 9.2 wrapper 역할

wrapper는 아래 역할만 담당한다.

1. story 입력 로드
2. scene plan 로드 또는 생성
3. `Qwen-Image` character anchor image 생성 호출
4. `Qwen-Image-Edit-2511` scene start image 생성 호출
5. CogVideo I2V 호출
6. 결과 mp4 저장
7. merged preview 생성
8. summary json 저장
9. 모든 경로를 volume 기준 경로로 정규화

### 9.3 초기 실행 모드

초기 버전은 아래 세 모드면 충분하다.

1. `generate-character-anchor`
2. `generate-scene-images`
3. `render-scenes-with-cogvideo`
4. `run-full-milestone`


## 11. 성공 기준

이번 마일스톤은 아래를 만족하면 성공이다.

1. 24GB VRAM급 GPU에서 CogVideo I2V가 실제로 실행된다.
2. text-only 입력으로 character anchor image가 생성된다.
3. 5개 scene start image가 생성된다.
4. 5개 scene clip이 사람이 읽을 수 있는 수준으로 나온다.
5. merged preview가 생성된다.
6. 적어도 주인공이 "같은 사람처럼 보이려는 경향"이 관찰된다.


## 12. 다음 추천 액션

다음 구현 순서는 아래가 적절하다.

1. `CogVideoX-5b-I2V`에서 `CogVideoX1.5-5B-I2V`로 기본 video 모델 전환
2. 현재 baseline(scene text, motion prompt, seed, steps)을 유지한 A/B 비교 실행
3. 결과가 개선되지 않으면 `LoRA/스타일 보정` 트랙으로 전환
4. 캐릭터 스타일 목표(단순 선화/만화체)에 맞춰 대안 모션 모델 트랙 병행 검토

### 12.1 우선순위 A: CogVideo 1.5 전환

현재 `CogVideoX-5b-I2V`는 720x480 고정 해상도/6초/8fps 제약이 있다.
`CogVideoX1.5-5B-I2V`는 더 높은 해상도 범위와 16fps(5/10초)를 지원한다.

실행 원칙:

1. 프롬프트/seed/steps/frames는 그대로 유지하고 `video_model`만 교체한다.
2. scene 1 단독 검증 후 5-scene 전체를 실행한다.
3. 비교 지표는 아래 3개만 본다.
4. 인물 일관성(같은 사람처럼 보이는지)
5. 동작 안정성(목/얼굴 만짐 같은 오동작 빈도)
6. 압축/깨짐(프레임 왜곡 체감)

### 12.2 우선순위 B: LoRA/스타일 보정

`LoRA`는 기존 대형 모델 전체를 다시 학습하지 않고, 작은 추가 가중치만 학습해 특정 스타일/캐릭터 성향을 주입하는 방식이다.

이번 프로젝트에서의 의미:

1. 목표 스타일(단순 선화/유머 캐릭터)을 별도 데이터로 학습해 기본 모델의 스타일 편향을 보정한다.
2. scene motion prompt를 바꾸는 것보다 더 직접적으로 스타일 일관성을 높일 수 있다.
3. CogVideo 공식 가이드와 diffusers 가이드는 LoRA fine-tuning 경로를 제공한다.

적용 순서:

1. 30~100개 짧은 학습 클립(캐릭터 스타일 중심) 구축
2. baseline 모델 + LoRA rank 실험(예: rank 64/128)
3. 동일 scene plan으로 무보정 대비 A/B 평가
4. 유효하면 milestone2 기본 경로로 채택

### 12.3 캐릭터 스타일 대안 트랙

사용자 목표가 `실사 고품질`보다 `캐릭터 느낌 전달`이라면 아래 트랙이 현실적이다.

1. 트랙 C1: `강한 이미지 스타일 + 일반 I2V`
2. 캐릭터 anchor/scene image를 더 강하게 만화체로 만들고(I2V는 CogVideo1.5 유지), 모션은 최소화한다.
3. 장점: 현재 파이프라인 재사용 가능.
4. 한계: 모션 모델이 실사 분포 편향이면 동작 깨짐이 남을 수 있다.
5. 트랙 C2: `카툰 특화 모션 모델` 병행
6. ToonCrafter 같은 카툰 보간/생성 모델은 cartoon domain 자체를 겨냥한다.
7. 장점: 캐릭터 스타일 유지와 만화형 움직임에 유리.
8. 한계: 짧은 길이/해상도 제약, 워크플로우 재구성 필요.
9. 트랙 C3: `Wan I2V 계열` 병행 평가
10. Wan2.1/2.2 계열은 I2V와 스타일/모션 제어 확장 생태계가 활발해 대안 비교 가치가 있다.
11. 장점: 다양한 해상도/모드와 확장성.
12. 한계: 운영 복잡도 증가, 초기 세팅 비용.


## 13. 참고자료

1. CogVideo GitHub README
   https://github.com/zai-org/CogVideo
2. CogVideo CLI demo
   [inference/cli_demo.py](../../inference/cli_demo.py)
3. Qwen-Image model card
   https://huggingface.co/Qwen/Qwen-Image
4. Qwen-Image-Edit-2511 model card
   https://huggingface.co/Qwen/Qwen-Image-Edit-2511
5. Runway Keyframes guide
   https://help.runwayml.com/hc/en-us/articles/34170748696595-Creating-with-Keyframes-on-Gen-3
6. Google DeepMind Veo
   https://deepmind.google/models/veo/
7. OpenAI Video Generation guide
   https://developers.openai.com/api/docs/guides/video-generation
8. CogVideoX1.5-5B-I2V model card
   https://huggingface.co/zai-org/CogVideoX1.5-5B-I2V
9. CogVideoX-5b-I2V model card
   https://huggingface.co/zai-org/CogVideoX-5b-I2V
10. Diffusers CogVideoX training guide (limitations + LoRA)
   https://huggingface.co/docs/diffusers/main/en/training/cogvideox
11. CogVideo fine-tuning guide (LoRA/SFT + VRAM table)
   https://github.com/zai-org/CogVideo/blob/main/finetune/README.md
12. Wan2.1 official repository
   https://github.com/Wan-Video/Wan2.1
13. Wan2.1 I2V model card
   https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P
14. LTX-Video official repository
   https://github.com/Lightricks/LTX-Video
15. LTX Image-to-Video guide
   https://docs.ltx.video/open-source-model/usage-guides/image-to-video
16. ToonCrafter official repository
   https://github.com/Doubiiu/ToonCrafter
17. ToonCrafter model card
   https://huggingface.co/Doubiiu/ToonCrafter
18. ToonCrafter paper
   https://arxiv.org/abs/2405.17933
