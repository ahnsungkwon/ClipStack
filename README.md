# ClipStack

**A powerful Windows clipboard manager that extends the built-in multi-clipboard (Win+V) with quick hotkey access to preset text sets.**

[한국어 설명](#한국어-설명) | [English](#english) 

---

## English

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
