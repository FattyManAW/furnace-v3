# 排爐系統 v3 — 設計規格書

**版本**：v3.0 | **日期**：2026-05-22 | **作者**：Vision（美術總監）
**標竿**：Asana Timeline + Notion Calendar + Linear Method

---

## 1. 色彩系統

### 主題層級
| Token | Light Mode | Dark Mode | 用途 |
|-------|-----------|----------|------|
| `--bg-primary` | `#fafafa` | `#0f1117` | 主背景 |
| `--bg-card` | `#ffffff` | `#1a1d2e` | 卡片/面板 |
| `--bg-surface` | `#f3f4f6` | `#252840` | 次級表面 |
| `--text-primary` | `#111827` | `#f1f5f9` | 主文字 |
| `--text-muted` | `#6b7280` | `#94a3b8` | 次文字 |
| `--border` | `#e5e7eb` | `#2d3148` | 邊框 |
| `--accent` | `#3b82f6` | `#60a5fa` | 主強調色 |
| `--accent-soft` | `#eff6ff` | `#1e3a5f` | 強調色背景 |

### 生命週期狀態色
| 狀態 | 色碼 | 用途 |
|------|------|------|
| pending | `#64748b` | 待排程（灰色） |
| scheduled | `#3b82f6` | 已排程（藍色） |
| in_progress | `#f59e0b` | 生產中（琥珀） |
| done | `#10b981` | 已完成（翠綠） |

### 爐次利用率色
| 區間 | 色碼 | 意義 |
|------|------|------|
| ≥90% | `#ef4444` | 高負載（紅） |
| 70-90% | `#f59e0b` | 中高負載（琥珀） |
| 40-70% | `#8b5cf6` | 中負載（紫） |
| <40% | `#3b82f6` | 低負載（藍） |

---

## 2. 字級系統
| Token | Size / Weight | 用途 |
|-------|-------------|------|
| Display | 28px / 700 | 頁面標題 |
| Heading | 18px / 600 | 區塊標題 |
| Body | 14px / 400 | 主要內容 |
| Caption | 12px / 400 | 輔助說明 |
| Micro | 10px / 400 | 工具提示、標籤 |

---

## 3. 元件庫

### GanttBar
- 拖曳 handle（GripVertical icon）
- 顏色對應 lifecycle_status
- Tooltip：plan_no / contract / qty / voltage / delivery_date
- 拖曳中：黃色高亮 + ring-2

### DependencyLine（SVG）
- 同合約號 entries 間繪製貝茲箭頭線
- 顏色：紫色 (#a78bfa)，透明度 50%
- marker-end 箭頭
- Toggle 開關控制顯示

### ZoomControl
- 三個按鈕：日(120px) / 週(80px) / 月(36px)
- 根據視窗寬度自適應 colW

### LifecycleBadge
- 四色 dot + 狀態文字
- 支援點擊切換 lifecycle_status

### KilnRow
- 爐次名稱 + 利用率色點
- Gantt 條塊 + 相依性連線覆蓋層

---

## 4. 版面結構

```
┌─────────────────────────────────────────────┐
│ Header: 標題 + ZoomControl + Nav Range       │
├─────────────────────────────────────────────┤
│ Gantt Grid                                  │
│ ┌──────┬────┬────┬────┬────┬────┬────┐     │
│ │ Kiln │Mon │Tue │Wed │Thu │Fri │Sat │     │
│ ├──────┼────┼────┼────┼────┼────┼────┤     │
│ │爐#1  │ ██ │ ██ │ ██ │    │    │    │     │
│ │爐#2  │    │ ██ │ ██ │ ██ │ ██ │    │     │
│ └──────┴────┴────┴────┴────┴────┴────┘     │
│              ↑ Dependency Arrows SVG         │
├─────────────────────────────────────────────┤
│ Legend: lifecycle + utilization             │
└─────────────────────────────────────────────┘
```

---

## 5. 動畫規範
- 拖曳：transition-all duration-100
- 縮放切換：scale 變化 CSS transition 300ms
- 相依線：opacity toggle 200ms
- 卡片 hover：scale(1.01) + shadow-lg
- 頁面進場：fade-slide-up 400ms（stagger 50ms per child）

---

## 6. 驗收標準
| # | 項目 | 方法 |
|---|------|------|
| 1 | Gantt 拖曳 | curl API before/after → screenshot 對比 |
| 2 | 相依線 | screenshot SVG arrows ≥1 條 |
| 3 | 縮放三級 | screenshot ×3 + Performance timing <200ms |
| 4 | 生命週期四色 | screenshot all 4 colors |
| 5 | 響應式 | screenshot 375/768/1440px |
| 6 | 主題切換 | screenshot light/dark mode |

---

## 7. 參考標竿
- Asana Timeline: https://asana.com/features/timeline
- Notion Calendar: https://www.notion.com/product/calendar
- Linear Method: https://linear.app/method