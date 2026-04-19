# Codex Migration

## 목적

이 문서는 `claude-code-video-toolkit`를 Codex에서도 사용할 수 있도록 하는 migration 계층의 구조를 설명한다.

중요한 전제:

1. 기존 Claude Code 리소스는 그대로 유지한다.
2. Codex 대응은 `생성/설치 레이어`로 추가한다.
3. upstream에 새 command/skill이 추가되어도 대부분 자동 반영되도록 설계한다.

## 왜 별도 migration 레이어가 필요한가

이 저장소의 기존 UX는 아래 자산에 강하게 의존한다.

1. `.claude/commands/*`
2. `.claude/skills/*`
3. `CLAUDE.md`

Codex는 이 구조를 그대로 읽는 제품이 아니므로, 아래 대응이 필요하다.

1. Claude command를 Codex skill로 변환
2. Claude skill을 Codex skill 설치 위치로 복사
3. 저장소 전체 설명은 Codex가 이해하기 쉬운 wrapper skill로 보강

## 설계

### Source of Truth

아래 리소스는 migration 이후에도 원본으로 유지한다.

1. `.claude/commands/*`
2. `.claude/skills/*`
3. `_internal/toolkit-registry.json`
4. `CLAUDE.md`

### Generated Layer

`scripts/migrate_to_codex.py`는 위 원본을 읽어 Codex용 skill 설치 디렉토리를 만든다.

생성 결과물:

1. 기존 toolkit skill 복사본
2. command wrapper skill
3. overview skill

### Mapping Layer

예외 처리는 `codex/migration_map.json`에서 관리한다.

이 파일은 아래 상황을 처리한다.

1. 이름 충돌
2. 특정 command/skill 제외
3. 향후 rename 정책

## 업데이트 전략

upstream에 command/skill이 추가되었을 때 기대 흐름:

1. 저장소 pull
2. `scripts/migrate_to_codex.py` 재실행
3. 자동 탐색으로 신규 항목 반영

스크립트 수정이 필요한 경우는 주로 아래뿐이다.

1. Codex skill 포맷 자체가 바뀐 경우
2. command/skill naming conflict 정책을 바꿔야 하는 경우
3. 새 command가 특별한 wrapper 문구를 필요로 하는 경우

## 실행 방법

임시 디렉토리에 생성 확인:

```bash
python3 scripts/migrate_to_codex.py --dest /tmp/codex-skills --force
```

실제 Codex 홈에 설치:

```bash
python3 scripts/migrate_to_codex.py --force
```

기본 설치 위치:

```text
~/.codex/skills
```

## 참고 자료

1. [Codex Migration Plan](../plans/codex_migration_plan.md)
2. [Agent Workflow](./agent_workflow.md)
3. [Docs README](../README.md)
