# Codex Migration Plan

## 목적

`claude-code-video-toolkit`의 기존 Claude Code 자산을 유지한 채, Codex 사용자도 유사한 진입 경험으로 사용할 수 있도록 `Codex migration layer`를 추가한다.

이 계획의 핵심은 기존 `.claude/commands/*`, `.claude/skills/*`, `CLAUDE.md`를 **소스 오브 트루스**로 유지하고, Codex 전용 리소스는 **생성/설치 계층**으로 분리하는 것이다.

## 범위

이번 작업 범위:

1. 하드코딩된 로컬 절대경로를 제거한다.
2. `.claude/commands/*`를 스캔해 Codex용 command-wrapper skill을 생성하는 스크립트를 추가한다.
3. `.claude/skills/*`를 Codex skill 디렉토리로 복사/설치하는 스크립트를 추가한다.
4. 예외 처리용 매핑 파일을 둔다.
5. 문서에 migration 구조와 실행 방법을 기록한다.

이번 작업 제외:

1. 기존 `.claude/*` 파일 직접 수정
2. 기존 `CLAUDE.md`를 `AGENTS.md`로 강제 치환
3. Codex 전용으로 템플릿/툴 동작을 별도 구현

## 설계 원칙

### 1. 기존 리소스 불변

upstream PR 가능성을 고려해 Claude Code 전용 리소스는 원칙적으로 유지한다.

즉:

1. `.claude/commands/*`는 그대로 둔다.
2. `.claude/skills/*`는 그대로 둔다.
3. `CLAUDE.md`도 그대로 둔다.

### 2. 동적 스캔 기반

`migrate_to_codex.py`는 다음을 자동 탐색한다.

1. `_internal/toolkit-registry.json`
2. `.claude/commands/*.md`
3. `.claude/skills/*/SKILL.md`

따라서 upstream에서 command/skill이 추가되어도 대부분은 스크립트 수정 없이 반영 가능해야 한다.

### 3. 예외만 매핑 파일로 관리

이름 충돌, 제외 대상, 향후 rename 정책은 별도 매핑 파일에서 관리한다.

즉 기본 경로는:

1. 자동 스캔
2. 자동 생성
3. 예외만 설정 파일로 override

## 생성 대상

스크립트는 Codex 홈(`~/.codex/skills`) 아래에 다음을 설치한다.

### A. 기존 toolkit skill 복사

`.claude/skills/*`를 Codex skill 형식으로 그대로 설치한다.

이유:

1. 이미 `SKILL.md` frontmatter가 존재한다.
2. 내용도 domain knowledge로 재사용 가능하다.

### B. command wrapper skill 생성

Claude Code의 slash command마다 Codex skill 하나를 생성한다.

예:

1. `/video` -> `video`
2. `/setup` -> `setup`
3. `/scene-review` -> `scene-review`

wrapper skill은 실제 workflow source를 `.claude/commands/<name>.md`로 안내하고, Codex에서 해당 command를 흉내 내는 진입점 역할을 한다.

### C. toolkit overview skill 생성

Codex가 저장소 전체 맥락을 빠르게 잡을 수 있도록 overview skill 하나를 같이 생성한다.

## 완료 기준

이번 계획의 완료 기준:

1. `scripts/migrate_to_codex.py`가 동작한다.
2. 임시 destination에 skill 설치 결과를 생성할 수 있다.
3. command wrapper skill과 copied skill이 모두 생성된다.
4. 문서만 읽고도 다른 세션 작업자가 구조를 이해할 수 있다.

## 참고 자료

1. [Agent Docs README](../agent/README.md)
2. [Project Status](../status/project_status.md)
3. [Backlog](../status/backlog.md)
4. [CLAUDE.md](../../CLAUDE.md)
5. [_internal/toolkit-registry.json](../../_internal/toolkit-registry.json)
