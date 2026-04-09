# 클립보드 3종 세트 설명서

## 개요

`clipboard_triplets.ahk`는 윈도우 기본 멀티클립보드(`Win+V`)를 그대로 쓰면서,
텍스트 3개를 한 세트로 저장하고 빠르게 다시 불러오는 `AutoHotkey v2` 스크립트입니다.

예를 들어 이런 식으로 씁니다.

1. 제목
2. 중간 항목
3. 상세 항목

필요할 때 단축키 한 번으로 이 3개를 다시 `Win+V` 맨 위에 올립니다.

## 파일

- `clipboard_triplets.ahk` - Main script (AutoHotkey v2)
- `run.cmd` - Double-click launcher
- `clipboard_triplets.ini` - Preset storage (auto-created)
- `CLIPBOARD_TRIPLETS_GUIDE.md` - This guide

## 준비

이 스크립트는 `AutoHotkey v2`가 필요합니다.

현재 PC에는 이미 설치되어 있습니다.

설치 경로:

`C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe`

## 실행 방법

**방법 1**: `clipboard_triplets.ahk` 더블클릭

**방법 2**: `run.cmd` 더블클릭

실행 후 트레이에서 AutoHotkey 아이콘을 확인할 수 있으면 정상 실행된 것입니다.

## 단축키

- `Ctrl+Alt+0`
  - 관리 창 열기
- `Ctrl+Alt+1` ~ `Ctrl+Alt+6`
  - 해당 슬롯의 3개 세트를 `Win+V`에 다시 넣기
- `Ctrl+Alt+Shift+1` ~ `Ctrl+Alt+Shift+6`
  - 해당 슬롯 바로 편집

## 사용 순서

1. `Ctrl+Alt+0`으로 관리 창을 엽니다.
2. 슬롯 번호를 고릅니다.
3. `세트 이름`, `위 항목`, `가운데 항목`, `아래 항목`을 입력합니다.
4. `저장`을 누릅니다.
5. 작업할 때 `Ctrl+Alt+1` 같은 단축키로 세트를 다시 불러옵니다.
6. `Win+V`를 눌러 필요한 항목을 선택해 붙여넣습니다.

## 항목 순서

윈도우 `Win+V`는 가장 최근에 들어간 항목이 맨 위에 옵니다.

그래서 스크립트는 내부적으로:

1. 아래 항목
2. 가운데 항목
3. 위 항목

순서로 주입합니다.

그 결과 `Win+V` 화면에서는:

1. 위 항목
2. 가운데 항목
3. 아래 항목

순서로 보이게 됩니다.

## 클립보드 3줄 가져오기

클립보드에 아래처럼 3줄이 있을 때:

```text
Project Q1 Report - Tech Division
Lead: John Smith | Team Size: 8 | Status: In Progress
Deliverables: API v2.0, Dashboard, Mobile App | Budget Used: 75%
```

관리 창에서 `클립보드 3줄 가져오기`를 누르면:

- 1줄째 -> 위 항목
- 2줄째 -> 가운데 항목
- 3줄째 -> 아래 항목

으로 자동 입력됩니다.

주의:

- 비어 있지 않은 줄이 정확히 3줄이어야 합니다.

## 자주 생기는 상황

### 실행했는데 아무것도 안 보일 때

- 트레이의 숨겨진 아이콘 영역에 `AutoHotkey` 아이콘이 들어갈 수 있습니다.
- 그래도 확인이 어려우면 [클립보드_3종세트_실행.cmd](E:/GoogleDrive/코드/Codex_Worktree_Test_Repo/클립보드_3종세트_실행.cmd)를 다시 더블클릭하면 됩니다.

### 슬롯이 비어 있다고 나올 때

- `위 항목`, `가운데 항목`, `아래 항목` 3칸이 모두 채워져 있어야 합니다.
- 입력 후 `저장`을 먼저 누르세요.

### 예전 클립보드가 섞여 보일 때

- `Win+V`는 최근 기록을 누적합니다.
- 필요하면 `Win+V` 창에서 개별 삭제하거나 `모두 지우기`를 쓰면 됩니다.

## 추천 사용 방식

- 1번 슬롯: 오늘 작업 A
- 2번 슬롯: 오늘 작업 B
- 3번 슬롯: 오늘 작업 C
- 4번 슬롯: 자주 쓰는 고정 세트
- 5번 슬롯: 임시 작업
- 6번 슬롯: 임시 작업

이렇게 두면 하루에 여러 세트를 바꿔 써도 관리하기 편합니다.

## 다음 확장 가능 기능

원하면 나중에 아래 기능도 추가할 수 있습니다.

- 원문 1개를 넣으면 3개로 자동 변환
- 슬롯 개수 늘리기
- 시작 프로그램 등록
- 세트 백업/복원
