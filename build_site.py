#!/usr/bin/env python3
"""Build the public GitHub Pages version of 빅제이 비서실 from downloads/빅제이_비서실.html.

- pulls the inline base64 clay-office image out into map.png
- strips all personal data (amounts, phone numbers, hospital names, passwords, handles)
- adds iOS "add to home screen" (standalone web app) meta tags
"""
import base64
import pathlib
import re

SRC = pathlib.Path("downloads/빅제이_비서실.html")
OUT = pathlib.Path("github-pages/bigjei-office")
OUT.mkdir(parents=True, exist_ok=True)

html = SRC.read_text(encoding="utf-8")

# ---------------------------------------------------------------- assets
m = re.search(r'<img src="data:image/png;base64,([A-Za-z0-9+/=\s]+)"', html)
assert m, "inline base64 image not found"
img_bytes = base64.b64decode(re.sub(r"\s+", "", m.group(1)))
(OUT / "map.png").write_bytes(img_bytes)
html = html.replace('<img src="data:image/png;base64,' + m.group(1) + '"', '<img src="map.png"', 1)

# ---------------------------------------------------------------- head
head_extra = """<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
<link rel="manifest" href="manifest.webmanifest" />
<meta name="theme-color" content="#f6efe4" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
<meta name="apple-mobile-web-app-title" content="빅제이 비서실" />
<meta name="application-name" content="빅제이 비서실" />
<meta name="description" content="빅제이 비서실 - 오피스 맵, 회의실, 작업실, 비서현황, 메모를 한 화면에서 보는 개인 현황판" />
<link rel="apple-touch-icon" href="icon.png" />
<link rel="icon" type="image/png" href="icon.png" />"""
old_viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'
assert old_viewport in html
html = html.replace(old_viewport, head_extra, 1)

# iPhone full-screen: keep content clear of the notch / home indicator
html = html.replace(
    "    padding-bottom: 18px;\n  }\n  /* Header */",
    "    padding-bottom: calc(18px + env(safe-area-inset-bottom));\n  }\n  /* Header */",
    1,
)
html = html.replace(
    "    padding: 16px 16px 12px;\n  }",
    "    padding: calc(16px + env(safe-area-inset-top)) 16px 12px;\n  }",
    1,
)

# ---------------------------------------------------------------- map character notes
char_repl = [
    (
        """<div class="char-dot" style="left: 46%; top: 13%;" title="유키야 총괄비서" onclick="showInfo('👑 유키야 총괄비서: 지휘실에서 전체 일정·요양병원·알림을 총괄 중이에요!')"></div>""",
        """<div class="char-dot" style="left: 46%; top: 13%;" title="유키야 총괄비서" onclick="showInfo('👑 유키야 총괄비서: 지휘실에서 전체 일정과 알림을 총괄하고 있어요!')"></div>""",
    ),
    (
        """<div class="char-dot" style="left: 47%; top: 41%;" title="양비서 (가계부)" onclick="showInfo('🐑 양비서 (가계부): 4사 통합 11월 가계부 정리 완료! 밤 10시 지출 확인 대기 중')"></div>""",
        """<div class="char-dot" style="left: 47%; top: 41%;" title="양비서 (가계부)" onclick="showInfo('🐑 양비서 (가계부): 이번 달 통합 가계부 정리 완료! 밤 10시 지출 확인 대기 중')"></div>""",
    ),
    (
        """<div class="char-dot" style="left: 59%; top: 38%;" title="냥비서 (쇼핑·리뷰)" onclick="showInfo('🐱 냥비서 (쇼핑·리뷰): 네이버폼 8건 응모 완료! 오늘 14:00 리뷰 10건 예정')"></div>""",
        """<div class="char-dot" style="left: 59%; top: 38%;" title="냥비서 (쇼핑·리뷰)" onclick="showInfo('🐱 냥비서 (쇼핑·리뷰): 이벤트 응모 챙기는 중! 오늘 14:00 리뷰 작성 예정')"></div>""",
    ),
    (
        """<div class="char-dot" style="left: 72%; top: 40%;" title="돌핀비서 (병원·예약)" onclick="showInfo('🐬 돌핀비서 (병원·예약): 강남구립행복 답변 정리 완료, 암 전문 3곳 선택 대기 중')"></div>""",
        """<div class="char-dot" style="left: 72%; top: 40%;" title="돌핀비서 (병원·예약)" onclick="showInfo('🐬 돌핀비서 (병원·예약): 예약 문의 답변 정리 완료, 일정 확인 대기 중')"></div>""",
    ),
]
for a, b in char_repl:
    assert a in html, a[:60]
    html = html.replace(a, b, 1)

# ---------------------------------------------------------------- placeholder in chat input
html = html.replace(
    'placeholder="지시할 내용을 입력하세요 (예: @양비서 22일 건 포함해줘)"',
    'placeholder="지시할 내용을 입력하세요 (예: @양비서 가계부 확인해줘)"',
    1,
)

# ---------------------------------------------------------------- 작업실 (was real hospital / shopping tasks)
tasks_old = html[html.index("  <!-- 3. 작업실 -->") : html.index("  <!-- 4. 비서현황 -->")]
tasks_new = """  <!-- 3. 작업실 -->
  <section id="tab-tasks" class="panel">
    <div class="card">
      <div class="card-head">
        <span class="card-title">📋 주간 일정 및 예약 확인</span>
        <span class="badge b-wait">확인 중</span>
      </div>
      <div class="card-body">이번 주 일정과 예약을 한 장으로 정리했어요. 확인이 필요한 항목부터 표시해 둘게요.</div>
    </div>
    <div class="card">
      <div class="card-head">
        <span class="card-title">🎁 쇼핑·이벤트 응모 챙기기</span>
        <span class="badge b-wait">진행 중</span>
      </div>
      <div class="card-body">마감이 가까운 이벤트부터 순서대로 응모 목록을 정리했어요. 오늘 마감 건부터 바로 진행할게요.</div>
    </div>
    <div class="card">
      <div class="card-head">
        <span class="card-title">🛍️ 쇼핑 리뷰 작성 챙기기</span>
        <span class="badge b-run">오늘 14:00</span>
      </div>
      <div class="card-body">오늘 몫 리뷰 작성을 오후 2시에 진행할 예정이에요. 남은 건은 순서대로 이어서 진행해요.</div>
    </div>
    <div class="card">
      <div class="card-head">
        <span class="card-title">💳 이번 달 카드 가계부 정리</span>
        <span class="badge b-done">반영 완료</span>
      </div>
      <div class="card-body">이번 달 카드 이용내역을 통합 가계부에 반영했어요. 밤 22:00에 오늘 지출을 확인해요.</div>
    </div>
  </section>

"""
html = html.replace(tasks_old, tasks_new, 1)

# ---------------------------------------------------------------- 비서현황
status_old = html[html.index("  <!-- 4. 비서현황 -->") : html.index("  <!-- 5. AI한도 -->")]
status_new = """  <!-- 4. 비서현황 -->
  <section id="tab-status" class="panel">
    <div class="card">
      <div class="card-head"><span class="card-title">🐰 유키야 · 총괄비서</span><span class="badge b-run">ON · 지휘실</span></div>
      <div class="card-body">아침 브리핑, 메일·노션 확인, 전체 작업 조율 담당</div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">🐑 양비서 · 가계부 전담</span><span class="badge b-run">ON · 대회의실</span></div>
      <div class="card-body">카드 내역 정리, 노션·엑셀·달력 동기화, 22시 지출 점검</div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">🐱 냥비서 · 쇼핑·응모</span><span class="badge b-run">ON · 대회의실</span></div>
      <div class="card-body">매일 리뷰 작성, 이벤트 응모 실행</div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">🐬 돌핀비서 · 병원·예약</span><span class="badge b-run">ON · 대회의실</span></div>
      <div class="card-body">예약 문의 확인, 일정 관리</div>
    </div>
  </section>

"""
html = html.replace(status_old, status_new, 1)

# ---------------------------------------------------------------- AI한도
limits_old = html[html.index("  <!-- 5. AI한도 -->") : html.index("  <!-- 6. 메모 -->")]
limits_new = """  <!-- 5. AI한도 -->
  <section id="tab-limits" class="panel">
    <div class="card">
      <div class="card-head"><span class="card-title">⏰ 등록된 자동 스케줄</span><span class="badge b-run">3건 가동</span></div>
      <div class="card-body">
        • 30분마다 새 메일 확인<br/>
        • 매일 14:00 정기 작업 실행<br/>
        • 매일 22:00 하루 지출 정리
      </div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">📊 오늘 작업 진행률</span><span class="badge b-run">68%</span></div>
      <div class="card-body">이벤트 응모 정리 · 가계부 반영 · 일정 답변 정리 완료</div>
      <div class="progress-track"><div class="progress-fill" style="width:68%"></div></div>
    </div>
  </section>

"""
html = html.replace(limits_old, limits_new, 1)

# ---------------------------------------------------------------- sample chats + memos
chats_old = html[html.index("  const defaultChats = {") : html.index("  let currentRoom = 'cmd';")]
chats_new = """  const defaultChats = {
    cmd: [
      { who: 'me', name: '빅제이 (대장님)', role: '', avatar: '👑', time: '오전 10:35', text: '이번 주 일정이랑 예약 한 번에 정리해줘 @유키야 @돌핀비서' },
      { who: 'ai', name: '유키야', role: '총괄비서', avatar: '🐰', time: '오전 10:36', text: '네, 대장님! 이번 주 일정과 예약을 한 장으로 정리해서 올려뒀습니다!🫡' },
      { who: 'ai', name: '돌핀비서', role: '병원·예약', avatar: '🐬', time: '오전 10:36', text: '확인이 필요한 예약 건은 따로 표시해 두겠습니다!' },
      { who: 'ai', name: '냥비서', role: '쇼핑·응모', avatar: '🐱', time: '오전 11:58', text: '이벤트 응모 목록도 마감 순서대로 정리해 뒀습니다!🔥' }
    ],
    big: [
      { who: 'ai', name: '양비서', role: '가계부 전담', avatar: '🐑', time: '오전 08:01', text: '이번 달 카드 이용내역 통합 가계부에 반영 완료했습니다!' },
      { who: 'ai', name: '냥비서', role: '쇼핑·응모', avatar: '🐱', time: '오전 08:51', text: '오늘 응모할 이벤트 목록 확인했습니다.' }
    ],
    lounge: [
      { who: 'ai', name: '유키야', role: '총괄비서', avatar: '🐰', time: '오전 11:50', text: '여기는 라운지! 바쁜 일 끝나고 커피 한 잔 하면서 아이디어 정리하는 방이에요 ☕' }
    ]
  };

  const defaultMemos = [
    '오늘의 메모: 주간 일정 확인하기',
    '이번 달 가계부 마감일 체크',
    '장보기 목록 정리'
  ];

"""
html = html.replace(chats_old, chats_new, 1)

(OUT / "index.html").write_text(html, encoding="utf-8")
print("wrote", OUT / "index.html", (OUT / "index.html").stat().st_size, "bytes")
print("wrote", OUT / "map.png", (OUT / "map.png").stat().st_size, "bytes")
