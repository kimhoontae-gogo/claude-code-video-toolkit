# 씬 연결성 검증 및 품질 향상 마일스톤 문서

## 0. 빠른 요약

이 문서는 1차 마일스톤의 종료 기록과 2차 마일스톤의 기준안을 함께 관리한다.

1차 마일스톤 질문:

`짧은 scene clip을 여러 개 생성할 때, 이전 scene의 마지막 프레임을 다음 scene의 init image로 활용하면 연결이 더 자연스러워지는가?`

1차 마일스톤 결론:

1. 로컬 `Mac mini M2 + MPS`에서는 질문에 답할 수 있을 정도의 clip 품질 확보에 실패했다.
2. Colab `T4 GPU`에서는 품질은 낮았지만 `with init`이 `without init`보다 더 연결성을 유지하는 경향을 확인했다.
3. 따라서 1차 마일스톤의 핵심 질문에 대해서는 `그렇다` 쪽의 방향성을 확인한 것으로 종료한다.
4. 다음 병목은 `continuity 자체`가 아니라 `품질 부족`이다.

2차 마일스톤 결론 목표:

1. 유저가 전달한 reference image 스타일을 첫 scene부터 반영한다.
2. 특정 GPU 하나가 아니라 `사용 가능한 GPU 환경`에서 품질 상한을 확인한다.
3. 원본 AnimateDiff 경로를 우선 사용한다.
4. scene chaining 시 이전 scene의 마지막 프레임을 다음 scene의 `init image` 역할로 연결한다.


## 1. 최종 목표와 현재 마일스톤의 관계

### 1.1 최종 목표

최종적으로 만들고 싶은 것은 아래 시스템이다.

`사용자가 스토리 텍스트 입력 -> 시스템이 scene 분할 -> scene별 영상 생성 -> 자연스럽게 연결 -> 최종 영상 출력`

### 1.2 1차 마일스톤

1차 마일스톤은 아래 질문을 검증했다.

- 같은 인물이 계속 같은 인물처럼 보이는가
- 같은 장소가 계속 같은 장소처럼 보이는가
- scene이 바뀌어도 갑자기 다른 영상처럼 튀지 않는가
- `init image`를 사용하면 이런 일관성이 더 좋아지는가

### 1.3 2차 마일스톤

2차 마일스톤은 질문을 조금 바꾼다.

핵심 목표:

1. 유저가 첫 번째 scene의 분위기와 캐릭터 모양을 정하는 `reference image`를 직접 전달할 수 있게 가정한다.
2. 그 reference image를 기준으로 scene의 캐릭터/스타일 일관성을 더 강하게 유도한다.
3. Colab T4에 한정하지 않고, `GPU가 가능한 어떤 환경이든` 품질이 어디까지 나오는지 확인할 수 있도록 한다.
4. 약 30초 길이의 multi-scene 결과를 목표로 한다.
5. `init image`는 각 scene의 마지막 프레임을 다음 scene의 image condition으로 넣는 방식으로 사용한다.


## 2. 1차 마일스톤 종료 정리

### 2.1 수행한 전략

1. 대표 이미지 슬라이드 방식은 폐기했다.
2. 실제 clip 기반 실험으로 방향을 바꿨다.
3. 로컬 M2 환경과 Colab T4 환경에서 `with init` / `without init` 비교를 시도했다.

### 2.2 결과 요약

1. 로컬 `Mac mini M2 + MPS`에서는 품질이 너무 낮아 질문에 답하기 어려웠다.
2. Colab `T4 GPU`에서는 전체 품질은 낮았지만, `with init`이 `without init`보다 인물/배경 구조를 더 유지하는 경향을 확인했다.
3. 따라서 1차 마일스톤은 `init image가 continuity에 도움을 줄 가능성`을 확인한 것으로 종료한다.

### 2.3 1차 마일스톤 종료 판단

1차 마일스톤은 아래 의미에서 완료로 본다.

1. `without init`과 `with init`를 비교 가능한 형태로 생성했다.
2. `with init`이 구조를 더 유지하는 경향을 관찰했다.
3. 다음 병목이 `continuity 여부`가 아니라 `품질 부족`이라는 점이 명확해졌다.


## 3. 2차 마일스톤 목표

2차 마일스톤의 목표는 아래 세 가지다.

1. 첫 번째 scene부터 유저의 reference image 느낌을 더 강하게 반영한다.
2. 사용 가능한 GPU 환경에서 품질을 어디까지 올릴 수 있는지 확인한다.
3. 전체 약 30초 길이의 multi-scene 영상에서 continuity와 품질을 동시에 본다.

운영 원칙:

1. Colab, RunPod, 기타 CUDA GPU 환경 중 실제로 확보 가능한 환경에서 동일한 실험 구조를 수행할 수 있어야 한다.
2. 한 번의 고정 설정으로 끝내지 않고, 저품질 설정부터 시작해서 성공하면 점차 상향하는 `quality ladder` 방식으로 수행한다.
3. 품질 상향의 기준은 단순 실행 성공이 아니라 `캐릭터 식별성`, `reference image 유사성`, `scene continuity`다.

현재 실행 우선순위 보정:

1. Colab은 1차 마일스톤의 방향성 확인에는 의미가 있었지만, 2차 마일스톤의 원본 AnimateDiff 실행 환경으로는 비권장이다.
2. 2차 마일스톤의 기본 실행 환경은 RunPod로 본다.
3. Colab은 문서상 보조 경로로만 남긴다.


## 4. reference image 기준

현재 기준 reference image의 핵심 특성은 아래와 같다.

1. 흑백 또는 무채색 위주
2. 매우 단순한 선화
3. 둥근 몸통의 사람 모양 캐릭터
4. 점 눈, 단순한 얼굴 표현
5. 배경과 소품도 매우 단순화

참고 해석:

1. 컬러는 없어도 된다.
2. 오히려 흑백/무채색이 현재 실험 목적에는 더 유리할 수 있다.
3. 목표는 `고급 일러스트`가 아니라 `식별 가능하고 일관된 캐릭터`다.


## 5. 성공 기준

2차 마일스톤은 아래 조건을 만족하면 성공으로 본다.

1. reference image 기반 캐릭터/스타일 방향이 prompt-only보다 더 명확하게 유지된다.
2. 사용 가능한 GPU 환경 중 최소 1개 이상에서 scene이 사람이 식별 가능한 수준까지 올라온다.
3. 각 scene의 마지막 프레임을 다음 scene의 `init image` 역할로 연결할 수 있다.
4. 총 30초 내외의 multi-scene 영상 구조를 만들 수 있다.
5. 어떤 환경에서 어떤 파라미터까지 성공했는지 문서화할 수 있다.


## 6. 포함 범위와 제외 범위

### 6.1 포함되는 것

1. reference image 기반 스타일 유도 실험
2. 총 30초 내외 multi-scene 실험
3. scene chaining 기반 `init image` 연결 실험
4. quality ladder 기반 파라미터 상향 실험
5. GPU 환경별 결과 문서 기록

### 6.2 포함되지 않는 것

1. LLM 기반 story -> scene split 자동화
2. TTS
3. BGM / SFX
4. 웹 UI
5. 최종 서비스 완성
6. RunPod 배포 자동화


## 7. 구현 방향

### 7.1 실행 경로

2차 마일스톤에서는 가능하면 별도 Diffusers 실험 스크립트보다 원본 AnimateDiff 실행 경로를 우선한다.

기본 방향:

1. 실제 생성은 `python -m scripts.animate --config ...` 경로를 사용한다.
2. scene별 config 또는 config 템플릿을 준비한다.
3. scene 1 결과의 마지막 프레임을 추출해 다음 scene config의 image condition 입력으로 넣는다.
4. 이 과정을 scene 수만큼 반복한다.

### 7.1A conditioning 전략 확정안

2차 마일스톤의 기본 conditioning 방식은 아래로 확정한다.

1. 기본 경로는 `SparseCtrl RGB`
2. 기본 모드는 `always-on init chaining`
3. 이번 마일스톤에서는 `without init` 브랜치는 기본 실행 범위에서 제외한다

이유:

1. 현재 목표는 `init image 유효성 비교`가 아니라 `init image를 쓰는 조건에서 품질 상한 확인`이다.
2. 현재 reference image가 단순 흑백 캐릭터이기 때문에 RGB condition으로도 충분히 직접적인 형태 고정이 가능할 것으로 본다.
3. `without init`까지 같이 돌리면 품질 ladder 비용이 커지고 해석이 복잡해진다.

### 7.2 init image 연결 방식

이번 마일스톤에서 `init image`는 아래 의미로 사용한다.

1. Scene N의 마지막 프레임을 추출한다.
2. 그 이미지를 Scene N+1의 image condition 입력으로 넣는다.
3. 첫 장면의 reference image는 `style anchor`
4. 이전 장면의 마지막 프레임은 `continuity anchor` 역할을 한다.

초기 연결 규칙:

1. Scene 1:
   user reference image 사용
2. Scene 2:
   Scene 1 last frame 사용
3. Scene 3:
   Scene 2 last frame 사용
4. Scene 4:
   Scene 3 last frame 사용
5. Scene 5:
   Scene 4 last frame 사용

후속 실험 후보:

1. user reference image와 previous last frame을 함께 쓰는 방식
2. 한 scene 안에서 여러 sparse image를 넣는 방식
3. scene 시작 프레임뿐 아니라 중간 프레임까지 condition을 넣는 방식

### 7.3 quality ladder 방식

특정 GPU 환경에서 무조건 해상도만 올리지 않는다.
아래 항목을 조합하면서 어디까지 식별 품질이 나오는지 본다.

1. `steps` 상향
2. `width/height` 상향
3. 필요 시 `num_frames` 유지 또는 소폭 증가
4. 흑백/단순 스타일 유지
5. reference image 기반 prompt 정교화
6. 장면당 길이와 전체 scene 수 조정

quality ladder 원칙:

1. 저품질/저비용 설정부터 시작한다.
2. 한 레벨이 성공하면 다음 레벨로 올라간다.
3. 실패하면 즉시 중단한다.
4. 마지막 성공 레벨을 기록한다.
5. 이 ladder는 Colab, RunPod, 기타 GPU 환경에서 동일한 구조로 적용한다.

권장 ladder 상승 순서:

1. 먼저 `steps`를 올린다.
2. 그 다음 `width/height`를 올린다.
3. 그 다음 `frames_per_scene`를 늘린다.

이유:

1. 현재 병목은 장면 식별성이므로, 먼저 denoising quality를 확보하는 쪽이 유리하다.
2. frame 수를 먼저 늘리면 GPU 비용은 크게 늘지만 식별성 개선은 불명확할 수 있다.


## 8. config 전략 확정안

이번 마일스톤에서는 scene별 완성 yaml 파일을 사람이 전부 손으로 만드는 방식보다,
`공통 템플릿 + scene plan + quality ladder + wrapper-generated temp yaml` 구조를 사용한다.

### 8.1 권장 파일 구조

```text
configs/experiments/milestone2/
  base_sparsectrl_rgb.yaml
  scene_plan_30s.yaml
  quality_ladder.yaml
```

설명:

1. `base_sparsectrl_rgb.yaml`
   AnimateDiff 공통 설정, 모델 경로, SparseCtrl RGB 기본 설정
2. `scene_plan_30s.yaml`
   5개 scene의 prompt, 목적, 길이, 연결 순서
3. `quality_ladder.yaml`
   단계별 steps / width / height / frame count / fps

현재 저장소 반영 상태:

1. [configs/experiments/milestone2/base_sparsectrl_rgb.yaml](../../configs/experiments/milestone2/base_sparsectrl_rgb.yaml)
2. [configs/experiments/milestone2/scene_plan_30s.yaml](../../configs/experiments/milestone2/scene_plan_30s.yaml)
3. [configs/experiments/milestone2/quality_ladder.yaml](../../configs/experiments/milestone2/quality_ladder.yaml)

### 8.2 왜 템플릿 기반인가

1. 5 scenes x 여러 quality levels 조합이면 정적 yaml 파일 수가 지나치게 많아진다.
2. init image 경로가 매 실행마다 바뀌므로 정적 yaml만으로는 관리가 불편하다.
3. wrapper가 값을 주입해 임시 yaml을 만드는 방식이 재현성과 확장성에 더 유리하다.

### 8.3 temp yaml 생성 원칙

wrapper는 실행 시 아래를 조합해 temp yaml을 만든다.

1. `base_sparsectrl_rgb.yaml`의 공통 AnimateDiff 설정
2. `scene_plan_30s.yaml`의 scene prompt
3. `quality_ladder.yaml`의 현재 level 파라미터
4. 현재 scene의 control image 경로

현재 구현 파일:

1. [scripts/run_reference_quality_ladder.py](../../scripts/run_reference_quality_ladder.py)

wrapper 책임:

1. Scene 1에는 user reference image를 넣는다.
2. Scene N의 마지막 프레임을 Scene N+1의 control image로 넣는다.
3. level을 낮은 비용부터 순서대로 올린다.
4. 실패하면 즉시 중단한다.
5. 마지막 성공 level을 `experiments/milestone2_quality_ladder/<timestamp>/best/`로 복사한다.
6. scene별 clip, merged clip, last frame sheet, level summary를 함께 남긴다.

실행 커맨드 기준:

```bash
cd /Users/kimtaehoon/workspace/AnimateDiff
./.venv/bin/python scripts/run_reference_quality_ladder.py \
  --reference-image /ABS/PATH/reference.png
```

산출물 기준:

1. `experiments/milestone2_quality_ladder/<timestamp>/reports/run_summary.json`
2. `experiments/milestone2_quality_ladder/<timestamp>/best/reports/merged.mp4`
3. `experiments/milestone2_quality_ladder/<timestamp>/best/reports/merged.gif`
4. `experiments/milestone2_quality_ladder/<timestamp>/best/reports/last_frames.png`
5. `experiments/milestone2_quality_ladder/<timestamp>/best/scenes/`

1. base config
2. 현재 scene의 prompt
3. 현재 quality level
4. 현재 scene에 들어갈 condition image 경로

temp yaml은 실행 폴더 안에 저장한다.

예시:

```text
experiments/milestone2/<timestamp>/level_01/configs/scene_01.yaml
experiments/milestone2/<timestamp>/level_01/configs/scene_02.yaml
...
```


## 9. wrapper 전략 확정안

wrapper는 AnimateDiff 자체를 대체하지 않는다.
원본 AnimateDiff 실행을 orchestration 하는 작은 실행기 역할만 맡는다.

### 9.1 wrapper 책임 범위

1. 입력 읽기
   - reference image path
   - scene plan
   - quality ladder
   - 환경 라벨
2. quality level 반복
3. Scene 1 config 생성
4. Scene 1 실행
5. Scene 1 마지막 프레임 추출
6. Scene 2 config 생성
7. Scene 2 실행
8. Scene 5까지 반복
9. 최종 merged 결과 생성
10. 마지막 성공 레벨 기록
11. 실패 시 즉시 중단

### 9.2 wrapper가 하지 않을 일

1. AnimateDiff 내부 생성 로직 재구현
2. 새로운 비디오 diffusion 파이프라인 구현
3. UI 제공

### 9.3 권장 실행 스크립트 이름

권장 후보:

- `scripts/run_milestone2_quality_ladder.py`

역할:

1. `python -m scripts.animate --config ...` 호출
2. scene chaining 제어
3. quality ladder 제어
4. 결과 요약 저장

### 9.4 결과 폴더 구조

```text
experiments/milestone2/<timestamp>/
  level_01/
    configs/
    scene_01/
    scene_02/
    scene_03/
    scene_04/
    scene_05/
    merged/
    reports/
  level_02/
  ...
```

이 구조에서 아래가 바로 보여야 한다.

1. 어느 level까지 성공했는지
2. 어느 scene에서 깨졌는지
3. 마지막 프레임이 무엇인지
4. 최종 merged 결과가 무엇인지


## 10. 30초 scene 구성안

### 8.1 전체 구조

1. 목표 길이: 총 30초 내외
2. 기본 구성: 5 scenes
3. 권장 길이: scene당 약 6초

### 10.2 scene 설계 원칙

1. 같은 인물, 같은 장소, 같은 시각 언어를 유지한다.
2. 단순히 `살짝 움직이는 정지화면`이 아니라, 읽을 수 있는 동적 동작을 넣는다.
3. 다만 reference image와의 형태 유사성이 무너지지 않도록 카메라와 배경은 지나치게 복잡하게 만들지 않는다.
4. 캐릭터 움직임은 커지더라도 장소 continuity는 유지한다.

공통 설정:

1. 인물: reference image와 유사한 단순 사람 모양 캐릭터 1명
2. 장소: 카페 창가
3. 스타일: 흑백 단순 선화 / line doodle / storyboard
4. 분위기: 단순하고 읽기 쉬운 톤
5. 컬러: 필수 아님

### 10.3 scene 상세안

#### Scene 1, 약 0초~6초

목적:
establishing shot

내용:
1. 캐릭터가 카페 창가 테이블에 앉아 있다.
2. 정적이기만 하지 않고 몸을 조금 흔들거나 시선을 옮기며 살아 있는 느낌을 준다.
3. 손은 컵 근처에서 작게 움직인다.

#### Scene 2, 약 6초~12초

목적:
첫 전환 검증

내용:
1. 같은 캐릭터가 창밖 쪽으로 고개를 돌린다.
2. 상체도 조금 더 회전해서 scene 변화가 눈에 보이게 한다.
3. Scene 1의 마지막 프레임을 Scene 2의 init image 역할로 사용한다.

#### Scene 3, 약 12초~18초

목적:
소품과 캐릭터 동작 검증

내용:
1. 캐릭터가 컵을 들어 올리거나 컵을 향해 손을 뻗는다.
2. 팔과 상체 움직임이 Scene 1, 2보다 더 커야 한다.
3. 테이블과 컵 같은 소품 continuity를 같이 본다.

#### Scene 4, 약 18초~24초

목적:
더 동적인 모션 검증

내용:
1. 캐릭터가 창가 쪽으로 몸을 기울이거나 앞으로 숙였다가 다시 돌아오는 동작을 한다.
2. 배경은 같은 장소로 유지하되 포즈 변화는 더 크다.
3. 단순한 캐릭터임에도 모션이 정적이지 않게 보이는지를 본다.

#### Scene 5, 약 24초~30초

목적:
최종 continuity 검증

내용:
1. 캐릭터가 다시 시선을 바깥에서 테이블 쪽으로 가져오거나, 손을 내린 뒤 조용히 창밖을 보는 상태로 마무리한다.
2. 이전 scene들의 동작이 끝난 뒤 자연스럽게 안정되는 ending shot 역할을 한다.

### 10.4 축소 테스트용 2-scene 안

초기 검증이 필요할 경우 아래 2-scene 축소안으로 먼저 본다.

1. Scene 1: 카페 창가에 앉아 컵 근처에서 손과 시선을 움직이는 establishing shot
2. Scene 2: 같은 캐릭터가 상체를 돌려 창밖을 바라보는 전환 shot


## 11. 관찰 포인트

1. 인물 동일성
2. 장소 동일성
3. 전환 자연스러움
4. reference image와의 형태 유사성
5. init image가 장면 전체를 유지하는지, 아니면 특정 오브젝트만 과도하게 끌고 가는지
6. 모션이 너무 정적이지 않고 충분히 동적으로 보이는지


## 12. 실험 흐름

1. 사용 가능한 GPU 환경을 확보한다.
2. reference image를 준비한다.
3. Scene 1 config를 만든다.
4. Scene 1을 생성한다.
5. Scene 1 마지막 프레임을 추출한다.
6. Scene 2 config에 Scene 1 마지막 프레임을 image condition으로 넣는다.
7. 같은 방식으로 Scene 3, Scene 4, Scene 5를 순차 생성한다.
8. 전체 scene을 이어붙여 약 30초 내외 merged 결과를 만든다.
9. 성공하면 다음 quality ladder 설정으로 올라간다.
10. 실패하면 멈추고 마지막 성공 설정을 기록한다.


## 13. 실행 도구 요구사항

여기서 말하는 `실행 도구`는 원본 AnimateDiff 실행 경로를 감싸는 얇은 orchestration layer를 의미한다.
반드시 별도 대형 애플리케이션일 필요는 없지만, 아래 요구사항은 만족해야 한다.

1. 기본 scene 수는 5개, 총 길이는 약 30초를 목표로 한다.
2. 축소 테스트용으로 2-scene 모드도 지원할 수 있어야 한다.
3. reference image 기반 스타일 조건을 넣을 수 있어야 한다.
4. scene 간 last frame을 다음 scene의 init image로 넘길 수 있어야 한다.
5. quality ladder 방식으로 설정을 자동 상승시킬 수 있어야 한다.
6. 실패 시 즉시 중단하고 마지막 성공 레벨을 기록해야 한다.
7. Colab, RunPod, 기타 CUDA GPU 환경에서 같은 구조로 실행 가능해야 한다.
8. stdout에 진행 상황 로그가 찍혀야 한다.
9. 실패 시 error log가 저장되어야 한다.
10. 결과는 scene별 clip과 frame으로 저장되어야 한다.
11. 최종 merged clip과 비교용 요약 산출물이 저장되어야 한다.

현재 구현 원칙:

1. 가능하면 `python -m scripts.animate --config ...` 경로를 그대로 사용한다.
2. 실험 자동화는 그 위에 얇은 wrapper 또는 runner를 둔다.
3. 목표는 AnimateDiff 자체를 대체하는 것이 아니라, multi-scene quality ladder 실험을 자동화하는 것이다.


## 14. 배포 및 실행 원칙

2차 마일스톤은 특정 플랫폼 전용이 아니라, GPU 가능한 환경 전반을 대상으로 한다.

우선 지원 대상:

1. Colab
2. RunPod
3. 기타 CUDA GPU 환경

문서화 원칙:

1. Colab에서 어떻게 업로드/설치/실행하는지 step by step으로 기록한다.
2. RunPod에서 어떻게 배포/접속/실행하는지 step by step으로 기록한다.
3. 동일한 quality ladder 실험 구조가 두 환경에서 모두 재현 가능해야 한다.


## 15. 결과 기록 형식

이번 실험 결과는 이 문서 하단에 추가하거나, 필요 시 별도 결과 문서로 정리한다.

최소 기록 항목:

1. 실행 환경
2. GPU 종류
3. 사용한 model / adapter / config
4. scene 수
5. 총 clip 길이
6. reference image 사용 방식
7. init image 연결 방식
8. 마지막 성공 quality level
9. reference image 유사성 평가
10. scene continuity 평가
11. 전체 품질 평가
12. 결론

실제 확인 우선순위:

1. 최종 merged video
2. scene별 clip
3. scene별 마지막 프레임
4. 품질 ladder summary


## 16. 현재 상태

이 문서는 현재 작업 방향을 정리한 초안이 아니라, 사용자와 합의된 현재 기준안이다.

1차 마일스톤은 종료되었다.
현재 작업 기준은 2차 마일스톤인 `reference image 기반 품질 향상`이다.


## 17. 실험 결과

### 15.1 로컬 M2 clip 실험

- 상태: 실패
- 이유:
  scene별 이미지와 clip이 사람 눈으로 식별 가능한 수준까지 올라오지 못했다.
- 해석:
  이는 `init image가 효과 없음`을 의미하지 않는다.
  현재 로컬 환경과 설정으로는 질문에 답할 수 없었다는 뜻이다.
- 다음 단계:
  GPU 가능한 원격 환경으로 전환

### 15.2 Colab T4 clip 실험

- 상태: 1차 마일스톤 완료에 사용
- 결과:
  `without init`보다 `with init`이 인물/배경 구조를 더 유지하는 경향을 확인했다.
- 한계:
  전체 품질은 여전히 낮아서, 자연스러운 영상 전환이라고 부르기에는 부족했다.
- 결론:
  `init image가 continuity에 도움을 줄 가능성`은 확인했다.
  다음 병목은 `품질 향상`이다.

관련 문서:

- [로컬 M2 clip 실험 실패 기록](../experiments/local_m2_clip_test_failure_2026-04-17.md)
- [원격 GPU 실행 계획 문서](./remote_gpu_execution_plan.md)

### 15.3 RunPod milestone 2 실험

- 상태: 종료
- 실행 결과:
  RunPod에서 원본 AnimateDiff + thin wrapper 구조는 실제로 동작했다.
- 마지막 성공 레벨:
  `level_03_more_motion`
- 실패 레벨:
  `level_04_30s_lowres_try`
- 직접 원인:
  `48 frames` 가 현재 temporal positional encoding 상한 `32` 를 초과했다.
- 품질 평가:
  결과 영상은 scene 간 연관성과 캐릭터 일관성이 약한 수준이 아니라, scene 자체가 중간부터 질감 형태로 붕괴해 평가가 어려운 상태였다.
- 직접 관찰:
  `scene_01_first`는 reference image와 유사하게 시작하지만 `scene_01_mid`부터 이미 구조가 사라지고,
  이후 scene들은 붕괴된 마지막 프레임을 체이닝한다.
- 결론:
  2차 마일스톤은 `실행 구조 검증 성공 / 유효 장면 생성 실패`로 종료한다.
  다음 단계는 단순 GPU 증설보다 conditioning 전략 재설계가 우선이다.

관련 문서:

- [Milestone 2 RunPod 결과 기록](../experiments/milestone2_runpod_quality_result_2026-04-18.md)
