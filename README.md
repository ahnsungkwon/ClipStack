# ClipStack

**A powerful Windows clipboard manager that extends the built-in multi-clipboard (Win+V) with quick hotkey access to preset text sets.**

![ClipStack Demo](./docs/assets/clipstack-demo.gif)

*Quick demo of ClipStack workflow: grab, stack, sync, and switch between saved text sets.*

[한국어 설명](#한국어-설명) | [English](#english) 

---

## English

### Why ClipStack Exists

I originally did not even know Windows had a built-in clipboard history feature.

While working on repetitive online registration tasks, I kept typing or copying and pasting the same pieces of text one by one. It was slow, tedious, and easy to lose focus. Then I discovered the built-in Windows multi-clipboard through `Win+V`, and it felt like a small breakthrough. The workflow became much faster and more comfortable.

But there was still one problem. My work was not just about reusing the same fixed text forever. Some values changed every time, such as dates, staff names, or event-specific details. I also had to switch back and forth between different registration sets depending on the event I was handling.

That made me think: what if these related clipboard items could be grouped into reusable sets and switched instantly?

That idea became **ClipStack**.

ClipStack builds on top of the Windows clipboard history experience and makes it practical for real work: save related text as sets, inject them back into the clipboard stack, and switch between them quickly with hotkeys.

My hope is simple: that this small utility makes repetitive work easier, smoother, and less frustrating for other users too. Good luck to everyone doing real work with real repetition. You deserve better tools.

### Features

- 💾 **Save 6 preset clipboard sets** - Store your favorite 3-item text combinations
- ⚡ **Ultra-fast hotkey access** - Ctrl+Alt+1~6 to load any saved set instantly
- 🎯 **Smart clipboard injection** - Automatically pushes 3 items to Windows clipboard in correct order
- 📋 **Built-in manager GUI** - Easy-to-use interface to create and edit sets
- 🔄 **Auto-import from history** - Grab recent clipboard items or current clipboard content with one click
- 🚀 **Lightweight & portable** - Single AutoHotkey script, no installation needed

### Use Cases

Perfect for anyone who frequently copies/pastes multiple related items:
- **Content creators**: Title, body, tags
- **Data entry**: Name, email, phone
- **Developers**: Code snippets, templates, boilerplate
- **Administrators**: Credentials, IDs, links
- **Students**: Citation, source, notes

### Quick Start

1. **Install AutoHotkey v2**: Download from [autohotkey.com](https://www.autohotkey.com)
2. **Download ClipStack**: Clone or download this repository
3. **Run the script**: Double-click `clipboard_triplets.ahk` (or use `run.cmd`)
4. **Open manager**: Press `Ctrl+Alt+0`
5. **Create sets**: Name your set, fill in 3 items, click Save
6. **Use hotkeys**: `Ctrl+Alt+1~6` to load, `Ctrl+Alt+Shift+1~6` to edit

### Hotkeys

| Hotkey | Action |
|--------|--------|
| `Ctrl+Alt+0` | Open manager window |
| `Ctrl+Alt+1`~`6` | Load preset set 1~6 |
| `Ctrl+Alt+Shift+1`~`6` | Edit preset set 1~6 |

### Files

- `clipboard_triplets.ahk` - Main script (AutoHotkey v2)
- `clipboard_triplets.ini` - Preset storage (auto-created)
- `run.cmd` - Double-click launcher
- `CLIPBOARD_TRIPLETS_GUIDE.md` - Detailed Korean guide

### Requirements

- Windows 7+
- AutoHotkey v2.0+
- PowerShell (for advanced features)

### License

MIT License - Use freely for personal or commercial purposes

---

## 한국어 설명

### 왜 ClipStack을 만들었나

처음에는 Windows 기본 기능인 멀티 클립보드 자체를 몰랐습니다.

온라인 서류 등록 업무를 하다 보면 비슷한 내용을 여러 번 입력해야 하는데, 매번 한 개씩 복사하고 붙여넣는 과정이 너무 번거롭고 시간도 많이 들었습니다. 그러다가 검색을 하다 보니 Windows에 `Win+V`로 불러오는 기본 멀티 클립보드 기능이 있다는 걸 알게 됐고, 그때 정말 "유레카"를 외쳤습니다. 작업이 훨씬 편해졌습니다.

하지만 거기서도 아쉬움이 있었습니다. 제 작업은 완전히 똑같은 내용을 반복하는 것만은 아니었습니다. 날짜나 담당자처럼 이벤트마다 조금씩 바뀌는 항목이 있었고, 여러 종류의 등록 업무를 번갈아 처리해야 할 때도 많았습니다.

그래서 자연스럽게 이런 생각이 들었습니다.
**"관련된 텍스트들을 세트로 묶어서, 필요할 때 바로 바꿔 쓸 수 있으면 얼마나 좋을까?"**

그 생각을 구현한 것이 바로 **ClipStack**입니다.

ClipStack은 Windows 멀티 클립보드를 더 실무적으로 쓸 수 있게 만들어줍니다. 자주 쓰는 여러 줄 텍스트를 세트로 저장하고, 다시 클립보드 히스토리에 넣고, 단축키로 빠르게 전환할 수 있게 해줍니다.

제 바람은 단순합니다. 이 작은 유틸리티가 반복적이고 번거로운 작업을 조금이라도 더 쉽게 만들어줬으면 좋겠습니다. 반복 업무를 하는 모든 사용자들, 정말 화이팅입니다.

### 기능

- 💾 **6개 세트 저장** - 자주 쓰는 3개 항목 조합을 미리 저장
- ⚡ **빠른 단축키** - Ctrl+Alt+1~6으로 즉시 불러오기
- 🎯 **스마트 주입** - Windows 클립보드에 3개 항목을 올바른 순서로 푸시
- 📋 **관리 GUI** - 세트를 쉽게 만들고 편집
- 🔄 **자동 가져오기** - 최근 항목이나 현재 클립보드 내용 한 번에 가져오기
- 🚀 **가볍고 휴대 가능** - 단일 AutoHotkey 스크립트, 설치 불필요

### 사용 순서

1. **AutoHotkey v2 설치** - [autohotkey.com](https://www.autohotkey.com)에서 다운로드
2. **ClipStack 다운로드** - 이 저장소를 클론하거나 다운로드
3. **스크립트 실행** - `clipboard_triplets.ahk` 더블클릭 (또는 `run.cmd`)
4. **관리창 열기** - `Ctrl+Alt+0` 누르기
5. **세트 만들기** - 이름 입력, 3개 항목 작성, 저장 클릭
6. **단축키로 사용** - `Ctrl+Alt+1~6`로 로드, `Ctrl+Alt+Shift+1~6`으로 편집

### 단축키

| 단축키 | 동작 |
|--------|------|
| `Ctrl+Alt+0` | 관리창 열기 |
| `Ctrl+Alt+1`~`6` | 세트 1~6 로드 |
| `Ctrl+Alt+Shift+1`~`6` | 세트 1~6 편집 |

### 파일

- `clipboard_triplets.ahk` - 메인 스크립트 (AutoHotkey v2)
- `clipboard_triplets.ini` - 세트 저장소 (자동 생성)
- `run.cmd` - 더블클릭 실행 프로그램
- `CLIPBOARD_TRIPLETS_GUIDE.md` - 상세 사용 가이드

### 필요사항

- Windows 7 이상
- AutoHotkey v2.0 이상
- PowerShell (고급 기능용)

### 라이센스

MIT License - 개인 및 상업용으로 자유롭게 사용 가능

---

### 기여 & 피드백

Issues와 Pull Requests를 환영합니다!

### FAQ

**Q: 항목을 4개 이상 저장할 수 있나요?**  
A: 현재는 3개로 고정되어 있습니다. 향후 확장 계획이 있습니다.

**Q: 시작 프로그램으로 등록할 수 있나요?**  
A: `run.cmd`를 Windows 시작 폴더에 바로가기로 만들면 됩니다.

**Q: 데이터가 어디에 저장되나요?**  
A: `clipboard_triplets.ini` 파일에 저장됩니다. 같은 폴더에 위치합니다.
