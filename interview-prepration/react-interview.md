# React Interview Reference

A senior-focused reference covering React core, hooks, patterns, testing, and Next.js. Concept + code snippet format.

---

## Table of Contents

### Part 1: React Core
1. [JSX & Rendering](#1-jsx--rendering)
2. [Components](#2-components)
3. [Hooks — Fundamentals](#3-hooks--fundamentals)
4. [Hooks — Advanced](#4-hooks--advanced)
5. [Component Lifecycle via Hooks](#5-component-lifecycle-via-hooks)
6. [Context API](#6-context-api)
7. [Performance Optimization](#7-performance-optimization)
8. [Rendering Patterns](#8-rendering-patterns)
9. [Error Boundaries](#9-error-boundaries)
10. [State Management Patterns](#10-state-management-patterns)
11. [Styling Approaches](#11-styling-approaches)
12. [React Testing Library + Jest](#12-react-testing-library--jest)
20. [React 19 Hooks & Compiler](#20-react-19-hooks--compiler)
21. [React Fiber](#21-react-fiber)
22. [Portals](#22-portals)
23. [Forms](#23-forms)
24. [TanStack Query](#24-tanstack-query)
25. [Zustand](#25-zustand)

### Part 2: Next.js
13. [App Router Architecture](#13-app-router-architecture)
14. [Server vs Client Components](#14-server-vs-client-components)
15. [Data Fetching](#15-data-fetching)
16. [Server Actions](#16-server-actions)
17. [Rendering Strategies](#17-rendering-strategies)
18. [Performance & Optimization](#18-performance--optimization)
19. [Auth & Middleware](#19-auth--middleware)
26. [Metadata API](#26-metadata-api)
27. [Streaming with Suspense](#27-streaming-with-suspense)

---

# Part 1: React Core

---

## 1. JSX & Rendering

### JSX Compilation

JSX is syntactic sugar. The React compiler (via Babel/SWC) transforms it into `React.createElement` calls. Since React 17, the new JSX transform imports `jsx` automatically — you no longer need `import React from 'react'` just for JSX.

```jsx
// What you write
const el = <Button color="blue" onClick={handleClick}>Submit</Button>;

// What it compiles to (new JSX transform)
import { jsx as _jsx } from 'react/jsx-runtime';
const el = _jsx(Button, { color: 'blue', onClick: handleClick, children: 'Submit' });
```

JSX expressions must return a single root — use `<>...</>` (Fragment) to avoid adding a DOM node:

```jsx
function List({ items }) {
  return (
    <>
      <h2>Items</h2>
      <ul>
        {items.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </>
  );
}
```

---

### Reconciliation & the Virtual DOM

React keeps a **virtual DOM** — a lightweight JS representation of the actual DOM. On each render, React diffs the new virtual DOM against the previous one (**reconciliation**) and applies only the changed nodes to the real DOM.

**Diffing heuristics:**
1. Two elements of different types produce completely different trees (full remount)
2. Elements of the same type update only changed attributes
3. The `key` prop tells React how to match list elements across renders

---

### Keys

Keys help React identify which list items changed, were added, or removed. Keys must be stable, unique among siblings, and not based on array index when items can reorder.

```jsx
// BAD — index as key causes bugs when list is reordered or items are inserted
{items.map((item, i) => <Item key={i} {...item} />)}

// GOOD — stable unique ID
{items.map((item) => <Item key={item.id} {...item} />)}

// Key also forces a remount (resets state) — useful trick
<Input key={userId} defaultValue={user.name} />
// Changing userId causes Input to fully remount with fresh state
```

---

## 2. Components

### Class Components vs Function Components

Class components were the original way to use state and lifecycle methods. Since React 16.8, hooks make function components fully capable — class components are rarely written in new code but appear in legacy codebases.

| | Class Component | Function Component |
|---|---|---|
| State | `this.state` / `this.setState` | `useState` / `useReducer` |
| Lifecycle | `componentDidMount`, `componentDidUpdate`, `componentWillUnmount` | `useEffect` |
| `this` binding | Required — easy to forget | No `this` |
| Code reuse | HOC / render props (verbose) | Custom hooks (simple) |
| Error boundaries | Supported | Not supported (still needs class) |
| Performance | `shouldComponentUpdate` / `PureComponent` | `React.memo` |

```jsx
// Class component
class Counter extends React.Component {
  state = { count: 0 };

  componentDidMount() {
    document.title = `Count: ${this.state.count}`;
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.count !== this.state.count) {
      document.title = `Count: ${this.state.count}`;
    }
  }

  componentWillUnmount() {
    document.title = 'App'; // cleanup
  }

  increment = () => this.setState((prev) => ({ count: prev.count + 1 }));

  render() {
    return (
      <div>
        <p>{this.state.count}</p>
        <button onClick={this.increment}>+</button>
      </div>
    );
  }
}

// Equivalent function component — shorter and clearer
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `Count: ${count}`;
    return () => { document.title = 'App'; };
  }, [count]);

  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount((c) => c + 1)}>+</button>
    </div>
  );
}
```

---

### Function Components & Props

A React component is a function that takes `props` and returns JSX (or `null`).

```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

function Button({ variant = 'primary', disabled = false, onClick, children }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

---

### Composition vs Inheritance

React favors composition over inheritance. Instead of extending a base component, pass behavior as props or children.

```jsx
// Composition via children
function Card({ title, children, footer }) {
  return (
    <div className="card">
      <div className="card-header">{title}</div>
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

// Usage
<Card title="Profile" footer={<Button>Save</Button>}>
  <Avatar src={user.avatar} />
  <p>{user.bio}</p>
</Card>
```

**Specialization** — a specific component wraps a generic one:

```jsx
function PrimaryButton(props) {
  return <Button {...props} variant="primary" />;
}
```

---

### `children` Patterns

```jsx
// React.Children utilities — iterate, count, map over children
function Tabs({ children }) {
  const [active, setActive] = React.useState(0);
  const tabs = React.Children.toArray(children);

  return (
    <div>
      <div className="tab-bar">
        {tabs.map((tab, i) => (
          <button key={i} onClick={() => setActive(i)}>
            {tab.props.label}
          </button>
        ))}
      </div>
      {tabs[active]}
    </div>
  );
}

// Render props — pass a function as children for maximum flexibility
function MouseTracker({ children }) {
  const [pos, setPos] = React.useState({ x: 0, y: 0 });
  return (
    <div onMouseMove={(e) => setPos({ x: e.clientX, y: e.clientY })}>
      {children(pos)}
    </div>
  );
}

<MouseTracker>
  {({ x, y }) => <p>Mouse at {x}, {y}</p>}
</MouseTracker>
```

---

## 3. Hooks — Fundamentals

### `useState`

`useState` returns a state value and a setter. The setter is stable (same reference across renders). Calling it schedules a re-render.

```jsx
const [count, setCount] = useState(0);

// Functional update — use when new state depends on old state
setCount((prev) => prev + 1);

// Lazy initializer — expensive initial value runs once
const [data, setData] = useState(() => JSON.parse(localStorage.getItem('data') ?? '{}'));

// Objects — state is replaced, not merged. Spread to merge manually
const [form, setForm] = useState({ name: '', email: '' });
setForm((prev) => ({ ...prev, email: 'new@example.com' }));
```

---

### `useReducer`

`useReducer` is `useState` with a reducer function. Prefer it when state logic is complex, multiple sub-values are related, or next state depends on multiple cases.

```jsx
const initialState = { count: 0, loading: false, error: null };

function reducer(state, action) {
  switch (action.type) {
    case 'increment': return { ...state, count: state.count + 1 };
    case 'decrement': return { ...state, count: state.count - 1 };
    case 'reset':     return initialState;
    case 'setLoading': return { ...state, loading: action.payload };
    default: throw new Error(`Unknown action: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </>
  );
}
```

---

### `useEffect`

`useEffect` runs after the render is committed to the DOM. It takes a setup function and an optional dependency array.

```jsx
// Runs after every render (no deps array) — rarely what you want
useEffect(() => { document.title = count; });

// Runs once on mount (empty deps) — equivalent to componentDidMount
useEffect(() => {
  const sub = eventBus.subscribe('update', handler);
  return () => sub.unsubscribe(); // cleanup on unmount
}, []);

// Runs when deps change
useEffect(() => {
  const controller = new AbortController();

  async function load() {
    try {
      const data = await fetchUser(userId, { signal: controller.signal });
      setUser(data);
    } catch (err) {
      if (err.name !== 'AbortError') setError(err);
    }
  }

  load();
  return () => controller.abort(); // cancel in-flight request on dep change
}, [userId]);
```

**Stale closure trap** — effects capture the values of variables at the time they run. Always include in deps:

```jsx
// BUG — count is always 0 inside the interval (stale closure)
useEffect(() => {
  const id = setInterval(() => console.log(count), 1000);
  return () => clearInterval(id);
}, []); // missing count in deps

// FIX — use functional update or include count in deps
useEffect(() => {
  const id = setInterval(() => setCount((c) => c + 1), 1000);
  return () => clearInterval(id);
}, []);
```

---

### `useLayoutEffect`

Same signature as `useEffect` but fires **synchronously** after DOM mutations, before the browser paints. Use for DOM measurements or preventing visual flicker.

```jsx
function Tooltip({ target }) {
  const ref = useRef(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  // Must run before paint to avoid tooltip flash at wrong position
  useLayoutEffect(() => {
    const rect = target.getBoundingClientRect();
    setPos({ top: rect.bottom, left: rect.left });
  }, [target]);

  return <div ref={ref} style={pos} className="tooltip" />;
}
```

---

### `useRef`

`useRef` returns a mutable object `{ current: value }` that persists across renders. Changing `.current` does **not** trigger a re-render.

```jsx
// DOM reference
function TextInput() {
  const inputRef = useRef(null);

  function focusInput() {
    inputRef.current?.focus();
  }

  return <input ref={inputRef} />;
}

// Mutable value that persists without causing re-renders
function Timer() {
  const intervalRef = useRef(null);
  const [running, setRunning] = useState(false);

  function start() {
    setRunning(true);
    intervalRef.current = setInterval(tick, 1000);
  }

  function stop() {
    setRunning(false);
    clearInterval(intervalRef.current);
  }

  // ...
}

// Tracking previous value
function usePrevious(value) {
  const ref = useRef(undefined);
  useEffect(() => { ref.current = value; });
  return ref.current; // returns value from previous render
}
```

---

## 4. Hooks — Advanced

### `useMemo`

Memoizes an expensive computed value. Re-runs only when deps change.

```jsx
function ProductList({ products, searchQuery, category }) {
  // Without useMemo, this runs on every render including unrelated state changes
  const filtered = useMemo(() => {
    return products
      .filter((p) => p.category === category)
      .filter((p) => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
      .sort((a, b) => a.price - b.price);
  }, [products, searchQuery, category]);

  return <ul>{filtered.map((p) => <ProductItem key={p.id} product={p} />)}</ul>;
}
```

**Don't over-use `useMemo`** — the memoization itself has cost. Only use it when:
- The computation is measurably slow
- The referential identity of the result matters (passed to `React.memo` child or another hook's deps)

---

### `useCallback`

Memoizes a function reference. The function is only recreated when deps change.

```jsx
function Parent({ userId }) {
  const [items, setItems] = useState([]);

  // Without useCallback, handleDelete is a new function every render
  // causing MemoizedChild to re-render even when items didn't change
  const handleDelete = useCallback((id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []); // no deps — setItems setter is stable

  return <MemoizedChild items={items} onDelete={handleDelete} />;
}

const MemoizedChild = React.memo(function Child({ items, onDelete }) {
  return items.map((item) => (
    <div key={item.id}>
      {item.name}
      <button onClick={() => onDelete(item.id)}>Delete</button>
    </div>
  ));
});
```

---

### `useContext`

Reads from a context. The component re-renders whenever the context value changes.

```jsx
const ThemeContext = React.createContext('light');

function App() {
  const [theme, setTheme] = useState('light');
  return (
    <ThemeContext.Provider value={theme}>
      <Page />
    </ThemeContext.Provider>
  );
}

function Button() {
  const theme = useContext(ThemeContext);
  return <button className={`btn-${theme}`}>Click</button>;
}
```

---

### `useId`

Generates a stable unique ID for accessibility attributes. IDs are stable across renders and consistent between server/client (no hydration mismatch).

```jsx
function FormField({ label, type = 'text' }) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input id={id} type={type} />
    </div>
  );
}
```

---

### `useTransition` & `useDeferredValue`

Both allow React to deprioritize a state update, keeping the UI responsive while expensive renders happen in the background.

```jsx
// useTransition — wrap the state update that triggers the expensive render
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  function handleSearch(e) {
    const q = e.target.value;
    setQuery(q); // urgent — updates input immediately

    startTransition(() => {
      setResults(expensiveSearch(q)); // non-urgent — can be interrupted
    });
  }

  return (
    <>
      <input value={query} onChange={handleSearch} />
      {isPending ? <Spinner /> : <ResultsList results={results} />}
    </>
  );
}

// useDeferredValue — defer a value you don't control (e.g., from props)
function ResultsList({ query }) {
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;

  const results = useMemo(() => expensiveSearch(deferredQuery), [deferredQuery]);

  return (
    <ul style={{ opacity: isStale ? 0.5 : 1 }}>
      {results.map((r) => <li key={r.id}>{r.name}</li>)}
    </ul>
  );
}
```

---

### Custom Hooks

Extract stateful logic into reusable functions. A custom hook is any function starting with `use` that calls other hooks.

```jsx
// useFetch — data fetching with loading/error state
function useFetch(url) {
  const [state, dispatch] = useReducer(
    (s, a) => ({ ...s, ...a }),
    { data: null, loading: true, error: null }
  );

  useEffect(() => {
    let cancelled = false;
    dispatch({ loading: true, error: null });

    fetch(url)
      .then((r) => r.json())
      .then((data) => { if (!cancelled) dispatch({ data, loading: false }); })
      .catch((error) => { if (!cancelled) dispatch({ error, loading: false }); });

    return () => { cancelled = true; };
  }, [url]);

  return state;
}

// useLocalStorage — persisted state
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setAndPersist = useCallback((newValue) => {
    setValue((prev) => {
      const next = typeof newValue === 'function' ? newValue(prev) : newValue;
      localStorage.setItem(key, JSON.stringify(next));
      return next;
    });
  }, [key]);

  return [value, setAndPersist];
}

// useDebounce
function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}

// useEventListener
function useEventListener(event, handler, element = window) {
  const savedHandler = useRef(handler);

  useLayoutEffect(() => { savedHandler.current = handler; }, [handler]);

  useEffect(() => {
    const listener = (e) => savedHandler.current(e);
    element?.addEventListener(event, listener);
    return () => element?.removeEventListener(event, listener);
  }, [event, element]);
}
```

---

## 5. Component Lifecycle via Hooks

Hooks map cleanly to the class lifecycle:

| Class lifecycle | Hook equivalent |
|---|---|
| `constructor` | `useState` / `useReducer` initializer |
| `componentDidMount` | `useEffect(() => { ... }, [])` |
| `componentDidUpdate` | `useEffect(() => { ... }, [deps])` |
| `componentWillUnmount` | Cleanup function returned from `useEffect` |
| `shouldComponentUpdate` | `React.memo` + `useMemo` / `useCallback` |
| `getSnapshotBeforeUpdate` | `useLayoutEffect` |
| `getDerivedStateFromProps` | Derive during render (no hook needed) |

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  // Mount + update (when userId changes)
  useEffect(() => {
    let cancelled = false;
    fetchUser(userId).then((u) => { if (!cancelled) setUser(u); });
    return () => { cancelled = true; }; // unmount cleanup
  }, [userId]);

  // Mount only
  useEffect(() => {
    analytics.track('profile_viewed');
  }, []);

  // Every render
  useEffect(() => {
    document.title = user ? `${user.name}'s Profile` : 'Loading...';
  });

  if (!user) return <Spinner />;
  return <div>{user.name}</div>;
}
```

### `StrictMode` Double-Invoke

In development, React 18 `StrictMode` mounts components twice (mount → unmount → remount) to surface effects that don't properly clean up. This is intentional — if your effect breaks on double-invoke, your cleanup is missing or incorrect.

```jsx
// This effect leaks in StrictMode — no cleanup
useEffect(() => {
  const sub = eventBus.on('update', handler);
  // missing return () => sub.off()
}, []);
```

---

## 6. Context API

### Creating & Providing Context

```tsx
interface AuthContextValue {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = useCallback(async (credentials: Credentials) => {
    const user = await authService.login(credentials);
    setUser(user);
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, login, logout }), [user, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook — throws if used outside provider
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
```

---

### Re-render Pitfalls

Every component that calls `useContext` re-renders when the context value changes. If the provider's value is a new object on every render, all consumers re-render too.

```jsx
// BAD — new object on every render, all consumers re-render
function Provider({ children }) {
  const [user, setUser] = useState(null);
  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

// GOOD — memoize the value
function Provider({ children }) {
  const [user, setUser] = useState(null);
  const value = useMemo(() => ({ user, setUser }), [user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
```

**Split contexts** to limit re-render scope — stable setters in one context, changing values in another:

```jsx
const UserContext = React.createContext(null);        // re-renders on user change
const UserActionsContext = React.createContext(null); // stable — never re-renders

function Provider({ children }) {
  const [user, setUser] = useState(null);
  const actions = useMemo(() => ({ setUser, logout: () => setUser(null) }), []);

  return (
    <UserActionsContext.Provider value={actions}>
      <UserContext.Provider value={user}>
        {children}
      </UserContext.Provider>
    </UserActionsContext.Provider>
  );
}
```

### When NOT to Use Context

- **Frequently changing values** (e.g., mouse position, scroll offset) — use local state or a pub/sub pattern instead
- **Deeply nested prop passing of stable values** — just pass props; prop drilling only becomes a problem at 4+ levels
- **Server state** (API data) — use a dedicated library (React Query / SWR) instead

---

## 7. Performance Optimization

### `React.memo`

Wraps a component to skip re-rendering if props haven't changed (shallow comparison by default).

```jsx
const ExpensiveList = React.memo(function ExpensiveList({ items, onSelect }) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id} onClick={() => onSelect(item.id)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
});

// Custom comparison — return true to skip render
const Chart = React.memo(
  function Chart({ data, width }) { /* ... */ },
  (prev, next) => prev.data === next.data && prev.width === next.width
);
```

---

### Code Splitting with `React.lazy` + `Suspense`

```jsx
// Lazy-load heavy routes — they're only downloaded when navigated to
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Settings = React.lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Router>
      <Suspense fallback={<PageSpinner />}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

// Suspense boundary can be nested — fine-grained loading states
function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart /> {/* lazy-loaded or data-fetching */}
      </Suspense>
    </div>
  );
}
```

---

### React Profiler

```jsx
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration, baseDuration) {
  if (actualDuration > 16) { // > 1 frame at 60fps
    console.warn(`Slow render in ${id} (${phase}): ${actualDuration.toFixed(2)}ms`);
  }
}

<Profiler id="ProductList" onRender={onRenderCallback}>
  <ProductList products={products} />
</Profiler>
```

Use the **React DevTools Profiler** for visual flame graphs — record interactions, identify components that re-render unnecessarily.

---

### Virtualization for Long Lists

Render only visible rows to avoid thousands of DOM nodes.

```jsx
import { FixedSizeList } from 'react-window';

function VirtualList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  );

  return (
    <FixedSizeList height={600} itemCount={items.length} itemSize={50} width="100%">
      {Row}
    </FixedSizeList>
  );
}
```

---

## 8. Rendering Patterns

### Controlled vs Uncontrolled Components

**Controlled** — React owns the value via state. Source of truth is in React.

```jsx
function ControlledInput() {
  const [value, setValue] = useState('');
  return <input value={value} onChange={(e) => setValue(e.target.value)} />;
}
```

**Uncontrolled** — the DOM owns the value. Access via ref.

```jsx
function UncontrolledInput() {
  const ref = useRef(null);

  function handleSubmit(e) {
    e.preventDefault();
    console.log(ref.current.value);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input ref={ref} defaultValue="initial" />
      <button type="submit">Submit</button>
    </form>
  );
}
```

Use controlled when: you need instant validation, conditional disabling, or format-on-type.
Use uncontrolled when: integrating with non-React code, file inputs, or large forms where individual field re-renders are costly.

---

### Higher-Order Components (HOC)

A HOC is a function that takes a component and returns a new component with added behavior. Largely superseded by hooks, but still common in libraries.

```jsx
function withAuth(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    const { user } = useAuth();
    if (!user) return <Navigate to="/login" />;
    return <WrappedComponent {...props} user={user} />;
  };
}

const ProtectedDashboard = withAuth(Dashboard);
```

---

### Compound Components

Components that share implicit state through context, designed to be used together.

```tsx
const TabsContext = React.createContext(null);

function Tabs({ children, defaultValue }) {
  const [active, setActive] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

Tabs.List = function TabList({ children }) {
  return <div className="tab-list" role="tablist">{children}</div>;
};

Tabs.Trigger = function TabTrigger({ value, children }) {
  const { active, setActive } = useContext(TabsContext);
  return (
    <button
      role="tab"
      aria-selected={active === value}
      onClick={() => setActive(value)}
    >
      {children}
    </button>
  );
};

Tabs.Content = function TabContent({ value, children }) {
  const { active } = useContext(TabsContext);
  if (active !== value) return null;
  return <div role="tabpanel">{children}</div>;
};

// Usage — expressive, flexible, no prop drilling
<Tabs defaultValue="profile">
  <Tabs.List>
    <Tabs.Trigger value="profile">Profile</Tabs.Trigger>
    <Tabs.Trigger value="settings">Settings</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="profile"><ProfileForm /></Tabs.Content>
  <Tabs.Content value="settings"><SettingsForm /></Tabs.Content>
</Tabs>
```

---

### `forwardRef` & `useImperativeHandle`

`forwardRef` allows a parent to obtain a ref to a child's DOM node or instance.

```tsx
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  function Input({ label, ...props }, ref) {
    return (
      <div>
        <label>{label}</label>
        <input ref={ref} {...props} />
      </div>
    );
  }
);

// Parent
const inputRef = useRef<HTMLInputElement>(null);
<Input ref={inputRef} label="Name" />
inputRef.current?.focus();
```

`useImperativeHandle` customizes what the ref exposes — expose only a controlled API, not the full DOM node:

```tsx
interface VideoHandle {
  play: () => void;
  pause: () => void;
  seek: (time: number) => void;
}

const VideoPlayer = React.forwardRef<VideoHandle, VideoProps>(
  function VideoPlayer({ src }, ref) {
    const videoRef = useRef<HTMLVideoElement>(null);

    useImperativeHandle(ref, () => ({
      play: () => videoRef.current?.play(),
      pause: () => videoRef.current?.pause(),
      seek: (time) => { if (videoRef.current) videoRef.current.currentTime = time; },
    }));

    return <video ref={videoRef} src={src} />;
  }
);
```

---

## 9. Error Boundaries

Error boundaries catch JavaScript errors in their child tree, log them, and render a fallback UI. They must be class components — there is no hook equivalent (yet).

```tsx
import { Component, ReactNode } from 'react';

interface Props {
  fallback: ReactNode | ((error: Error, reset: () => void) => ReactNode);
  children: ReactNode;
  onError?: (error: Error, info: { componentStack: string }) => void;
}

interface State {
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    this.props.onError?.(error, info);
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      const { fallback } = this.props;
      return typeof fallback === 'function'
        ? fallback(this.state.error, this.reset)
        : fallback;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary
  fallback={(error, reset) => (
    <div>
      <p>Something went wrong: {error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )}
  onError={(err, info) => errorReporter.capture(err, info)}
>
  <UserProfile userId={id} />
</ErrorBoundary>
```

**`react-error-boundary`** package provides a hook-friendly wrapper with `useErrorBoundary` for imperative error throwing from event handlers.

---

## 9b. Memory Leaks in React

Memory leaks in React occur when a component is unmounted but something still holds a reference to it — typically a pending async operation, subscription, or timer that tries to call `setState` on a dead component.

### Common Patterns & Fixes

**1. Async operation after unmount:**

```jsx
// LEAKS — setState called after component unmounts if fetch is slow
useEffect(() => {
  fetchUser(id).then((user) => setUser(user)); // no cleanup
}, [id]);

// FIX — AbortController cancels the fetch on unmount
useEffect(() => {
  const controller = new AbortController();
  fetchUser(id, { signal: controller.signal })
    .then((user) => setUser(user))
    .catch((err) => { if (err.name !== 'AbortError') setError(err); });
  return () => controller.abort();
}, [id]);
```

**2. `setInterval` / `setTimeout` not cleared:**

```jsx
// LEAKS
useEffect(() => {
  const id = setInterval(() => setCount((c) => c + 1), 1000);
  // missing clearInterval
}, []);

// FIX
useEffect(() => {
  const id = setInterval(() => setCount((c) => c + 1), 1000);
  return () => clearInterval(id);
}, []);
```

**3. Event listeners not removed:**

```jsx
// LEAKS
useEffect(() => {
  window.addEventListener('resize', handleResize);
  // missing removeEventListener
}, []);

// FIX
useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

**4. WebSocket / subscription not closed:**

```jsx
useEffect(() => {
  const ws = new WebSocket(url);
  ws.onmessage = (e) => setMessages((m) => [...m, e.data]);
  return () => ws.close(); // cleanup closes the connection
}, [url]);
```

**5. Closures in `useCallback` capturing stale state:**

This doesn't leak memory but causes stale data bugs — always include deps in the array.

### React 18 `StrictMode` Double-Mount

In development, `StrictMode` mounts → unmounts → remounts every component. This surfaces leaked effects — if your component breaks on the second mount, the cleanup is missing.

---

## 10. State Management Patterns

### Choosing the Right Tool

| Scenario | Recommended |
|---|---|
| Local UI state (toggle, form) | `useState` |
| Complex state with multiple actions | `useReducer` |
| Shared state across distant components | Context + `useReducer` |
| Server/async state (API data) | React Query / SWR |
| High-frequency updates (mouse, canvas) | Local ref + manual DOM |

---

### `useState` vs `useReducer`

```jsx
// useState — simple, independent values
const [open, setOpen] = useState(false);
const [count, setCount] = useState(0);

// useReducer — when multiple state values interact
// or when next state depends on multiple conditions
const [state, dispatch] = useReducer(reducer, {
  status: 'idle',   // 'idle' | 'loading' | 'success' | 'error'
  data: null,
  error: null,
});

// With useReducer, state transitions are explicit and testable
function reducer(state, action) {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, status: 'loading', error: null };
    case 'FETCH_SUCCESS':
      return { status: 'success', data: action.payload, error: null };
    case 'FETCH_ERROR':
      return { ...state, status: 'error', error: action.payload };
    default:
      return state;
  }
}
```

---

### Context + `useReducer` for Global State

A lightweight Redux-like pattern without any library:

```tsx
type Action =
  | { type: 'SET_USER'; payload: User }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<Settings> };

interface AppState {
  user: User | null;
  settings: Settings;
}

const initialState: AppState = { user: null, settings: defaultSettings };

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_USER': return { ...state, user: action.payload };
    case 'LOGOUT': return { ...state, user: null };
    case 'UPDATE_SETTINGS':
      return { ...state, settings: { ...state.settings, ...action.payload } };
    default: return state;
  }
}

const StateContext = React.createContext<AppState>(initialState);
const DispatchContext = React.createContext<React.Dispatch<Action>>(() => {});

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);
  return (
    <DispatchContext.Provider value={dispatch}>
      <StateContext.Provider value={state}>
        {children}
      </StateContext.Provider>
    </DispatchContext.Provider>
  );
}

export const useAppState = () => useContext(StateContext);
export const useDispatch = () => useContext(DispatchContext);
```

---

### Derived State

Compute from existing state during render — don't store derived values in state.

```jsx
// BAD — redundant state, easy to get out of sync
const [items, setItems] = useState([]);
const [filteredItems, setFilteredItems] = useState([]);

// GOOD — derive during render
const [items, setItems] = useState([]);
const [query, setQuery] = useState('');
const filteredItems = items.filter((i) => i.name.includes(query));

// For expensive derivations, memoize
const sortedFilteredItems = useMemo(
  () => filteredItems.slice().sort((a, b) => a.price - b.price),
  [filteredItems]
);
```

---

## 11. Styling Approaches

### CSS Modules

Scoped CSS — class names are locally scoped by default. Zero runtime cost.

```css
/* Button.module.css */
.button {
  padding: 8px 16px;
  border-radius: 4px;
}
.primary { background: #0070f3; color: white; }
.secondary { background: transparent; border: 1px solid #0070f3; }
```

```jsx
import styles from './Button.module.css';

function Button({ variant = 'primary', children }) {
  return (
    <button className={`${styles.button} ${styles[variant]}`}>
      {children}
    </button>
  );
}
```

**Trade-offs:** No dynamic styles, co-location is manual, works great for static UI.

---

### Tailwind CSS

Utility-first CSS. Styles live entirely in the JSX class names. No context-switching, no naming things, highly consistent design tokens.

```jsx
function Button({ variant = 'primary', children, disabled }) {
  const base = 'inline-flex items-center px-4 py-2 rounded-md font-medium transition-colors';
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300',
    secondary: 'border border-blue-600 text-blue-600 hover:bg-blue-50',
    ghost: 'text-gray-600 hover:bg-gray-100',
  };

  return (
    <button className={`${base} ${variants[variant]}`} disabled={disabled}>
      {children}
    </button>
  );
}
```

**Trade-offs:** Verbose JSX, requires design system discipline, not great for truly dynamic values (use CSS variables for those).

---

### styled-components / Emotion

CSS-in-JS — styles are co-located with components, support dynamic styles via props, generate scoped class names at runtime.

```jsx
import styled from 'styled-components';

const Button = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  background: ${(props) => props.variant === 'primary' ? '#0070f3' : 'transparent'};
  color: ${(props) => props.variant === 'primary' ? 'white' : '#0070f3'};
  border: ${(props) => props.variant === 'secondary' ? '1px solid #0070f3' : 'none'};
`;

<Button variant="primary">Submit</Button>
```

**Trade-offs:** Runtime style injection (performance cost, flash on SSR without setup), large bundle, difficult with RSC (Server Components don't support runtime CSS-in-JS).

---

### Decision Guide

| Need | Best fit |
|---|---|
| Static styles, maximum performance | CSS Modules |
| Design system with utility classes | Tailwind |
| Highly dynamic styles tied to JS values | styled-components / Emotion |
| Server Components (Next.js App Router) | CSS Modules or Tailwind (avoid runtime CSS-in-JS) |

---

## 12. React Testing Library + Jest

### Core Philosophy

RTL encourages testing from the user's perspective — query by role, label, or text rather than implementation details (class names, component structure).

> "The more your tests resemble the way your software is used, the more confidence they can give you." — Kent C. Dodds

---

### Render, Query, Assert

```jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

test('calls onClick when clicked', async () => {
  const user = userEvent.setup();
  const handleClick = jest.fn();

  render(<Button onClick={handleClick}>Submit</Button>);

  await user.click(screen.getByRole('button', { name: /submit/i }));

  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

---

### Query Priority

Use queries in this order (most accessible → least):

1. `getByRole` — preferred, matches ARIA roles
2. `getByLabelText` — for form inputs
3. `getByPlaceholderText`
4. `getByText`
5. `getByDisplayValue`
6. `getByAltText` — for images
7. `getByTitle`
8. `getByTestId` — last resort, use `data-testid`

```jsx
// getByRole — semantic and resilient
screen.getByRole('button', { name: /submit/i });
screen.getByRole('heading', { name: /welcome/i, level: 1 });
screen.getByRole('textbox', { name: /email/i });
screen.getByRole('checkbox', { name: /agree to terms/i });

// getByLabelText — for form fields
screen.getByLabelText(/email address/i);

// getAllBy, queryBy, findBy variants
screen.queryByText(/error/i);       // returns null if not found (no throw)
await screen.findByText(/loaded/i); // async — waits for element to appear
```

---

### Async Testing

```jsx
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { UserProfile } from './UserProfile';

// Mock Service Worker — intercept real fetch calls
const server = setupServer(
  rest.get('/api/users/:id', (req, res, ctx) => {
    return res(ctx.json({ id: 1, name: 'Alice', email: 'alice@example.com' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('displays user data after loading', async () => {
  render(<UserProfile userId={1} />);

  // Assert loading state
  expect(screen.getByRole('progressbar')).toBeInTheDocument();

  // Wait for data to appear
  expect(await screen.findByText('Alice')).toBeInTheDocument();
  expect(screen.getByText('alice@example.com')).toBeInTheDocument();
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
});

test('shows error when request fails', async () => {
  server.use(
    rest.get('/api/users/:id', (req, res, ctx) => res(ctx.status(500)))
  );

  render(<UserProfile userId={1} />);

  expect(await screen.findByRole('alert')).toHaveTextContent(/something went wrong/i);
});
```

---

### Mocking

```jsx
// Mock a module
jest.mock('../services/authService', () => ({
  login: jest.fn(),
  logout: jest.fn(),
}));

// Mock a custom hook
jest.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ user: { id: 1, name: 'Alice' }, logout: jest.fn() }),
}));

// Mock timers
jest.useFakeTimers();
// ... trigger something that uses setTimeout
jest.runAllTimers();
jest.useRealTimers();

// Spy on and mock a specific method
const spy = jest.spyOn(console, 'error').mockImplementation(() => {});
// ... test code that would console.error
expect(spy).toHaveBeenCalledWith(expect.stringMatching(/required prop/));
spy.mockRestore();
```

---

### Testing Custom Hooks

```jsx
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

test('increments counter', () => {
  const { result } = renderHook(() => useCounter(0));

  expect(result.current.count).toBe(0);

  act(() => result.current.increment());

  expect(result.current.count).toBe(1);
});

// Hook that needs a provider
test('useAuth returns current user', () => {
  const wrapper = ({ children }) => (
    <AuthProvider initialUser={mockUser}>{children}</AuthProvider>
  );

  const { result } = renderHook(() => useAuth(), { wrapper });
  expect(result.current.user).toEqual(mockUser);
});
```

---

# Part 2: Next.js

---

## 13. App Router Architecture

Next.js 13+ App Router uses the `app/` directory. The file system defines the route tree.

```
app/
├── layout.tsx          ← root layout (wraps all pages)
├── page.tsx            ← route: /
├── loading.tsx         ← automatic loading UI for this segment
├── error.tsx           ← error boundary for this segment
├── not-found.tsx       ← 404 for this segment
├── (marketing)/        ← route group — no URL segment
│   ├── about/
│   │   └── page.tsx    ← route: /about
│   └── pricing/
│       └── page.tsx    ← route: /pricing
├── dashboard/
│   ├── layout.tsx      ← nested layout (wraps dashboard pages)
│   ├── page.tsx        ← route: /dashboard
│   └── [id]/
│       └── page.tsx    ← route: /dashboard/123
└── api/
    └── users/
        └── route.ts    ← API route: GET/POST /api/users
```

### Layouts

Layouts persist across navigations — state is preserved, DOM is not remounted.

```tsx
// app/layout.tsx — root layout
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}

// app/dashboard/layout.tsx — nested layout
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="dashboard">
      <Sidebar />
      <div className="dashboard-content">{children}</div>
    </div>
  );
}
```

### Route Handlers (API Routes)

```ts
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = Number(searchParams.get('page') ?? '1');

  const users = await userService.findAll({ page });
  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await userService.create(body);
  return NextResponse.json(user, { status: 201 });
}

// app/api/users/[id]/route.ts
export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await userService.findById(Number(params.id));
  if (!user) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  return NextResponse.json(user);
}
```

---

## 14. Server vs Client Components

React Server Components (RSC) render on the server — they can be async, access databases/filesystems directly, and never ship their code to the client.

**Default in App Router: all components are Server Components.** Add `"use client"` to opt into client-side rendering.

```tsx
// Server Component — no "use client"
// Can: async/await, access DB, read filesystem, use server-only secrets
// Cannot: useState, useEffect, browser APIs, event handlers
async function UserProfile({ userId }: { userId: number }) {
  const user = await db.users.findUnique({ where: { id: userId } }); // direct DB access

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <LikeButton initialLikes={user.likes} /> {/* client component */}
    </div>
  );
}

// Client Component
'use client';

import { useState } from 'react';

function LikeButton({ initialLikes }: { initialLikes: number }) {
  const [likes, setLikes] = useState(initialLikes);
  return (
    <button onClick={() => setLikes((l) => l + 1)}>
      ❤️ {likes}
    </button>
  );
}
```

### `"use client"` Boundary Rules

- `"use client"` marks a boundary — the component and all its imports become client code
- You **can** pass Server Components as `children` or props to Client Components — they render on the server and their output (HTML) is passed as a prop

```tsx
// OK — ServerComponent renders on server, output passed as children
function ClientLayout({ children }: { children: React.ReactNode }) {
  'use client';
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button onClick={() => setOpen(!open)}>Toggle</button>
      {open && children}
    </div>
  );
}

// In a Server Component
<ClientLayout>
  <ServerComponent /> {/* renders on server */}
</ClientLayout>
```

### Serialization Constraints

Props passed from Server to Client Components must be serializable (JSON-compatible). Functions, class instances, and Dates must be converted.

```tsx
// ERROR — functions are not serializable
<ClientComponent onClick={serverFunction} />

// ERROR — class instances are not serializable
<ClientComponent user={new UserClass(data)} />

// OK — plain objects
<ClientComponent user={{ id: 1, name: 'Alice' }} />
```

---

## 15. Data Fetching

### Server Component Fetch with Caching

```tsx
// fetch in Server Components is extended by Next.js with caching
async function ProductList() {
  // Cached indefinitely (static) — revalidated on-demand or by tag
  const products = await fetch('https://api.example.com/products', {
    next: { tags: ['products'] },
  }).then((r) => r.json());

  // Revalidate every 60 seconds (ISR behavior)
  const config = await fetch('https://api.example.com/config', {
    next: { revalidate: 60 },
  }).then((r) => r.json());

  // No cache — fresh on every request (SSR behavior)
  const user = await fetch('https://api.example.com/me', {
    cache: 'no-store',
  }).then((r) => r.json());

  return <ul>{products.map((p) => <ProductItem key={p.id} product={p} />)}</ul>;
}
```

### On-Demand Revalidation

```ts
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from 'next/cache';

export async function POST(req: NextRequest) {
  const { tag, secret } = await req.json();
  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  revalidateTag(tag);          // revalidate all fetches tagged with this
  revalidatePath('/products'); // or revalidate a specific path
  return NextResponse.json({ revalidated: true });
}
```

### `generateStaticParams` — Static Generation for Dynamic Routes

```tsx
// app/products/[slug]/page.tsx
export async function generateStaticParams() {
  const products = await fetch('https://api.example.com/products').then(r => r.json());
  return products.map((p: Product) => ({ slug: p.slug }));
}

export default async function ProductPage({ params }: { params: { slug: string } }) {
  const product = await fetch(`https://api.example.com/products/${params.slug}`).then(r => r.json());
  return <ProductDetail product={product} />;
}
```

---

## 16. Server Actions

Server Actions are async functions that run on the server, callable from Client Components. They replace API routes for mutations.

```tsx
// actions/users.ts
'use server';

import { revalidatePath } from 'next/cache';

export async function createUser(formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;

  // Validate
  if (!name || !email) throw new Error('Name and email are required');

  await db.users.create({ data: { name, email } });
  revalidatePath('/users');
}

// Client Component — form with progressive enhancement
'use client';
import { createUser } from '@/actions/users';
import { useFormState, useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return <button type="submit" disabled={pending}>{pending ? 'Saving...' : 'Save'}</button>;
}

function CreateUserForm() {
  const [state, formAction] = useFormState(createUser, null);
  return (
    <form action={formAction}>
      <input name="name" required />
      <input name="email" type="email" required />
      {state?.error && <p role="alert">{state.error}</p>}
      <SubmitButton />
    </form>
  );
}
```

### Optimistic Updates with `useOptimistic`

```tsx
'use client';
import { useOptimistic } from 'react';
import { toggleLike } from '@/actions/posts';

function LikeButton({ postId, initialLikes, initialLiked }) {
  const [optimisticState, setOptimistic] = useOptimistic(
    { likes: initialLikes, liked: initialLiked },
    (state, action) => ({
      likes: state.likes + (action === 'like' ? 1 : -1),
      liked: action === 'like',
    })
  );

  async function handleClick() {
    const action = optimisticState.liked ? 'unlike' : 'like';
    setOptimistic(action); // update UI immediately
    await toggleLike(postId, action); // then sync with server
  }

  return (
    <button onClick={handleClick}>
      {optimisticState.liked ? '❤️' : '🤍'} {optimisticState.likes}
    </button>
  );
}
```

---

## 17. Rendering Strategies

### SSR (Server-Side Rendering)

Page renders on the server per request. Always fresh. Use for personalized pages, real-time data.

```tsx
// Dynamic rendering triggered by: cookies(), headers(), searchParams, cache: 'no-store'
import { cookies } from 'next/headers';

export default async function Dashboard() {
  const session = cookies().get('session')?.value;
  const user = await getUserFromSession(session);
  return <DashboardContent user={user} />;
}
```

### SSG (Static Site Generation)

Pages pre-rendered at build time. Fastest possible response. Use for content that doesn't change often.

```tsx
// Static by default — no dynamic data sources
export default async function BlogPost({ params }) {
  const post = await fetch(`https://cms.example.com/posts/${params.slug}`, {
    next: { tags: [`post-${params.slug}`] },
  }).then(r => r.json());

  return <article>{post.content}</article>;
}
```

### ISR (Incremental Static Regeneration)

Pre-rendered at build, but regenerated in the background when stale.

```tsx
export default async function ProductPage({ params }) {
  const product = await fetch(`/api/products/${params.id}`, {
    next: { revalidate: 3600 }, // regenerate at most every hour
  }).then(r => r.json());

  return <ProductDetail product={product} />;
}
```

### PPR (Partial Pre-Rendering) — Next.js 15+

Static shell with dynamic holes — the static parts ship immediately, dynamic parts stream in.

```tsx
import { Suspense } from 'react';

export default function ProductPage({ params }) {
  return (
    <div>
      {/* Static — pre-rendered */}
      <StaticProductInfo productId={params.id} />

      {/* Dynamic — streams in after */}
      <Suspense fallback={<RecommendationsSkeleton />}>
        <PersonalizedRecommendations userId={getCurrentUserId()} />
      </Suspense>
    </div>
  );
}
```

### Decision Guide

| Strategy | When to use |
|---|---|
| SSG | Blog posts, docs, marketing pages — rarely changes |
| ISR | Product pages, news — changes periodically |
| SSR | Dashboards, user-specific pages — changes per request |
| CSR | Highly interactive UIs where data is user-specific post-login |
| PPR | Mostly static pages with a few personalized sections |

---

## 18. Performance & Optimization

### `next/image`

Automatically optimizes images: lazy loading, WebP conversion, responsive `srcSet`, prevents layout shift via reserved space.

```tsx
import Image from 'next/image';

// Local image — width/height inferred from import
import heroImg from '@/public/hero.jpg';
<Image src={heroImg} alt="Hero" priority />

// Remote image — must specify size (or use fill)
<Image
  src="https://cdn.example.com/photo.jpg"
  alt="Product"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, 50vw"
/>

// Fill container — parent must have position: relative
<div style={{ position: 'relative', aspectRatio: '16/9' }}>
  <Image src={src} alt={alt} fill style={{ objectFit: 'cover' }} />
</div>
```

### `next/font`

Self-hosts fonts — no layout shift, no external network request, automatic subset.

```tsx
import { Inter, Roboto_Mono } from 'next/font/google';
import localFont from 'next/font/local';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

// layout.tsx
<html className={inter.variable}>
```

### Route Prefetching

Next.js automatically prefetches linked pages when their `<Link>` enters the viewport.

```tsx
import Link from 'next/link';

// Prefetched automatically in production
<Link href="/dashboard">Dashboard</Link>

// Disable prefetch for authenticated-only pages
<Link href="/admin" prefetch={false}>Admin</Link>

// Programmatic navigation
import { useRouter } from 'next/navigation';
const router = useRouter();
router.push('/dashboard');
router.prefetch('/checkout'); // prefetch manually
```

### Bundle Analysis

```bash
# Install analyzer
npm install @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});
module.exports = withBundleAnalyzer({});

# Analyze
ANALYZE=true npm run build
```

---

## 18b. Pages Router vs App Router

Next.js has two routing systems. New projects should use App Router (stable since Next.js 13.4).

| | Pages Router (`pages/`) | App Router (`app/`) |
|---|---|---|
| Data fetching | `getStaticProps`, `getServerSideProps`, `getStaticPaths` | `async` Server Components, `fetch` with cache options |
| Layouts | `_app.js`, per-page `getLayout` pattern | Nested `layout.tsx` files (persist across navigation) |
| Server Components | No — all components are client-side | Yes — default |
| Streaming | No | Yes — `<Suspense>` boundaries |
| Loading UI | Manual | `loading.tsx` auto-wraps with Suspense |
| Error UI | `_error.js` | `error.tsx` per segment |
| API routes | `pages/api/*.ts` | `app/api/*/route.ts` |
| Middleware | `middleware.ts` | Same |

### Pages Router Data Fetching

```tsx
// getStaticProps — runs at BUILD time, result passed as props
// Use for: static pages, content that rarely changes (blog, docs)
export async function getStaticProps(context) {
  const { params, locale } = context;
  const post = await fetchPost(params.slug);

  if (!post) return { notFound: true }; // renders 404 page

  return {
    props: { post },
    revalidate: 60, // ISR: regenerate at most every 60s
  };
}

// getStaticPaths — required with getStaticProps for dynamic routes
export async function getStaticPaths() {
  const posts = await fetchAllPosts();
  return {
    paths: posts.map((p) => ({ params: { slug: p.slug } })),
    fallback: 'blocking', // 'blocking' | true | false
    // false: 404 for unknown paths
    // true: show fallback UI while generating
    // 'blocking': SSR the first request, cache result
  };
}

// getServerSideProps — runs on SERVER per request, result passed as props
// Use for: personalized pages, real-time data, auth-gated content
export async function getServerSideProps(context) {
  const { req, res, params, query } = context;
  const session = await getSession(req);

  if (!session) {
    return { redirect: { destination: '/login', permanent: false } };
  }

  const user = await fetchUser(session.userId);
  return { props: { user } };
}

// Page component receives the props from either function
export default function Page({ post }) {
  return <article>{post.content}</article>;
}
```

**`getStaticProps` vs `getServerSideProps`:**

| | `getStaticProps` | `getServerSideProps` |
|---|---|---|
| Runs | Build time (+ ISR) | Every request |
| Speed | Fast — served from CDN | Slower — server round-trip |
| Data freshness | Stale until revalidated | Always fresh |
| Access to `req`/`res` | No | Yes |
| Use for | Blogs, docs, marketing | Dashboards, user-specific, real-time |

---

## 18c. Dynamic Routing

### Pages Router

```
pages/
├── blog/
│   ├── index.tsx         → /blog
│   ├── [slug].tsx        → /blog/my-post (single segment)
│   ├── [...slug].tsx     → /blog/a/b/c  (catch-all, requires segment)
│   └── [[...slug]].tsx   → /blog  AND  /blog/a/b/c (optional catch-all)
└── api/
    └── users/
        └── [id].ts       → /api/users/123
```

```tsx
// [slug].tsx — params.slug is a string
export default function Post({ params }) {
  // params.slug = 'my-post'
}

// [...slug].tsx — params.slug is an array, path must have at least one segment
export default function Doc({ params }) {
  // /docs/a/b/c → params.slug = ['a', 'b', 'c']
  // /docs → 404
}

// [[...slug]].tsx — optional catch-all, path can be empty
export default function Page({ params }) {
  // /blog       → params.slug = undefined
  // /blog/a/b   → params.slug = ['a', 'b']
}
```

### App Router

```
app/
├── blog/
│   ├── page.tsx               → /blog
│   ├── [slug]/
│   │   └── page.tsx           → /blog/my-post
│   ├── [...slug]/
│   │   └── page.tsx           → /blog/a/b/c
│   └── [[...slug]]/
│       └── page.tsx           → /blog  AND  /blog/a/b/c
└── (group)/
    └── dashboard/
        └── page.tsx           → /dashboard (route group — no URL segment)
```

```tsx
// [slug]/page.tsx
export default function PostPage({ params }: { params: { slug: string } }) {
  return <Post slug={params.slug} />;
}

// [...slug]/page.tsx
export default function DocsPage({ params }: { params: { slug: string[] } }) {
  return <Docs path={params.slug.join('/')} />;
}
```

---

## 18d. `next.config.js`

`next.config.js` (or `next.config.ts`) configures the Next.js build and runtime. It runs in Node.js — no browser APIs.

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Strict mode — enables React StrictMode
  reactStrictMode: true,

  // Output — 'standalone' bundles only required files for deployment
  output: 'standalone',

  // Environment variables — exposed to the browser (prefix with NEXT_PUBLIC_)
  // Better: use process.env directly; configure in .env files
  env: {
    APP_VERSION: process.env.npm_package_version,
  },

  // Images — whitelist external domains for next/image
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.example.com', pathname: '/images/**' },
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Redirects — server-side, permanent or temporary
  async redirects() {
    return [
      { source: '/old-path', destination: '/new-path', permanent: true },
    ];
  },

  // Rewrites — proxy without redirect (URL stays the same)
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'https://api.example.com/:path*' },
    ];
  },

  // Headers — add custom response headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
        ],
      },
    ];
  },

  // Webpack customization — extend the default config
  webpack(config, { isServer }) {
    if (!isServer) {
      config.resolve.fallback = { fs: false }; // prevent Node modules in client bundle
    }
    return config;
  },

  // Experimental features
  experimental: {
    ppr: true,               // Partial Pre-Rendering (Next.js 14+)
    serverActions: { bodySizeLimit: '2mb' },
  },
};

module.exports = nextConfig;
```

---

## 19. Auth & Middleware

### `middleware.ts`

Middleware runs before a request is processed — on every matched request, before Server Components render. Ideal for auth, redirects, A/B testing, i18n routing.

```ts
// middleware.ts (root of project)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { verifyToken } from '@/lib/auth';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes — skip auth
  const publicPaths = ['/login', '/register', '/api/auth'];
  if (publicPaths.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const token = request.cookies.get('token')?.value;
  if (!token) {
    return NextResponse.redirect(new URL(`/login?from=${pathname}`, request.url));
  }

  try {
    const payload = await verifyToken(token);
    // Forward user info to headers for Server Components
    const response = NextResponse.next();
    response.headers.set('x-user-id', payload.sub);
    return response;
  } catch {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

// Matcher — only run middleware on these paths
export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

### NextAuth.js (Auth.js)

```ts
// auth.ts
import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';
import Credentials from 'next-auth/providers/credentials';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    GitHub,
    Credentials({
      credentials: { email: {}, password: {} },
      async authorize(credentials) {
        const user = await verifyCredentials(credentials);
        return user ?? null;
      },
    }),
  ],
  callbacks: {
    jwt({ token, user }) {
      if (user) token.role = user.role;
      return token;
    },
    session({ session, token }) {
      session.user.role = token.role;
      return session;
    },
  },
});

// app/api/auth/[...nextauth]/route.ts
export const { GET, POST } = handlers;

// Server Component — get session
const session = await auth();
if (!session) redirect('/login');

// Client Component
import { useSession } from 'next-auth/react';
const { data: session, status } = useSession();
```

### Role-Based Access Control (RBAC)

```tsx
// Higher-order Server Component for protected pages
async function requireRole(role: string, children: React.ReactNode) {
  const session = await auth();
  if (!session) redirect('/login');
  if (session.user.role !== role) redirect('/unauthorized');
  return children;
}

// Page
export default async function AdminPage() {
  return requireRole('admin', <AdminDashboard />);
}
```

---

# Part 1 (continued): React Core

---

## 20. React 19 Hooks & Compiler

### `use()` Hook

`use()` reads a resource — a Promise or a Context — during render. Unlike all other hooks, it can be called **conditionally**.

```tsx
import { use, Suspense } from 'react';

// use() with a Promise — suspends until resolved
// The promise must be created outside the component (stable reference)
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // suspends at this line
  return <h1>{user.name}</h1>;
}

// Parent creates the promise without awaiting it
async function Page({ params }: { params: { id: string } }) {
  const userPromise = fetchUser(params.id); // NOT awaited
  return (
    <Suspense fallback={<Skeleton />}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  );
}

// use() with Context — same as useContext but works inside conditionals
function Button({ showLabel }: { showLabel: boolean }) {
  if (!showLabel) return <button aria-label="icon" />;
  const theme = use(ThemeContext); // OK inside a conditional branch
  return <button className={theme.button}>Click</button>;
}
```

### `useActionState`

Replaces `useFormState` (React 18 / react-dom). Now imported from `'react'` directly. The third return value is `isPending`.

```tsx
'use client';
import { useActionState } from 'react'; // NOT from react-dom

type State = { error: string | null; success: boolean };
const initial: State = { error: null, success: false };

function CreateUserForm() {
  const [state, formAction, isPending] = useActionState(createUser, initial);

  return (
    <form action={formAction}>
      <input name="name" required disabled={isPending} />
      <input name="email" type="email" required disabled={isPending} />
      {state.error && <p role="alert">{state.error}</p>}
      {state.success && <p>User created!</p>}
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  );
}

// Server Action receives prevState as first argument
'use server';
export async function createUser(prevState: State, formData: FormData): Promise<State> {
  const name = formData.get('name') as string;
  try {
    await db.users.create({ data: { name, email: formData.get('email') as string } });
    return { error: null, success: true };
  } catch {
    return { error: 'Failed to create user', success: false };
  }
}
```

### React Compiler (React Forget)

The React Compiler ships as an opt-in in React 19. It statically analyzes components and automatically inserts `useMemo`, `useCallback`, and `React.memo` where beneficial — so you don't have to.

```bash
# Next.js — enable in next.config.js
experimental: { reactCompiler: true }

# Other setups
npm install babel-plugin-react-compiler
```

```tsx
// Before compiler — manual memoization
const MemoizedList = React.memo(function List({ items }: { items: Item[] }) {
  return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
});

function Parent({ items, query }: Props) {
  const filtered = useMemo(() => items.filter(i => i.name.includes(query)), [items, query]);
  const handleClick = useCallback((id: string) => console.log(id), []);
  return <MemoizedList items={filtered} onClick={handleClick} />;
}

// After compiler — write natural React, compiler handles it
function Parent({ items, query }: Props) {
  const filtered = items.filter(i => i.name.includes(query)); // compiler memoizes
  return <List items={filtered} onClick={(id) => console.log(id)} />; // and this
}
```

**Requirement:** Code must follow the Rules of React (pure render functions, no mutation during render). The compiler skips any component it can't safely analyze.

---

## 21. React Fiber

Fiber is the reconciliation engine introduced in React 16. It replaced the synchronous recursive stack reconciler with an **incremental, interruptible work loop**.

### Two-Phase Architecture

```
Render Phase (interruptible — can be paused, resumed, or discarded)
  beginWork  → process each fiber node top-down
  completeWork → collect side effects bottom-up
         ↓
Commit Phase (synchronous — cannot be interrupted)
  before-mutation → getSnapshotBeforeUpdate
  mutation        → apply DOM additions/deletions/updates
  layout          → useLayoutEffect / componentDidMount
         ↓
  (browser paints)
         ↓
  passive effects → useEffect runs asynchronously
```

### Fiber Nodes

Each React element becomes a **Fiber node** — a JS object that forms a linked tree:

```ts
interface FiberNode {
  type: string | Function;     // 'div' or the component function
  key: string | null;
  child: FiberNode | null;     // first child
  sibling: FiberNode | null;   // next sibling
  return: FiberNode | null;    // parent (not "parent" to avoid confusion with DOM)
  alternate: FiberNode | null; // double buffer — previous committed tree

  pendingProps: object;
  memoizedProps: object;
  memoizedState: Hook | null;  // linked list of hook states

  lanes: Lanes;                // priority bitmask for this update
  flags: Flags;                // side effects (Placement, Update, Deletion...)
}
```

React maintains **two trees** — the **current tree** (on screen) and the **work-in-progress tree** (being built). After commit they swap. This is double buffering — it means React can discard in-progress work without touching the live UI.

### Priority Lanes

React 18 concurrent features use a bitmask of **priority lanes**:

```
SyncLane             — synchronous, highest priority (legacy mode)
InputContinuousLane  — pointer events, scroll
DefaultLane          — setState not wrapped in anything
TransitionLane       — startTransition() updates
IdleLane             — lowest priority background work
```

```tsx
// startTransition — marks the update as TransitionLane
// React can interrupt it if a higher-priority update arrives (e.g. user typing)
const [isPending, startTransition] = useTransition();

function handleSearch(e: React.ChangeEvent<HTMLInputElement>) {
  setQuery(e.target.value);           // SyncLane — updates input immediately
  startTransition(() => {
    setResults(expensiveSearch(e.target.value)); // TransitionLane — interruptible
  });
}
```

### Time Slicing

Fiber breaks render work into small units and **yields to the browser** between them using the Scheduler package (backed by `MessageChannel`). This prevents a 200ms render from blocking user interactions.

**What Fiber enables:**
| Feature | How Fiber makes it possible |
|---|---|
| Concurrent rendering | Render phase is interruptible — multiple updates in-flight |
| `startTransition` | Low-priority updates run in TransitionLane, preempted by input |
| Suspense | A component can "throw" a Promise to pause render and retry later |
| Error boundaries | Errors are caught per-tree segment without unmounting the root |
| `useEffect` timing | Passive effects run after paint, not synchronously like layout effects |

---

## 22. Portals

`createPortal(children, domNode)` renders children into a **different DOM node** while keeping them in the **same React tree**. Context works across portals; events bubble through the React tree, not the DOM tree.

```tsx
import { createPortal } from 'react-dom';
import { useEffect, useRef } from 'react';

// Modal — escapes overflow:hidden and z-index stacking contexts
function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null;

  return createPortal(
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button onClick={onClose} aria-label="Close">×</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>,
    document.body
  );
}

// Portal children can still consume context from anywhere above in the React tree
function Page() {
  const [open, setOpen] = useState(false);
  return (
    <ThemeContext.Provider value="dark">
      <button onClick={() => setOpen(true)}>Open</button>
      <Modal isOpen={open} onClose={() => setOpen(false)} title="Edit Profile">
        {/* ProfileForm can useContext(ThemeContext) even though it's in document.body */}
        <ProfileForm />
      </Modal>
    </ThemeContext.Provider>
  );
}

// Hook that creates/cleans up a portal mount node
function usePortal(id = 'portal-root') {
  const [mountNode, setMountNode] = useState<HTMLElement | null>(null);

  useLayoutEffect(() => {
    let el = document.getElementById(id);
    const created = !el;
    if (created) {
      el = document.createElement('div');
      el.id = id;
      document.body.appendChild(el);
    }
    setMountNode(el);
    return () => { if (created && el?.childNodes.length === 0) el.remove(); };
  }, [id]);

  return mountNode;
}

// Tooltip using the portal hook
function Tooltip({ children, content, visible }: TooltipProps) {
  const portal = usePortal('tooltip-root');
  return (
    <>
      {children}
      {visible && portal && createPortal(
        <div className="tooltip">{content}</div>,
        portal
      )}
    </>
  );
}
```

**Key rules:**
- Events bubble through the **React component** tree — a click inside a portal modal bubbles to React ancestors, not DOM ancestors
- Context is inherited from the component's position in the **React tree**, not the DOM
- Portals are the standard solution for escaping `overflow: hidden`, `transform`, and `z-index` stacking contexts — common for modals, tooltips, dropdowns, and toasts

---

## 23. Forms

### React Hook Form

RHF registers inputs as uncontrolled by default — the form only re-renders on submit and when error/touched state changes (not on every keystroke).

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email'),
  age: z.coerce.number().min(18, 'Must be 18+'),
});
type FormData = z.infer<typeof schema>;

function ProfileForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', email: '', age: 18 },
  });

  const onSubmit = async (data: FormData) => {
    await saveProfile(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input {...register('name')} placeholder="Name" />
        {errors.name && <span role="alert">{errors.name.message}</span>}
      </div>
      <div>
        <input {...register('email')} type="email" />
        {errors.email && <span role="alert">{errors.email.message}</span>}
      </div>
      <div>
        <input {...register('age')} type="number" />
        {errors.age && <span role="alert">{errors.age.message}</span>}
      </div>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}
```

### Controlled Third-Party Inputs with `Controller`

```tsx
import { Controller } from 'react-hook-form';
import Select from 'react-select';

function TagForm() {
  const { control, handleSubmit } = useForm<{ tags: string[] }>();

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <Controller
        name="tags"
        control={control}
        rules={{ required: 'Select at least one tag' }}
        render={({ field, fieldState }) => (
          <>
            <Select
              isMulti
              options={tagOptions}
              value={tagOptions.filter(o => field.value?.includes(o.value))}
              onChange={selected => field.onChange(selected.map(s => s.value))}
              onBlur={field.onBlur}
            />
            {fieldState.error && <span role="alert">{fieldState.error.message}</span>}
          </>
        )}
      />
    </form>
  );
}
```

### Dynamic Field Arrays with `useFieldArray`

```tsx
import { useFieldArray } from 'react-hook-form';

function InvoiceForm() {
  const { control, register, handleSubmit, watch } = useForm({
    defaultValues: { items: [{ description: '', qty: 1, price: 0 }] },
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'items' });

  const items = watch('items');
  const total = items.reduce((sum, item) => sum + item.qty * item.price, 0);

  return (
    <form onSubmit={handleSubmit(console.log)}>
      {fields.map((field, i) => (
        <div key={field.id}> {/* always use field.id as key, not index */}
          <input {...register(`items.${i}.description`)} placeholder="Description" />
          <input {...register(`items.${i}.qty`, { valueAsNumber: true })} type="number" min={1} />
          <input {...register(`items.${i}.price`, { valueAsNumber: true })} type="number" step="0.01" />
          {fields.length > 1 && (
            <button type="button" onClick={() => remove(i)}>Remove</button>
          )}
        </div>
      ))}
      <button type="button" onClick={() => append({ description: '', qty: 1, price: 0 })}>
        Add item
      </button>
      <p>Total: ${total.toFixed(2)}</p>
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Multi-Step Forms

```tsx
import { FormProvider, useForm, useFormContext } from 'react-hook-form';

type WizardData = {
  personal: { name: string; email: string };
  plan: { tier: 'free' | 'pro' };
};

function Step1() {
  const { register, formState: { errors } } = useFormContext<WizardData>();
  return (
    <>
      <input {...register('personal.name', { required: true })} placeholder="Name" />
      <input {...register('personal.email', { required: true })} placeholder="Email" />
    </>
  );
}

function Step2() {
  const { register } = useFormContext<WizardData>();
  return (
    <fieldset>
      <label><input {...register('plan.tier')} type="radio" value="free" /> Free</label>
      <label><input {...register('plan.tier')} type="radio" value="pro" /> Pro</label>
    </fieldset>
  );
}

function Wizard() {
  const [step, setStep] = useState(1);
  const methods = useForm<WizardData>({ mode: 'onBlur' });

  // handleSubmit validates only the current step's fields
  const next = methods.handleSubmit(() => setStep(s => s + 1));
  const submit = methods.handleSubmit(data => saveSignup(data));

  return (
    <FormProvider {...methods}>
      <form>
        {step === 1 && <Step1 />}
        {step === 2 && <Step2 />}
        <div>
          {step > 1 && <button type="button" onClick={() => setStep(s => s - 1)}>Back</button>}
          {step < 2 && <button type="button" onClick={next}>Next</button>}
          {step === 2 && <button type="button" onClick={submit}>Submit</button>}
        </div>
      </form>
    </FormProvider>
  );
}
```

---

## 24. TanStack Query

TanStack Query manages **server state** — caching, background refetching, deduplication, stale-while-revalidate — things you'd otherwise build manually.

```tsx
// Setup — configure defaults once
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // data is fresh for 5 minutes
      gcTime: 10 * 60 * 1000,    // cache kept for 10 min after last subscriber leaves
      retry: 2,
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

```tsx
// useQuery — fetch, cache, and subscribe to data
import { useQuery } from '@tanstack/react-query';

function UsersList() {
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],              // cache key — use arrays for namespacing
    queryFn: () => fetch('/api/users').then(r => {
      if (!r.ok) throw new Error('Network error');
      return r.json();
    }),
    select: data => data.filter((u: User) => u.active), // transform before returning
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <ul>{users?.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

// Parameterized query — refetches when userId changes
function UserDetail({ userId }: { userId: number }) {
  const { data: user } = useQuery({
    queryKey: ['users', userId],     // different key = separate cache entry
    queryFn: () => fetchUser(userId),
    enabled: !!userId,               // skip query when userId is falsy
  });
  return <div>{user?.name}</div>;
}
```

```tsx
// useMutation — mutations with cache invalidation
import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreateUserForm() {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: (newUser: NewUser) =>
      fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      }).then(r => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] }); // refetch list
      toast.success('User created');
    },
    onError: err => toast.error(err.message),
  });

  return (
    <button onClick={() => mutate({ name: 'Alice', email: 'alice@example.com' })} disabled={isPending}>
      {isPending ? 'Creating...' : 'Create User'}
    </button>
  );
}

// Optimistic updates — update UI before server responds, rollback on error
const { mutate: updateUser } = useMutation({
  mutationFn: (user: User) => fetch(`/api/users/${user.id}`, { method: 'PATCH', body: JSON.stringify(user) }),
  onMutate: async (updatedUser) => {
    await queryClient.cancelQueries({ queryKey: ['users', updatedUser.id] });
    const previous = queryClient.getQueryData<User>(['users', updatedUser.id]);
    queryClient.setQueryData(['users', updatedUser.id], updatedUser); // optimistic
    return { previous };
  },
  onError: (_err, updatedUser, context) => {
    queryClient.setQueryData(['users', updatedUser.id], context?.previous); // rollback
  },
  onSettled: (_data, _err, updatedUser) => {
    queryClient.invalidateQueries({ queryKey: ['users', updatedUser.id] }); // sync
  },
});
```

```tsx
// Prefetching on hover — data ready before navigation
const queryClient = useQueryClient();

<Link
  href={`/users/${id}`}
  onMouseEnter={() =>
    queryClient.prefetchQuery({
      queryKey: ['users', id],
      queryFn: () => fetchUser(id),
    })
  }
>
  View profile
</Link>
```

**Mental model:**
- `useState`/`useReducer` — **client state** (UI toggles, form values, local ephemeral state)
- TanStack Query — **server state** (data from APIs that lives on the server, needs sync)

TanStack Query handles stale-while-revalidate, deduplication (multiple components calling the same query get one fetch), background refetch on focus/reconnect, and pagination — all of which you'd otherwise build by hand.

---

## 25. Zustand

Zustand is a minimal global state library with no providers, no reducers, and no action types.

```tsx
import { create } from 'zustand';

// Basic store
interface CounterStore {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set(state => ({ count: state.count + 1 })),
  decrement: () => set(state => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));

// Each component subscribes to only what it reads — no unnecessary re-renders
function CountDisplay() {
  const count = useCounterStore(state => state.count); // only re-renders when count changes
  return <span>{count}</span>;
}

function Controls() {
  const increment = useCounterStore(state => state.increment); // stable reference, never re-renders
  const decrement = useCounterStore(state => state.decrement);
  return (
    <>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </>
  );
}
```

```tsx
// Async actions — use set directly, no thunk middleware needed
interface UserStore {
  users: User[];
  loading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
  getUserById: (id: number) => User | undefined;
}

const useUserStore = create<UserStore>((set, get) => ({
  users: [],
  loading: false,
  error: null,

  fetchUsers: async () => {
    set({ loading: true, error: null });
    try {
      const users = await fetch('/api/users').then(r => r.json());
      set({ users, loading: false });
    } catch (err: unknown) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  getUserById: (id) => get().users.find(u => u.id === id), // get() reads current state
}));
```

```tsx
// Slice pattern — compose multiple feature slices into one store
type BearSlice = { bears: number; addBear: () => void };
type FishSlice = { fish: number; addFish: () => void };

const createBearSlice = (set: any): BearSlice => ({
  bears: 0,
  addBear: () => set((s: any) => ({ bears: s.bears + 1 })),
});

const createFishSlice = (set: any): FishSlice => ({
  fish: 0,
  addFish: () => set((s: any) => ({ fish: s.fish + 1 })),
});

const useBoundStore = create<BearSlice & FishSlice>()((...a) => ({
  ...createBearSlice(...a),
  ...createFishSlice(...a),
}));

// Middleware — persist to localStorage, DevTools integration
import { persist, devtools } from 'zustand/middleware';

const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        token: null,
        setUser: (user) => set({ user }),
        logout: () => set({ user: null, token: null }),
      }),
      {
        name: 'auth-store',
        partialize: state => ({ user: state.user }), // only persist user, not token
      }
    )
  )
);
```

```tsx
// Prevent unnecessary re-renders when subscribing to multiple fields
import { useShallow } from 'zustand/react/shallow';

const { name, email } = useAuthStore(
  useShallow(state => ({ name: state.user?.name, email: state.user?.email }))
);
// Without useShallow, this would re-render on any store change — even unrelated fields
```

**Zustand vs Context + useReducer:**
- No `Provider` needed — components access the store directly
- Selectors + `useShallow` avoid the context re-render problem without splitting contexts
- Async actions are plain `async` functions — no middleware like Redux Thunk
- DevTools middleware connects to Redux DevTools with zero extra setup

---

# Part 2 (continued): Next.js

---

## 26. Metadata API

The App Router manages `<head>` through the Metadata API. It replaces `next/head` from the Pages Router and supports static exports, dynamic generation, and title templates.

```tsx
// Static metadata — export from any page.tsx or layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Product Catalog',
  description: 'Browse our full catalog of products',

  openGraph: {
    title: 'Product Catalog',
    description: 'Browse our full catalog',
    url: 'https://myshop.com/products',
    siteName: 'My Shop',
    images: [{ url: 'https://myshop.com/og/products.png', width: 1200, height: 630 }],
    type: 'website',
  },

  twitter: { card: 'summary_large_image', images: ['https://myshop.com/og/products.png'] },

  robots: { index: true, follow: true },
  alternates: { canonical: 'https://myshop.com/products' },
};
```

```tsx
// Dynamic metadata — for data-driven pages
import type { Metadata, ResolvingMetadata } from 'next';

interface Props { params: { slug: string } }

export async function generateMetadata(
  { params }: Props,
  parent: ResolvingMetadata  // access parent layout's metadata
): Promise<Metadata> {
  // generateMetadata and the Page component fetch in parallel — no waterfall
  const product = await fetchProduct(params.slug);
  const parentOg = (await parent).openGraph;

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      ...parentOg,            // inherit parent OG fields
      title: product.name,
      images: [{ url: product.imageUrl }],
    },
  };
}

export default async function ProductPage({ params }: Props) {
  const product = await fetchProduct(params.slug);
  return <ProductDetail product={product} />;
}
```

```tsx
// Title templates — define once in layout, pages extend automatically
// app/layout.tsx
export const metadata: Metadata = {
  title: {
    default: 'My Shop',          // used when a child page doesn't set a title
    template: '%s | My Shop',    // child sets title: 'Cart' → 'Cart | My Shop'
  },
};

// app/cart/page.tsx
export const metadata: Metadata = {
  title: 'Cart',               // rendered as 'Cart | My Shop'
};

// app/landing/page.tsx
export const metadata: Metadata = {
  title: { absolute: 'Summer Sale 2026' }, // ignores template entirely
};
```

```tsx
// Dynamic OG images — generated at request time with next/og
// app/og/route.tsx
import { ImageResponse } from 'next/og';

export async function GET(request: Request) {
  const title = new URL(request.url).searchParams.get('title') ?? 'My Shop';

  return new ImageResponse(
    <div style={{ display: 'flex', width: '100%', height: '100%', background: '#0f172a', padding: 60 }}>
      <h1 style={{ color: '#f8fafc', fontSize: 64, fontWeight: 700 }}>{title}</h1>
    </div>,
    { width: 1200, height: 630 }
  );
}

// Reference from page metadata
export const metadata: Metadata = {
  openGraph: {
    images: [{ url: `/og?title=${encodeURIComponent('My Product')}` }],
  },
};
```

**Key rules:**
- `generateMetadata` and the page component run **in parallel** — don't duplicate fetches; use `React.cache` to deduplicate them
- Metadata is **deep-merged** through the layout tree — child metadata overrides parent fields, but unset fields inherit
- `"use client"` components cannot export metadata — metadata APIs are server-only

---

## 27. Streaming with Suspense

Next.js streams HTML progressively — the server sends the static shell immediately, then flushes each `<Suspense>` boundary as its data resolves.

### How It Works

```
Browser receives bytes over time:
─────────────────────────────────────────────────────────>

0ms    → <html><body><nav>...</nav>
           <div id="main">
             <!--$?--><template id="B:0"></template><!--/$-->  ← placeholder
           </div>

~100ms → <div hidden id="S:0"><ProductList .../></div>
          <script>$RC("B:0","S:0")</script>  ← swap placeholder with real content
```

Each `<Suspense>` boundary is a **flush point** — the server sends the resolved content and a script to swap it in.

```tsx
// app/products/page.tsx — multiple independent boundaries
import { Suspense } from 'react';

export default function ProductsPage() {
  return (
    <div>
      <h1>Products</h1>       {/* static — sent immediately */}
      <SearchBar />            {/* static — sent immediately */}

      <Suspense fallback={<ProductsSkeleton />}>
        <ProductList />        {/* async Server Component — streams when DB query resolves */}
      </Suspense>

      <Suspense fallback={<RecommendationsSkeleton />}>
        <Recommendations />    {/* independent — doesn't wait for ProductList */}
      </Suspense>
    </div>
  );
}

async function ProductList() {
  const products = await db.products.findMany(); // suspends here
  return <ul>{products.map(p => <ProductItem key={p.id} product={p} />)}</ul>;
}
```

### `loading.tsx` — Automatic Suspense

```tsx
// app/dashboard/loading.tsx — Next.js wraps the page in <Suspense> automatically
export default function Loading() {
  return <DashboardSkeleton />;
}
// Equivalent to: <Suspense fallback={<DashboardSkeleton />}><DashboardPage /></Suspense>
```

### Fine-Grained Streaming with `use()`

Start all fetches simultaneously without awaiting, then let each Suspense boundary stream independently:

```tsx
// Pass unawaited promises down — each component suspends when it calls use()
export default async function DashboardPage({ params }: { params: { id: string } }) {
  // All requests start in parallel — none awaited at the top
  const statsPromise = fetchStats(params.id);
  const activityPromise = fetchActivity(params.id);
  const usersPromise = fetchUsers(params.id);

  return (
    <div>
      <Suspense fallback={<StatsSkeleton />}>
        <StatsWidget data={statsPromise} />
      </Suspense>
      <Suspense fallback={<ActivitySkeleton />}>
        <ActivityFeed data={activityPromise} />
      </Suspense>
      <Suspense fallback={<UsersSkeleton />}>
        <UserTable data={usersPromise} />
      </Suspense>
    </div>
  );
}

function StatsWidget({ data }: { data: Promise<Stats> }) {
  const stats = use(data); // suspends until promise resolves
  return <StatsGrid stats={stats} />;
}
```

### Avoiding Waterfalls

```tsx
// BAD — sequential awaits: total time = sum of all fetch times
async function SlowPage() {
  const user = await fetchUser();    // 100ms
  const posts = await fetchPosts();  // 100ms — starts AFTER user
  const stats = await fetchStats();  // 100ms — starts AFTER posts
  // 300ms total before anything is sent to browser
  return <>{/* render */}</>;
}

// GOOD — parallel start + streaming: total time ≈ slowest single fetch
async function FastPage() {
  const userPromise  = fetchUser();  // all start immediately in parallel
  const postsPromise = fetchPosts();
  const statsPromise = fetchStats();

  return (
    <>
      <Suspense fallback={<UserSkeleton />}>
        <UserProfile data={userPromise} />   {/* shows at ~100ms */}
      </Suspense>
      <Suspense fallback={<PostsSkeleton />}>
        <PostsList data={postsPromise} />     {/* shows at ~100ms */}
      </Suspense>
    </>
  );
}
```

**`React.cache` for deduplication** — when a Server Component and `generateMetadata` both fetch the same data, wrap the fetch in `cache()` so the DB is only hit once:

```tsx
import { cache } from 'react';

export const fetchProduct = cache(async (slug: string) => {
  return db.products.findUnique({ where: { slug } });
});
// Called in generateMetadata AND in the page component → one DB query
```

---

*Last updated: 2026-06-04*
