# Colab Python 3.12 실패 기록

## 1. 문서 목적

이 문서는 2차 마일스톤을 Colab T4 환경에서 실행하려다 중단한 이유를 기록한다.


## 2. 실행 목적

목적은 아래였다.

1. 원본 AnimateDiff + thin wrapper 구조를 Colab T4에서 실행한다.
2. `reference image + init image chaining + quality ladder` 구조가 동작하는지 본다.
3. RunPod 비용을 쓰기 전에 무료 환경에서 1회 확인한다.


## 3. 시도한 경로

1. 최소 파일 zip 업로드
2. `requirements.txt` 기반 설치 시도
3. Hugging Face 로그인 준비
4. Colab 내 reference image 생성
5. `scripts/run_reference_quality_ladder.py` 실행


## 4. 확인된 문제

### 4.1 초기 wrapper 버그

초기 실행에서는 아래 경로가 생성되지 않아 실패했다.

- `experiments/.../scene_01/run.log`

이 문제는 wrapper 코드 수정으로 해결했다.


### 4.2 Colab 기본 Python과 레거시 의존성 충돌

Colab 런타임 정보:

- Python `3.12.13`

실행 중 확인된 문제:

1. `requirements.txt` 설치 후에도 `diffusers`, `transformers`가 정상 설치되지 않았다.
2. 최소 패키지 수동 설치 시 `tokenizers` wheel build가 실패했다.
3. 원본 AnimateDiff 코드는 구버전 `diffusers` API 경로를 기대한다.
4. 현재 Colab 기본 Python 3.12 환경은 이 저장소의 구버전 의존성 조합과 맞지 않는다.

대표 에러:

- `ModuleNotFoundError: No module named 'diffusers.modeling_utils'`
- `Failed to build tokenizers`


## 5. 결론

이번 2차 마일스톤에서 Colab은 `비권장 실행 환경`으로 판단한다.

이유:

1. 목표는 품질 검증이지 Colab 환경 우회가 아니다.
2. 현재 저장소는 오래된 `diffusers/transformers/tokenizers` 조합을 기대한다.
3. Colab 기본 Python 3.12 환경과 충돌 가능성이 높다.
4. 해결하려면 별도 Python 3.10 계열 환경을 다시 만들거나 의존성 우회가 필요해진다.
5. 이 비용은 현재 마일스톤 목표에 비해 과하다.


## 6. 후속 결정

다음 실행 환경은 RunPod로 고정한다.

RunPod에서 기대하는 장점:

1. Python 버전 통제 가능
2. CUDA/Torch 조합 통제 가능
3. 반복 실행과 정리가 Colab보다 안정적
4. CLI/API 자동화 설계가 가능


## 7. 이 기록의 의미

이 문서는 "Colab에서 조금 더 만지면 된다"는 뜻이 아니다.

현재 기준 해석:

1. Colab은 1차 마일스톤의 간단한 방향성 확인에는 의미가 있었다.
2. 2차 마일스톤의 원본 AnimateDiff 검증 환경으로는 비효율적이다.
3. 따라서 이후 문서와 실행 기준은 RunPod 우선으로 정리한다.
