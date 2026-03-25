    # Smart Classroom UI/UX System

## Visual Tokens

- Primary: `#4F46E5`
- Accent: `#8B5CF6`
- Background: `#F9FAFB`
- Surface: glass-style white overlays with blur and soft borders
- Radius scale: `12px / 16px / 20px`
- Motion: `240ms ease-in-out`
- Typography: `Inter` with 16px base

## Core Components

- `app-shell`: role-based sidebar + topbar layout
- `app-card`: reusable glass card container
- `kpi-card`: dashboard metric card
- `status-badge`: semantic status states (`submitted`, `pending`, `late`)
- `dropzone`: drag-and-drop upload zone
- `toast-custom`: lightweight notifications
- `progress-ring`: student attendance progress indicator

## Page Patterns Implemented

- Authentication split-screen (`login`, `register`)
- Teacher dashboard, attendance, assignments, submissions, analytics
- Student dashboard, attendance, assignments, grades, analytics, assignment upload
- Public home hero section

## Accessibility + UX

- Focus-visible outlines on interactive controls
- High contrast text and status indicators
- Mobile-adaptive sidebar with toggle behavior
- Dark mode with persisted preference (`localStorage`)

## Figma Handoff Notes

Create matching component variants in Figma for:

1. Sidebar nav item (`default`, `hover`, `active`)
2. KPI card (`teacher`, `student`)
3. Status badge (`submitted`, `pending`, `late`)
4. Form inputs (`default`, `focus`, `error`)
5. Assignment card (`teacher`, `student`)

Use an 8px spacing system and desktop-first frames (`1440px`), then adapt to tablet (`1024px`) and mobile (`390px`).
