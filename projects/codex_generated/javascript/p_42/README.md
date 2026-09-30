# React Component Library Demo

Reusable UI components (Button, Card, Modal) built with styled-components and Context-based state management for shared UI state (modal controls). PropTypes included for runtime validation.

## Setup
```bash
npm install
npm run dev
```
Visit http://localhost:5173 to view the demo.

## Components
- `Button` – Variants: `primary`, `secondary`, `outline`, `ghost`
- `Card` – Variants: `filled`, `outline`
- `Modal` – Controlled component connected via `UIProvider`

## State Management
`UIProvider` exposes hooks (`useUI`) for modal open/close state (can be extended to other UI concerns).

## Usage Example
```jsx
import { UIProvider, Button, Card, Modal, useUI } from './src/library';
```
See `src/App.jsx` for full example of composition.
