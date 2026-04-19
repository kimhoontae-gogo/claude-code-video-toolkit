# Architecture Decisions

## ADR-001: Agent Native 문서 구조 도입

결정:

`docs/` 하위에 `status`, `plans`, `history`, `agent`, `architecture` 구조를 도입한다.

이유:

1. 다른 세션 작업자가 문서만으로 상태를 복원할 수 있어야 한다.
2. 계획-구현-검증-기록 흐름을 고정해야 한다.

영향:

1. 모든 기능/실험 작업 후 문서 현행화가 필수다.
2. 과거 실험은 `history/`에 분리 보관한다.

