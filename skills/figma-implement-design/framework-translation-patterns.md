# Framework-Specific Translation Patterns

Load when the target project uses a framework OTHER than React + Tailwind (the MCP default output), when converting Figma MCP output to Vue, Svelte, Angular, or vanilla HTML/CSS, or when the project uses a non-Tailwind CSS system (CSS Modules, styled-components, Sass, plain CSS).

## React + Tailwind to Vue 3 (Composition API)

| React Pattern | Vue 3 Equivalent | Gotcha |
|---|---|---|
| `className="flex gap-4 p-2"` | `:class="'flex gap-4 p-2'"` or use project's CSS system | Vue uses `class` not `className`. If project uses Tailwind, classes transfer directly. If not, map to project CSS. |
| `{items.map(item => <Card key={item.id} />)}` | `<Card v-for="item in items" :key="item.id" />` | Vue uses `v-for` directive, not JS map. Key goes ON the element, not as a child prop. |
| `{isVisible && <Modal />}` | `<Modal v-if="isVisible" />` | Vue uses `v-if` directive for conditional rendering. `v-show` for CSS-based toggle (keeps DOM, hides visually). |
| `onClick={() => handleClick(id)}` | `@click="handleClick(id)"` | Vue uses `@event` shorthand for `v-on:event`. No arrow function wrapper needed for simple calls. |
| `useState(false)` | `ref(false)` or `reactive({})` | Import from `vue`. `ref` for primitives, `reactive` for objects. Access `.value` in script, not in template. |
| `useEffect(() => {}, [dep])` | `watch(dep, () => {})` or `watchEffect(() => {})` | `watch` for specific dependencies, `watchEffect` for auto-tracked. No dependency array -- Vue tracks automatically. |
| `<>{children}</>` | `<slot />` (default) or `<slot name="header" />` (named) | Vue uses slots instead of children prop. Named slots replace React's render props pattern. |
| `import styles from './Component.module.css'` | `<style scoped>` in SFC | Vue SFCs have built-in scoped styles. No CSS module import needed. Scoping uses data attributes, not class hashing. |

**Vue SFC structure from MCP output**: Wrap the JSX in `<template>`, convert state to `<script setup>`, move styles to `<style scoped>`. Every React component becomes one `.vue` file.

## React + Tailwind to Svelte 5

| React Pattern | Svelte 5 Equivalent | Gotcha |
|---|---|---|
| `className="flex gap-4"` | `class="flex gap-4"` | Direct transfer if project uses Tailwind. Svelte uses standard `class` attribute. |
| `{items.map(item => <Card />)}` | `{#each items as item (item.id)}<Card />{/each}` | Svelte uses block syntax `{#each}...{/each}`. Key goes in parens after `as item`. |
| `{isVisible && <Modal />}` | `{#if isVisible}<Modal />{/if}` | Block syntax `{#if}...{/if}`. Supports `{:else if}` and `{:else}`. |
| `onClick={handler}` | `onclick={handler}` | Svelte 5 uses lowercase event names (native DOM events). No `on:click` directive in Svelte 5 runes mode. |
| `useState(0)` | `let count = $state(0)` | Svelte 5 runes: `$state` for reactive variables. Directly mutable (`count++` works). |
| `useEffect(() => {}, [dep])` | `$effect(() => { /* auto-tracked */ })` | Svelte 5 auto-tracks dependencies. No dependency array. Runs when any referenced `$state` changes. |
| `{children}` | `{@render children()}` or `<slot />` (legacy) | Svelte 5 uses snippets and `{@render}`. Legacy `<slot>` still works but `{@render}` is preferred. |
| Styled-components / CSS Modules | `<style>` block (auto-scoped) | Svelte scopes all `<style>` by default. Use `:global()` for escape hatch. |

**Svelte 5 breaking changes from Svelte 4**: If the project is Svelte 4, use `export let` instead of `$props()`, `on:click` instead of `onclick`, and `$: reactive` instead of `$derived`. Check `package.json` for Svelte version before translating.

## React + Tailwind to Angular 17+

| React Pattern | Angular Equivalent | Gotcha |
|---|---|---|
| `className="flex gap-4"` | `class="flex gap-4"` or `[ngClass]="{'flex': true}"` | Angular uses standard `class` for static, `[ngClass]` for dynamic. If project has component library (Angular Material), use those classes. |
| `{items.map(item => <Card />)}` | `@for (item of items; track item.id) { <app-card /> }` | Angular 17+ uses `@for` control flow (not `*ngFor`). `track` is mandatory. |
| `{isVisible && <Modal />}` | `@if (isVisible) { <app-modal /> }` | Angular 17+ built-in `@if` control flow. Replaces `*ngIf`. |
| `onClick={handler}` | `(click)="handler()"` | Angular uses `(event)` binding syntax. Parentheses, not brackets. |
| `useState` / `useEffect` | `signal()` / `effect()` or `BehaviorSubject` + `async` pipe | Angular 17+ signals are the modern approach. Legacy apps may use RxJS Observables. Check project patterns. |
| Props: `{ title, onClick }` | `@Input() title: string; @Output() onClick = new EventEmitter()` | Angular separates inputs and outputs. With signals: `title = input<string>()`. |
| `{children}` | `<ng-content />` or `<ng-content select="[header]" />` | Angular content projection. Named slots use CSS selectors as discriminators. |
| Component file | 3 files: `.component.ts`, `.component.html`, `.component.css` (or inline) | Angular separates template, logic, and styles by default. Standalone components (Angular 17+) reduce boilerplate. |

**Angular standalone vs module**: Angular 17+ defaults to standalone components (no NgModule). If the project uses modules, wrap new components in the appropriate module. Check `angular.json` and existing component patterns.

## CSS System Translation

When the project does NOT use Tailwind, translate utility classes to the project's CSS system.

| Tailwind Class | CSS Equivalent | CSS Modules / Styled-Components |
|---|---|---|
| `flex` | `display: flex` | `.container { display: flex; }` |
| `gap-4` | `gap: 1rem` (Tailwind default: 1 unit = 0.25rem) | Map to project spacing token if it exists |
| `p-2` | `padding: 0.5rem` | Use project spacing variable: `padding: var(--space-2)` |
| `text-lg` | `font-size: 1.125rem; line-height: 1.75rem` | Use project typography token: `font-size: var(--text-lg)` |
| `bg-blue-500` | `background-color: #3b82f6` | NEVER hardcode hex. Map to project color token: `background-color: var(--color-primary)` |
| `rounded-lg` | `border-radius: 0.5rem` | Use project border radius token if available |
| `shadow-md` | `box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` | Use project shadow token or elevation system |
| `hover:bg-blue-600` | `.element:hover { background-color: #2563eb; }` | Map hover state to project interaction patterns |
| `sm:flex-row` | `@media (min-width: 640px) { flex-direction: row; }` | Use project breakpoint variables. Tailwind `sm` = 640px, `md` = 768px, `lg` = 1024px, `xl` = 1280px. |

**Token mapping priority**: Always check `get_variable_defs` output from Figma MCP for design tokens. Map Figma variables to the project's existing token system. Only fall back to hardcoded values when no token match exists within a reasonable tolerance.

## Component Library Mapping

When the project uses a component library, map MCP-generated primitives to library components.

| MCP Primitive | shadcn/ui | MUI (Material UI) | Vuetify | Angular Material |
|---|---|---|---|---|
| `<button>` | `<Button variant="..." />` | `<Button variant="..." />` | `<v-btn>` | `<button mat-button>` |
| `<input>` | `<Input />` | `<TextField />` | `<v-text-field>` | `<mat-form-field><input matInput></mat-form-field>` |
| `<select>` | `<Select>` + `<SelectItem>` | `<Select>` + `<MenuItem>` | `<v-select>` | `<mat-select>` + `<mat-option>` |
| `<dialog>` / modal | `<Dialog>` | `<Dialog>` | `<v-dialog>` | `<mat-dialog>` via `MatDialog.open()` |
| Card container | `<Card>` + `<CardContent>` | `<Card>` + `<CardContent>` | `<v-card>` | `<mat-card>` |
| `<table>` | `<Table>` components | `<Table>` or `<DataGrid>` | `<v-data-table>` | `<mat-table>` (CDK-based) |

**Library detection**: Check `package.json` for component library dependencies before translating. If the project has a custom component library, scan the components directory for existing primitives. Always prefer existing components over creating new ones from MCP output.
