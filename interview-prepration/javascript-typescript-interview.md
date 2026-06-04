# JavaScript & TypeScript Interview Reference

A senior-focused reference covering core concepts with code examples. Organized from foundational to advanced.

---

## Table of Contents

### Part 1: JavaScript

1. [Core Language Fundamentals](#1-core-language-fundamentals)
2. [Functions](#2-functions)
3. [Prototypes & Objects](#3-prototypes--objects)
4. [Asynchronous JavaScript](#4-asynchronous-javascript)
5. [ES6+ Features](#5-es6-features)
6. [Memory & Performance](#6-memory--performance)
7. [Modules](#7-modules)
8. [Browser & Node.js Runtime](#8-browser--nodejs-runtime)
9. [Error Handling](#9-error-handling)
15. [Async Iteration](#15-async-iteration)
16. [Array Methods Deep Dive](#16-array-methods-deep-dive)
17. [Object Static Methods](#17-object-static-methods)
18. [AggregateError](#18-aggregateerror)
19. [Intl API](#19-intl-api)

### Part 2: TypeScript

10. [Type System Fundamentals](#10-type-system-fundamentals)
11. [Advanced Types](#11-advanced-types)
12. [TypeScript in Practice](#12-typescript-in-practice)
13. [Decorators in TypeScript](#13-decorators-in-typescript)
14. [TypeScript Configuration](#14-typescript-configuration)
20. [satisfies Operator](#20-satisfies-operator)
21. [Explicit Resource Management (using)](#21-explicit-resource-management-using)
22. [const Type Parameters](#22-const-type-parameters)

---

# Part 1: JavaScript

---

## 1. Core Language Fundamentals

### Variables: `var` / `let` / `const`, Hoisting, TDZ

`var` is function-scoped and hoisted to the top of its function with an initial value of `undefined`. `let` and `const` are block-scoped and hoisted but not initialized — accessing them before their declaration throws a `ReferenceError`. This uninitialized state is called the **Temporal Dead Zone (TDZ)**.

```js
console.log(a); // undefined (hoisted)
var a = 1;

console.log(b); // ReferenceError: Cannot access 'b' before initialization
let b = 2;
```

`const` requires an initializer and cannot be reassigned, but the value it points to can still be mutated if it's an object or array.

```js
const obj = { x: 1 };
obj.x = 2; // fine — mutating the object
obj = {}; // TypeError — reassigning the binding
```

**Key distinction:** `var` in a loop shares the same binding across iterations; `let` creates a new binding per iteration.

```js
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0); // prints 3, 3, 3
}

for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0); // prints 0, 1, 2
}
```

---

### Data Types, Type Coercion, `==` vs `===`

JavaScript has 8 data types: `undefined`, `null`, `boolean`, `number`, `bigint`, `string`, `symbol`, and `object`. Everything that isn't a primitive is an object (including functions and arrays).

**Type coercion** is implicit type conversion. `==` triggers it; `===` does not.

```js
0 == false; // true  — false coerces to 0
0 === false; // false — different types
'' == false; // true  — both coerce to 0
null == undefined; // true  — special case in spec
null === undefined; // false

typeof null; // 'object' — historic bug in JS
typeof []; // 'object'
Array.isArray([]); // true — use this instead
```

**`+` operator coercion trap:**

```js
1 + '2'; // '12' — number coerces to string
1 - '2'; // -1  — string coerces to number
```

### `null` vs `undefined`

Both represent the absence of a value, but they're distinct:

| | `null` | `undefined` |
|---|---|---|
| Meaning | Intentionally empty — developer set it | Not yet assigned — JS default |
| `typeof` | `'object'` (historic bug) | `'undefined'` |
| JSON | Serialized as `null` | Property omitted |
| Arithmetic | Coerces to `0` | Coerces to `NaN` |

```js
let a;          // undefined — declared but not assigned
let b = null;   // null — explicitly set to "no value"

typeof undefined; // 'undefined'
typeof null;      // 'object' — famous JS bug, never fixed for backwards compat

undefined + 1;    // NaN
null + 1;         // 1 — null coerces to 0

// Equality
null == undefined;  // true  — loose equality treats them as equal
null === undefined; // false — strict equality: different types

// Checking for either
if (value == null) { }    // catches both null and undefined (intentional loose ==)
if (value === null) { }   // only null
if (value === undefined) {} // only undefined
if (value != null) { }    // value is neither null nor undefined

// Optional chaining + nullish coalescing work with both
user?.address?.city ?? 'Unknown'; // short-circuits on null or undefined
```

---

### JavaScript Quirks & Coercion Edge Cases

These come up in interviews specifically because they're surprising. Understanding *why* they behave this way matters more than memorizing the output.

#### Floating-Point Arithmetic

```js
0.1 + 0.2;         // 0.30000000000000004 — NOT 0.3
0.1 + 0.2 === 0.3; // false
```

**Why:** JavaScript uses IEEE 754 double-precision floating-point. `0.1` and `0.2` can't be represented exactly in binary — they're repeating fractions, like `1/3` in decimal. The rounding errors accumulate.

```js
// Fix 1 — epsilon comparison
Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON; // true

// Fix 2 — toFixed (returns a string)
(0.1 + 0.2).toFixed(1); // '0.3'

// Fix 3 — integer math (scale up, compute, scale down)
(0.1 * 10 + 0.2 * 10) / 10; // 0.3
```

#### `+` Operator with Arrays and Objects

`+` does string concatenation if either operand becomes a string. Arrays and objects are coerced via `toString()`.

```js
[] + [];   // '' — [].toString() = '', '' + '' = ''
[] + {};   // '[object Object]' — {} coerces to '[object Object]'
{} + [];   // 0 — {} parsed as empty block (not object!), +[] coerces to 0
{} + {};   // NaN — {} as block, +{} → NaN

// Force expression context with parens:
({} + {}); // '[object Object][object Object]'
({} + []); // '[object Object]'
```

**Why `{} + []` is `0` at the statement level:** When `{}` is the *first token in a statement*, the parser treats it as an empty block, not an object literal. The expression becomes the unary `+[]`, which coerces the array: `[].toString()` → `''` → `+''` → `0`.

```js
// Array-to-number coercion via toString:
+[];      // 0   — [].toString() = ''   → +'' = 0
+[1];     // 1   — [1].toString() = '1' → +'1' = 1
+[1, 2];  // NaN — [1,2].toString() = '1,2' → +'1,2' = NaN
```

#### `NaN` Oddities

```js
typeof NaN;       // 'number' — NaN is a numeric value meaning "invalid number"
NaN === NaN;      // false — NaN is the only value not equal to itself
NaN !== NaN;      // true

// Safe NaN check:
Number.isNaN(NaN);      // true  — only true for actual NaN
Number.isNaN('hello');  // false — does not coerce
isNaN('hello');         // true  — coerces first, unreliable

// NaN propagates through all arithmetic:
1 + NaN; // NaN
NaN * 0; // NaN
```

#### Other Surprises

```js
// Loose equality edge cases
null == undefined;  // true  — special-cased in the spec
null == 0;          // false — null only equals undefined under ==
'' == false;        // true  — both coerce to 0
'0' == false;       // true  — '0' → 0, false → 0
[] == false;        // true  — [] → '' → 0, false → 0
[] == ![];          // true  — ![] is false ([] is truthy), then [] == false

// parseInt surprises
parseInt('1e2');     // 1   — stops at 'e'; use Number() for this
parseInt(0.0000005); // 5   — 0.0000005.toString() = '5e-7', parses '5'

// Array serialization
[1, 2, 3].toString(); // '1,2,3' — commas, no brackets
[1, [2, [3]]].join(); // '1,2,3' — recursively flattened in join
```

---

### Scope: Global, Function, Block

**Lexical scope** means that scope is determined at write time, not at call time. Inner functions can access outer variables, but not the reverse.

```js
const x = 'global';

function outer() {
  const x = 'outer';

  function inner() {
    const x = 'inner';
    console.log(x); // 'inner'
  }

  inner();
  console.log(x); // 'outer'
}

console.log(x); // 'global'
```

Block scope (`let`/`const`) creates a new scope for any `{}` block — `if`, `for`, `while`, etc.

---

### `this` Keyword — Binding Rules

`this` is determined at **call time**, not definition time (except for arrow functions, which capture `this` from their enclosing lexical scope).

There are 4 binding rules, in priority order:

1. **`new` binding** — `this` is the newly created object
2. **Explicit binding** — `call`, `apply`, `bind` set `this` explicitly
3. **Implicit binding** — the object to the left of the dot
4. **Default binding** — `globalThis` in non-strict mode, `undefined` in strict mode

```js
function greet() {
  console.log(this.name);
}

const user = { name: 'Alice', greet };
user.greet(); // 'Alice' — implicit binding

greet.call({ name: 'Bob' }); // 'Bob' — explicit binding

const bound = greet.bind({ name: 'Carol' });
bound(); // 'Carol' — explicit binding via bind

// Arrow function — captures enclosing this
const obj = {
  name: 'Dave',
  greet: () => console.log(this.name), // 'this' is enclosing scope, not obj
};
obj.greet(); // undefined (or global name)
```

**Class methods lose `this` when passed as callbacks** — bind or use arrow functions:

```js
class Timer {
  constructor() {
    this.count = 0;
  }

  // Arrow class field captures 'this' at construction time
  tick = () => {
    this.count++;
  };
}
```

### `call` vs `apply` vs `bind`

All three explicitly set `this`. The difference is when and how arguments are passed:

| Method | Invokes immediately | Arguments |
|---|---|---|
| `call(thisArg, arg1, arg2)` | Yes | Spread individually |
| `apply(thisArg, [arg1, arg2])` | Yes | As an array |
| `bind(thisArg, arg1, arg2)` | No — returns a new function | Pre-set (partial application) |

```js
function greet(greeting, punctuation) {
  return `${greeting}, ${this.name}${punctuation}`;
}

const user = { name: 'Alice' };

greet.call(user, 'Hello', '!');    // 'Hello, Alice!'
greet.apply(user, ['Hello', '!']); // 'Hello, Alice!' — args as array
const sayHi = greet.bind(user, 'Hi'); // returns new function, 'Hi' pre-set
sayHi('.');  // 'Hi, Alice.'
sayHi('?');  // 'Hi, Alice?'

// apply trick — spread array into variadic function (pre-spread syntax)
const nums = [3, 1, 4, 1, 5];
Math.max.apply(null, nums); // 5 — equivalent to Math.max(...nums)

// bind for callbacks that need correct `this`
class Button {
  constructor(label) { this.label = label; }
  handleClick() { console.log(this.label); }
}

const btn = new Button('Save');
document.addEventListener('click', btn.handleClick.bind(btn)); // 'this' is btn
```

---

## 2. Functions

### Declarations vs Expressions vs Arrow Functions

**Function declarations** are hoisted in full — both the name and the body. **Function expressions** (including arrow functions) are not hoisted.

```js
hello(); // works — declaration is hoisted
function hello() {
  console.log('hello');
}

world(); // TypeError: world is not a function
var world = function () {
  console.log('world');
};
```

**Arrow functions** differ from regular functions in three key ways:

- No own `this` (lexically bound)
- No `arguments` object
- Cannot be used as constructors (`new` throws)

```js
const add = (a, b) => a + b;

// No 'arguments' — use rest params instead
const sum = (...nums) => nums.reduce((a, b) => a + b, 0);
```

---

### Closures

A closure is a function that retains access to variables from its outer scope even after the outer function has returned. Closures are the mechanism behind module patterns, factory functions, and data encapsulation.

```js
function makeCounter(start = 0) {
  let count = start;

  return {
    increment: () => ++count,
    decrement: () => --count,
    value: () => count,
  };
}

const counter = makeCounter(10);
counter.increment(); // 11
counter.increment(); // 12
counter.value(); // 12
```

**Practical use — private state without classes:**

```js
function createStore(initialState) {
  let state = initialState;
  const listeners = [];

  return {
    getState: () => state,
    setState: (next) => {
      state = next;
      listeners.forEach((fn) => fn(state));
    },
    subscribe: (fn) => {
      listeners.push(fn);
      return () => listeners.splice(listeners.indexOf(fn), 1);
    },
  };
}
```

---

### IIFE (Immediately Invoked Function Expression)

An IIFE runs immediately after being defined. Used to create an isolated scope — common before ES modules.

```js
const result = (function () {
  const private = 'only here';
  return { public: private.toUpperCase() };
})();

console.log(result.public); // 'ONLY HERE'
console.log(private); // ReferenceError
```

---

### Higher-Order Functions

A higher-order function takes a function as an argument or returns a function. `map`, `filter`, `reduce` are the canonical examples.

```js
const users = [
  { name: 'Alice', age: 30, active: true },
  { name: 'Bob', age: 25, active: false },
  { name: 'Carol', age: 35, active: true },
];

const activeNames = users.filter((u) => u.active).map((u) => u.name);
// ['Alice', 'Carol']

const totalAge = users.reduce((sum, u) => sum + u.age, 0); // 90
```

---

### Currying & Partial Application

**Currying** transforms a function of `n` arguments into a chain of `n` single-argument functions.

**Partial application** fixes some arguments of a function, returning a new function that takes the rest.

```js
// Currying
const curry = (fn) => {
  const arity = fn.length;
  return function curried(...args) {
    if (args.length >= arity) return fn(...args);
    return (...more) => curried(...args, ...more);
  };
};

const add = curry((a, b, c) => a + b + c);
add(1)(2)(3); // 6
add(1, 2)(3); // 6
add(1)(2, 3); // 6

// Partial application
const multiply = (a, b) => a * b;
const double = multiply.bind(null, 2);
double(5); // 10

// Or with a helper
const partial =
  (fn, ...preset) =>
  (...rest) =>
    fn(...preset, ...rest);
const triple = partial(multiply, 3);
triple(7); // 21
```

**Where currying shines — composable pipelines:**

```js
const filter = curry((predicate, arr) => arr.filter(predicate));
const map = curry((transform, arr) => arr.map(transform));

const getActiveNames = (users) => [filter((u) => u.active), map((u) => u.name)].reduce((acc, fn) => fn(acc), users);
```

---

### Memoization

Memoization caches the result of a function call so repeated calls with the same arguments return the cached value without recomputation.

```js
function memoize(fn) {
  const cache = new Map();
  return function (...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

const fibonacci = memoize(function fib(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
});

fibonacci(40); // fast
```

**Caveats:**

- `JSON.stringify` fails for functions, circular refs, and `undefined` values — use a WeakMap for object args or a custom key serializer
- Unbounded caches grow indefinitely — add an LRU eviction strategy for long-running processes

```js
// WeakMap-based memoization for object arguments (allows GC)
function memoizeWeak(fn) {
  const cache = new WeakMap();
  return function (obj) {
    if (cache.has(obj)) return cache.get(obj);
    const result = fn.call(this, obj);
    cache.set(obj, result);
    return result;
  };
}
```

---

## 3. Prototypes & Objects

### Prototype Chain

Every object in JavaScript has an internal `[[Prototype]]` link to another object (or `null`). When you access a property, the engine walks this chain until it finds the property or reaches `null`.

```js
const animal = {
  breathe() {
    return 'breathing';
  },
};

const dog = Object.create(animal);
dog.bark = function () {
  return 'woof';
};

dog.bark(); // 'woof' — own property
dog.breathe(); // 'breathing' — found on prototype

Object.getPrototypeOf(dog) === animal; // true
```

---

### `Object.create`, `Object.assign`, Spread

```js
// Object.create — sets the prototype explicitly
const base = {
  greet() {
    return `Hi, I'm ${this.name}`;
  },
};
const instance = Object.create(base);
instance.name = 'Alice';
instance.greet(); // "Hi, I'm Alice"

// Object.assign — shallow copy / merge
const target = { a: 1 };
const result = Object.assign(target, { b: 2 }, { c: 3 });
// target and result are the same object: { a: 1, b: 2, c: 3 }

// Spread — also shallow, but creates a new object
const merged = { ...target, d: 4 };

// Shallow means nested objects are still referenced:
const original = { nested: { x: 1 } };
const copy = { ...original };
copy.nested.x = 99;
original.nested.x; // 99 — same reference
```

### Deep Copy vs Shallow Copy

**Shallow copy** — copies the top-level properties. Nested objects/arrays are still shared references.

**Deep copy** — recursively copies all nested values. No shared references.

```js
const original = {
  name: 'Alice',
  address: { city: 'Cairo', zip: '11511' },
  tags: ['admin', 'user'],
};

// --- Shallow copy methods ---

// Spread
const shallow1 = { ...original };

// Object.assign
const shallow2 = Object.assign({}, original);

// Verify: nested object is still shared
shallow1.address.city = 'Alex';
original.address.city; // 'Alex' — mutated the original

// --- Deep copy methods ---

// structuredClone (modern, built-in — Node 17+, all modern browsers)
const deep1 = structuredClone(original);
deep1.address.city = 'Giza';
original.address.city; // 'Cairo' — not affected

// structuredClone supports: objects, arrays, Date, Map, Set, RegExp, ArrayBuffer
// Does NOT support: functions, DOM nodes, class instances (methods are lost)

// JSON round-trip (simple but lossy)
const deep2 = JSON.parse(JSON.stringify(original));
// Loses: undefined values, functions, Date (becomes string), Map/Set, circular refs

// Recursive custom deep clone (handles edge cases you define)
function deepClone(value) {
  if (value === null || typeof value !== 'object') return value;
  if (value instanceof Date) return new Date(value);
  if (Array.isArray(value)) return value.map(deepClone);
  return Object.fromEntries(
    Object.entries(value).map(([k, v]) => [k, deepClone(v)])
  );
}
```

**Which to use:**
- `structuredClone` — default choice for deep copy
- Spread / `Object.assign` — fine for flat objects or when sharing nested refs is intentional
- JSON round-trip — avoid unless you know your data is JSON-safe

---

### ES6 Classes

Classes are syntactic sugar over the prototype system — no new object model, just cleaner syntax.

```js
class Animal {
  #name; // private field (ES2022)

  constructor(name) {
    this.#name = name;
  }

  speak() {
    return `${this.#name} makes a noise.`;
  }

  get name() {
    return this.#name;
  }

  static create(name) {
    return new Animal(name);
  }
}

class Dog extends Animal {
  constructor(name) {
    super(name);
  }

  speak() {
    return `${this.name} barks.`;
  }
}

const d = new Dog('Rex');
d.speak(); // 'Rex barks.'
d instanceof Dog; // true
d instanceof Animal; // true
```

**Under the hood:**

```js
Dog.prototype.__proto__ === Animal.prototype; // true
```

---

### Inheritance Patterns

**Prototypal delegation** (preferred in functional style):

```js
const canFly = {
  fly() {
    return `${this.name} is flying`;
  },
};

const canSwim = {
  swim() {
    return `${this.name} is swimming`;
  },
};

const duck = Object.assign(Object.create(canFly), canSwim, { name: 'Donald' });
duck.fly(); // 'Donald is flying'
duck.swim(); // 'Donald is swimming'
```

**Mixin pattern** (composition over inheritance):

```js
const Serializable = (superclass) =>
  class extends superclass {
    serialize() {
      return JSON.stringify(this);
    }
  };

const Validatable = (superclass) =>
  class extends superclass {
    validate() {
      return Object.keys(this).every((k) => this[k] != null);
    }
  };

class Base {}
class Model extends Serializable(Validatable(Base)) {}
```

---

## 4. Asynchronous JavaScript

### Event Loop, Call Stack, Task Queue, Microtask Queue

JavaScript is single-threaded. The event loop coordinates execution using:

- **Call stack** — executes synchronous code (LIFO)
- **Microtask queue** — Promise callbacks, `queueMicrotask` (drained completely after each task)
- **Macrotask queue** — `setTimeout`, `setInterval`, I/O callbacks (one per event loop tick)

**Priority: call stack → microtasks → macrotasks**

```js
console.log('1');

setTimeout(() => console.log('2'), 0); // macrotask

Promise.resolve().then(() => console.log('3')); // microtask

console.log('4');

// Output: 1, 4, 3, 2
```

**Why it matters:** microtasks can starve the event loop if they continuously queue new microtasks.

```js
// This blocks the event loop indefinitely:
function infinite() {
  Promise.resolve().then(infinite);
}
infinite();
```

---

### Callbacks and Callback Hell

```js
// Callback hell — pyramid of doom
getUser(id, (err, user) => {
  if (err) return handleError(err);
  getPosts(user.id, (err, posts) => {
    if (err) return handleError(err);
    getComments(posts[0].id, (err, comments) => {
      // ...
    });
  });
});
```

Problems: error handling must be done at every level, control flow is hard to follow, no built-in cancellation.

---

### Promises

A Promise represents an eventual value. It can be `pending`, `fulfilled`, or `rejected`.

```js
function fetchUser(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id > 0) resolve({ id, name: 'Alice' });
      else reject(new Error('Invalid ID'));
    }, 100);
  });
}

fetchUser(1)
  .then((user) => user.name)
  .then((name) => console.log(name)) // 'Alice'
  .catch((err) => console.error(err))
  .finally(() => console.log('done'));
```

**Chaining works because `.then` returns a new Promise.** Returning a value wraps it; returning a Promise flattens it.

```js
Promise.resolve(1)
  .then((x) => x + 1) // returns 2
  .then((x) => Promise.resolve(x * 10)) // returns Promise(20), flattened to 20
  .then(console.log); // 20
```

---

### `async`/`await`

`async`/`await` is syntactic sugar over Promises. An `async` function always returns a Promise.

```js
async function loadUserData(id) {
  try {
    const user = await fetchUser(id);
    const posts = await fetchPosts(user.id);
    return { user, posts };
  } catch (err) {
    console.error('Failed:', err.message);
    throw err;
  }
}
```

**Common mistake — sequential when parallel is possible:**

```js
// Sequential (slow — waits for each before starting next)
const user = await fetchUser(1);
const config = await fetchConfig();

// Parallel (fast — both requests in flight simultaneously)
const [user, config] = await Promise.all([fetchUser(1), fetchConfig()]);
```

---

### Promise Combinators

| Method               | Resolves when                  | Rejects when                 |
| -------------------- | ------------------------------ | ---------------------------- |
| `Promise.all`        | All resolve                    | Any rejects                  |
| `Promise.allSettled` | All settle (resolve or reject) | Never                        |
| `Promise.race`       | First settles                  | First settles with rejection |
| `Promise.any`        | First resolves                 | All reject                   |

```js
// Promise.allSettled — get results regardless of failure
const results = await Promise.allSettled([
  fetchUser(1),
  fetchUser(-1), // will reject
]);
results.forEach((r) => {
  if (r.status === 'fulfilled') console.log(r.value);
  else console.error(r.reason);
});

// Promise.any — first success wins
const fastest = await Promise.any([fetch('https://cdn1.example.com/data'), fetch('https://cdn2.example.com/data')]);
```

---

## 5. ES6+ Features

### Destructuring, Rest/Spread, Optional Chaining, Nullish Coalescing

```js
// Array destructuring
const [first, second, ...rest] = [1, 2, 3, 4, 5];

// Object destructuring with rename and default
const { name: userName = 'Guest', age = 0 } = user ?? {};

// Nested destructuring
const {
  address: { city },
} = user;

// Spread — shallow copy
const newArr = [...arr, newItem];
const newObj = { ...obj, overrideKey: newValue };

// Optional chaining — short-circuits to undefined, never throws
const city = user?.address?.city;
const first = arr?.[0];
const result = obj?.method?.();

// Nullish coalescing — only falls back on null/undefined (not 0, '', false)
const port = config.port ?? 3000;
const name = user.name ?? 'Anonymous';
```

---

### Iterators & Generators

An **iterator** is an object with a `next()` method returning `{ value, done }`. An **iterable** has a `[Symbol.iterator]()` method returning an iterator. `for...of`, spread, and destructuring all consume iterables.

```js
// Custom iterable
const range = {
  from: 1,
  to: 5,
  [Symbol.iterator]() {
    let current = this.from;
    const last = this.to;
    return {
      next() {
        if (current <= last) return { value: current++, done: false };
        return { value: undefined, done: true };
      },
    };
  },
};

[...range]; // [1, 2, 3, 4, 5]
```

A **generator function** (`function*`) returns a generator object that is both an iterator and an iterable. Execution pauses at each `yield`.

```js
function* range(start, end, step = 1) {
  for (let i = start; i <= end; i += step) {
    yield i;
  }
}

[...range(1, 10, 2)]; // [1, 3, 5, 7, 9]

// Infinite sequence — safe because lazy
function* naturals() {
  let n = 1;
  while (true) yield n++;
}

function take(n, iter) {
  const result = [];
  for (const val of iter) {
    result.push(val);
    if (result.length === n) break;
  }
  return result;
}

take(5, naturals()); // [1, 2, 3, 4, 5]
```

**`yield*` delegates to another iterable:**

```js
function* concat(...iterables) {
  for (const it of iterables) yield* it;
}

[...concat([1, 2], [3, 4], [5])]; // [1, 2, 3, 4, 5]
```

**Two-way communication — generators as coroutines:**

```js
function* calculator() {
  let result = 0;
  while (true) {
    const input = yield result;
    result += input;
  }
}

const gen = calculator();
gen.next(); // { value: 0, done: false } — start
gen.next(10); // { value: 10, done: false }
gen.next(20); // { value: 30, done: false }
```

---

### Symbol

A `Symbol` is a unique, immutable primitive. Two symbols with the same description are never equal.

```js
const id1 = Symbol('id');
const id2 = Symbol('id');
id1 === id2; // false — always unique

// Use case: non-colliding object keys
const ID = Symbol('id');
const obj = { [ID]: 123, name: 'Alice' };
obj[ID]; // 123 — accessible only with the symbol
Object.keys(obj); // ['name'] — symbols not enumerated
```

**Well-known symbols** let you customize built-in JavaScript behavior:

```js
class Collection {
  constructor(...items) {
    this.items = items;
  }

  // Make the class iterable
  [Symbol.iterator]() {
    return this.items[Symbol.iterator]();
  }

  // Customize instanceof behavior
  static [Symbol.hasInstance](instance) {
    return Array.isArray(instance?.items);
  }

  // Customize string coercion
  get [Symbol.toStringTag]() {
    return 'Collection';
  }
}

const c = new Collection(1, 2, 3);
[...c]; // [1, 2, 3]
Object.prototype.toString.call(c); // '[object Collection]'
```

---

### Proxy & Reflect

**Proxy** wraps an object and intercepts operations on it via **traps**. **Reflect** provides default implementations of those operations.

```js
const handler = {
  get(target, prop, receiver) {
    console.log(`GET ${prop}`);
    return Reflect.get(target, prop, receiver);
  },
  set(target, prop, value, receiver) {
    console.log(`SET ${prop} = ${value}`);
    return Reflect.set(target, prop, value, receiver);
  },
};

const obj = new Proxy({ x: 1 }, handler);
obj.x; // logs "GET x", returns 1
obj.y = 2; // logs "SET y = 2"
```

**Practical use — validation:**

```js
function createValidated(schema) {
  return new Proxy(
    {},
    {
      set(target, prop, value) {
        const validator = schema[prop];
        if (validator && !validator(value)) {
          throw new TypeError(`Invalid value for ${prop}: ${value}`);
        }
        return Reflect.set(target, prop, value);
      },
    },
  );
}

const user = createValidated({
  age: (v) => typeof v === 'number' && v >= 0,
});

user.age = 25; // ok
user.age = -1; // TypeError: Invalid value for age: -1
```

**Practical use — reactive/observable objects (Vue 3's reactivity model):**

```js
function reactive(target, onChange) {
  return new Proxy(target, {
    set(obj, prop, value) {
      const old = obj[prop];
      const result = Reflect.set(obj, prop, value);
      if (old !== value) onChange(prop, value, old);
      return result;
    },
  });
}

const state = reactive({ count: 0 }, (key, newVal) => {
  console.log(`${key} changed to ${newVal}`);
});

state.count++; // "count changed to 1"
```

**Key traps:**

| Trap             | Intercepts                |
| ---------------- | ------------------------- |
| `get`            | Property read             |
| `set`            | Property write            |
| `has`            | `in` operator             |
| `deleteProperty` | `delete` operator         |
| `apply`          | Function call             |
| `construct`      | `new` operator            |
| `ownKeys`        | `Object.keys`, `for...in` |

---

### WeakMap & WeakSet

`WeakMap` and `WeakSet` hold **weak references** — their entries don't prevent garbage collection of the key (WeakMap) or value (WeakSet).

```js
// WeakMap — private data per object instance, no memory leak
const _private = new WeakMap();

class Person {
  constructor(name, age) {
    _private.set(this, { age });
    this.name = name;
  }

  getAge() {
    return _private.get(this).age;
  }
}

// When a Person instance is GC'd, its _private entry is too.
```

**Difference from Map:** WeakMap keys must be objects, is not iterable, and has no `.size`. Use Map when you need iteration or primitive keys; use WeakMap when keys are objects and you don't want to prevent GC.

---

## 6. Memory & Performance

### Memory Lifecycle & Garbage Collection

JavaScript uses **mark-and-sweep** GC. The engine periodically marks all reachable objects from root references (global scope, call stack) and sweeps unreachable ones.

Modern engines (V8) use generational GC:

- **Young generation (nursery)** — short-lived objects, collected frequently
- **Old generation** — objects that survived multiple collections, collected less often

---

### Common Memory Leaks

**1. Forgotten event listeners:**

```js
// Leak — listener holds reference to element and closure
element.addEventListener('click', heavyHandler);

// Fix — remove when done
element.removeEventListener('click', heavyHandler);
// Or use AbortController:
const controller = new AbortController();
element.addEventListener('click', handler, { signal: controller.signal });
controller.abort(); // removes listener
```

**2. Closures holding large data:**

```js
function processData(largeArray) {
  const processed = expensiveProcess(largeArray);

  return function report() {
    // largeArray is still in scope even if not used
    return processed.summary;
  };
}

// Fix: don't capture what you don't need
function processData(largeArray) {
  const summary = expensiveProcess(largeArray).summary;
  return function report() {
    return summary;
  };
}
```

**3. Detached DOM nodes:**

```js
// Leak — removed node still referenced
const button = document.getElementById('btn');
document.body.removeChild(button);
// button variable still holds reference — not GC'd

// Fix — null the reference when done
button = null;
```

**4. Uncleared timers:**

```js
// Leak — setInterval keeps running even after component unmounts
const id = setInterval(poll, 1000);

// Fix
clearInterval(id);
```

---

### Debounce vs Throttle

**Debounce** delays execution until after a quiet period. Use for events that fire rapidly and you only care about the final state (search input, window resize).

**Throttle** limits execution to once per interval. Use for events where you want regular updates but not every tick (scroll, mousemove).

```js
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function throttle(fn, interval) {
  let lastCall = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastCall >= interval) {
      lastCall = now;
      return fn.apply(this, args);
    }
  };
}

// Usage
const onSearch = debounce((query) => fetchResults(query), 300);
const onScroll = throttle(() => updateUI(), 100);
```

---

## 7. Modules

### CommonJS vs ES Modules

**CommonJS** (Node.js default pre-ESM): synchronous, runtime evaluation, values are copied.

```js
// exporting
module.exports = { add, subtract };
// or
exports.add = add;

// importing
const { add } = require('./math');
const math = require('./math'); // whole object
```

**ES Modules**: static, analyzed at parse time (enables tree-shaking), values are live bindings.

```js
// named exports
export const add = (a, b) => a + b;
export function subtract(a, b) {
  return a - b;
}

// default export
export default class Calculator {}

// importing
import { add, subtract } from './math.js';
import Calculator, { add } from './math.js';
import * as math from './math.js';
```

**Key differences:**

|                     | CommonJS         | ES Modules          |
| ------------------- | ---------------- | ------------------- |
| Evaluation          | Runtime          | Parse time (static) |
| Binding             | Copied value     | Live binding        |
| Top-level `await`   | No               | Yes                 |
| Tree-shaking        | No               | Yes                 |
| `this` at top level | `module.exports` | `undefined`         |

---

### Dynamic Imports & Tree-Shaking

**Dynamic import** loads a module lazily at runtime, returning a Promise. Essential for code-splitting.

```js
// Static — always loaded
import { heavyLib } from './heavy.js';

// Dynamic — loaded on demand
button.addEventListener('click', async () => {
  const { heavyLib } = await import('./heavy.js');
  heavyLib.run();
});

// Conditional loading
const module = await import(process.env.NODE_ENV === 'test' ? './mock-api.js' : './api.js');
```

**Tree-shaking** is the process of eliminating unused exports from a bundle. It requires:

1. ES module syntax (static `import`/`export`)
2. No side effects on import (or `"sideEffects": false` in `package.json`)
3. A bundler that performs it (Webpack, Rollup, esbuild)

---

## 8. Browser & Node.js Runtime

### Event Delegation

Instead of attaching listeners to every child element, attach one listener to a parent and use `event.target` to identify the source. More memory-efficient, works for dynamically added elements.

```js
document.getElementById('list').addEventListener('click', (event) => {
  const item = event.target.closest('li[data-id]');
  if (!item) return;

  const id = item.dataset.id;
  handleItemClick(id);
});
```

---

### Node.js Event Loop vs Browser

Both use an event loop, but Node.js has additional phases:

```
   ┌───────────────────────────┐
   │           timers           │  ← setTimeout, setInterval callbacks
   ├───────────────────────────┤
   │     pending callbacks      │  ← I/O errors from previous tick
   ├───────────────────────────┤
   │       idle, prepare        │  ← internal use
   ├───────────────────────────┤
   │           poll             │  ← retrieve new I/O events (blocks here if queue empty)
   ├───────────────────────────┤
   │           check            │  ← setImmediate callbacks
   ├───────────────────────────┤
   │      close callbacks       │  ← socket.on('close', ...)
   └───────────────────────────┘
```

**`setImmediate` vs `setTimeout(fn, 0)`:**

```js
// Inside an I/O callback, setImmediate always fires before setTimeout
fs.readFile('file', () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate'));
  // Always: immediate, timeout
});
```

**`process.nextTick`** fires before the event loop continues to the next phase — even before Promise microtasks. Use sparingly.

```js
console.log('1');
process.nextTick(() => console.log('2'));
Promise.resolve().then(() => console.log('3'));
console.log('4');
// Output: 1, 4, 2, 3
```

---

### Streams & Buffer

**Streams** process data in chunks, keeping memory usage constant regardless of data size.

```js
const { createReadStream, createWriteStream } = require('fs');
const { createGzip } = require('zlib');

// Pipe: read → compress → write (constant memory)
createReadStream('large.log')
  .pipe(createGzip())
  .pipe(createWriteStream('large.log.gz'))
  .on('finish', () => console.log('done'));
```

**Buffer** represents fixed-length raw binary data. Used for TCP streams, file I/O, cryptography.

```js
const buf = Buffer.from('hello', 'utf8');
buf.toString('hex'); // '68656c6c6f'
buf.toString('base64'); // 'aGVsbG8='

// Allocate and fill
const zero = Buffer.alloc(10); // 10 bytes, zeroed
const unsafe = Buffer.allocUnsafe(10); // 10 bytes, uninitialized (faster, but contains old memory)
```

---

## 9. Error Handling

### `try`/`catch`/`finally`

```js
function parseJSON(str) {
  try {
    return JSON.parse(str);
  } catch (err) {
    if (err instanceof SyntaxError) {
      console.error('Invalid JSON:', err.message);
      return null;
    }
    throw err; // re-throw unexpected errors
  } finally {
    // Runs regardless of success or failure — good for cleanup
    console.log('parseJSON finished');
  }
}
```

**`finally` always runs, even if `catch` throws or `return` is hit.**

---

### Custom Error Types

Extend `Error` to create domain-specific error types that can be caught selectively.

```js
class AppError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = this.constructor.name;
    this.code = options.code ?? 'UNKNOWN_ERROR';
    this.statusCode = options.statusCode ?? 500;
    Error.captureStackTrace?.(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource, id) {
    super(`${resource} with id ${id} not found`, { code: 'NOT_FOUND', statusCode: 404 });
    this.resource = resource;
    this.id = id;
  }
}

class ValidationError extends AppError {
  constructor(field, message) {
    super(message, { code: 'VALIDATION_ERROR', statusCode: 400 });
    this.field = field;
  }
}

// Usage
try {
  throw new NotFoundError('User', 42);
} catch (err) {
  if (err instanceof NotFoundError) {
    res.status(err.statusCode).json({ error: err.message });
  } else {
    throw err;
  }
}
```

---

### Async Error Handling Patterns

```js
// Unhandled rejection — always add a catch or global handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection:', reason);
  process.exit(1);
});

// Async IIFE entry point — wrap in try/catch
(async () => {
  try {
    await main();
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
})();

// Helper to avoid try/catch boilerplate — Go-style error tuples
async function to(promise) {
  try {
    return [null, await promise];
  } catch (err) {
    return [err, null];
  }
}

const [err, user] = await to(fetchUser(id));
if (err) return handleError(err);
```

---

# Part 2: TypeScript

---

## 10. Type System Fundamentals

### Basic Types & Type Inference

TypeScript infers types from assignments — explicit annotations are only needed when inference can't do it.

```ts
// Inferred
const name = 'Alice'; // string
const count = 0; // number
const active = true; // boolean
const items = [1, 2, 3]; // number[]

// Explicit — needed when initializing without a value
let input: string;
let data: Record<string, unknown>;

// Primitives
let n: number = 42;
let s: string = 'hello';
let b: boolean = true;
let u: undefined = undefined;
let nl: null = null;
let big: bigint = 100n;

// Arrays
let nums: number[] = [1, 2, 3];
let strs: Array<string> = ['a', 'b'];

// Tuple — fixed-length, typed positionally
let pair: [string, number] = ['age', 30];

// any — disables type checking (avoid)
let x: any = 'hello';
x = 42; // ok

// unknown — safe alternative to any (must narrow before use)
let y: unknown = getInput();
if (typeof y === 'string') y.toUpperCase(); // ok after narrowing
```

---

### `interface` vs `type`

Both define object shapes, but with key differences:

```ts
// interface — can be extended and merged
interface User {
  id: number;
  name: string;
}

interface Admin extends User {
  role: 'admin';
}

// Declaration merging — two declarations of the same interface merge
interface Window {
  myCustomProp: string;
}

// type — more flexible, supports unions/intersections/primitives
type ID = string | number;
type Point = { x: number; y: number };
type Named = { name: string };
type NamedPoint = Point & Named;

// type cannot be re-declared (no merging)
```

**Rule of thumb:** use `interface` for object shapes and public API contracts (supports merging); use `type` for unions, intersections, mapped types, and aliases.

---

### Union, Intersection, Literal Types

```ts
// Union — one of these types
type Result = 'success' | 'error' | 'loading';
type ID = string | number;
type MaybeUser = User | null;

// Intersection — all of these types combined
type AdminUser = User & { permissions: string[] };

// Literal types — specific values as types
type Direction = 'north' | 'south' | 'east' | 'west';
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type StatusCode = 200 | 201 | 400 | 401 | 403 | 404 | 500;

// Discriminated union — union with a shared literal field for narrowing
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number }
  | { kind: 'triangle'; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    case 'triangle':
      return 0.5 * shape.base * shape.height;
  }
}
```

---

## 11. Advanced Types

### Generics

Generics make components work over many types while preserving type information.

```ts
// Generic function
function identity<T>(value: T): T {
  return value;
}

identity<string>('hello'); // type: string
identity(42); // inferred: number

// Generic with constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { id: 1, name: 'Alice' };
getProperty(user, 'name'); // string — typed correctly
getProperty(user, 'age'); // Error — 'age' not in type

// Generic interface
interface Repository<T> {
  findById(id: number): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<T>;
  delete(id: number): Promise<void>;
}

// Generic class
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }
  pop(): T | undefined {
    return this.items.pop();
  }
  peek(): T | undefined {
    return this.items.at(-1);
  }
  isEmpty(): boolean {
    return this.items.length === 0;
  }
}

const stack = new Stack<number>();
stack.push(1);
stack.pop(); // number | undefined
```

---

### Mapped Types

Mapped types transform each property in an existing type.

```ts
// Built on the mapped type syntax: { [K in keyof T]: ... }

// Make all properties optional
type Partial<T> = { [K in keyof T]?: T[K] };

// Make all properties required
type Required<T> = { [K in keyof T]-?: T[K] };

// Make all properties readonly
type Readonly<T> = { readonly [K in keyof T]: T[K] };

// Custom mapped types
type Nullable<T> = { [K in keyof T]: T[K] | null };

type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface User {
  id: number;
  name: string;
}
type UserGetters = Getters<User>;
// { getId: () => number; getName: () => string }
```

---

### Conditional Types

Types that choose between two possibilities based on a condition.

```ts
type IsArray<T> = T extends any[] ? true : false;
IsArray<string[]>; // true
IsArray<string>; // false

// infer — extract a type from a conditional
type ElementType<T> = T extends (infer E)[] ? E : never;
ElementType<string[]>; // string
ElementType<number>; // never

type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type Awaited<T> = T extends Promise<infer V> ? V : T;

// Distributive conditional types — applied to each member of a union
type ToArray<T> = T extends any ? T[] : never;
ToArray<string | number>; // string[] | number[]

// Non-distributive — wrap in tuple to prevent distribution
type ToArrayND<T> = [T] extends [any] ? T[] : never;
ToArrayND<string | number>; // (string | number)[]
```

---

### Template Literal Types

Types built from string literal combinations.

```ts
type EventName = 'click' | 'focus' | 'blur';
type HandlerName = `on${Capitalize<EventName>}`;
// 'onClick' | 'onFocus' | 'onBlur'

type CSSProperty = 'margin' | 'padding';
type CSSDirection = 'Top' | 'Right' | 'Bottom' | 'Left';
type LonghandProperty = `${CSSProperty}${CSSDirection}`;
// 'marginTop' | 'marginRight' | ... | 'paddingLeft'

// Typed event emitter
type EventMap = {
  userCreated: { id: number; name: string };
  orderPlaced: { orderId: string; total: number };
};

type EventNames = keyof EventMap;
type ListenerName<T extends EventNames> = `on${Capitalize<T>}`;

function on<T extends EventNames>(event: T, handler: (payload: EventMap[T]) => void): void {}

on('userCreated', ({ id, name }) => {}); // payload fully typed
on('orderPlaced', ({ orderId, total }) => {});
```

---

### Utility Types

TypeScript's built-in type transformers:

```ts
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

// Partial — all properties optional
type UserUpdate = Partial<User>;

// Required — all properties required
type StrictUser = Required<Partial<User>>;

// Pick — subset of properties
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit — all except specified
type UserWithoutId = Omit<User, 'id'>;

// Record — map type
type UserMap = Record<string, User>;
type StatusMap = Record<'active' | 'inactive' | 'banned', User[]>;

// Exclude / Extract — filter union members
type T1 = Exclude<'a' | 'b' | 'c', 'a'>; // 'b' | 'c'
type T2 = Extract<'a' | 'b' | 'c', 'a' | 'c'>; // 'a' | 'c'

// NonNullable
type T3 = NonNullable<string | null | undefined>; // string

// ReturnType / Parameters
function fetchUser(id: number, token: string): Promise<User> {}
type FetchReturn = ReturnType<typeof fetchUser>; // Promise<User>
type FetchParams = Parameters<typeof fetchUser>; // [number, string]

// ConstructorParameters / InstanceType
class Service {
  constructor(url: string, timeout: number) {}
}
type ServiceParams = ConstructorParameters<typeof Service>; // [string, number]
type ServiceInstance = InstanceType<typeof Service>; // Service
```

---

## 12. TypeScript in Practice

### `unknown` vs `any` vs `never`

- **`any`** — opts out of type checking entirely. Avoid unless dealing with truly dynamic code or migrating from JS.
- **`unknown`** — type-safe alternative to `any`. You must narrow it before using it.
- **`never`** — represents an impossible type. A function that always throws or loops forever returns `never`. Useful for exhaustiveness checks.

```ts
// unknown requires narrowing
function process(input: unknown): string {
  if (typeof input === 'string') return input.toUpperCase();
  if (typeof input === 'number') return input.toFixed(2);
  throw new Error('Unsupported type');
}

// never for exhaustiveness
function assertNever(x: never): never {
  throw new Error(`Unhandled case: ${x}`);
}

function handleShape(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    // If you add a new Shape variant and forget to handle it,
    // TypeScript errors here because shape is now never assignable to never
    default:
      return assertNever(shape);
  }
}
```

---

### Type Narrowing & Type Guards

TypeScript narrows types within conditional branches using control flow analysis.

```ts
// typeof narrowing
function format(value: string | number): string {
  if (typeof value === 'string') return value.toUpperCase();
  return value.toFixed(2);
}

// instanceof narrowing
function handle(err: unknown): string {
  if (err instanceof ValidationError) return err.field;
  if (err instanceof Error) return err.message;
  return 'Unknown error';
}

// in operator narrowing
function move(animal: Cat | Dog): void {
  if ('fly' in animal) {
    /* never — neither has fly */
  }
  if ('meow' in animal) animal.meow();
  else animal.bark();
}

// User-defined type guard — return type is a type predicate
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' && obj !== null && 'id' in obj && 'name' in obj;
}

// Assertion function — narrows or throws
function assertIsString(val: unknown): asserts val is string {
  if (typeof val !== 'string') throw new TypeError('Not a string');
}
```

---

### Declaration Merging

TypeScript merges multiple declarations with the same name.

```ts
// Interface merging — used for module augmentation
interface Request {
  user?: User;
}

// Merged with Express's Request — no need to re-declare everything
// Now req.user is typed everywhere

// Namespace merging with function/class
function createPlugin(name: string): Plugin {}

namespace createPlugin {
  export interface Options {
    debug?: boolean;
  }
  export const version = '1.0.0';
}

createPlugin('foo');
createPlugin.version; // '1.0.0'
```

---

### Module Augmentation

Add types to an existing module without modifying it.

```ts
// Augment Express to add user to Request
import 'express';

declare module 'express' {
  interface Request {
    user?: {
      id: number;
      roles: string[];
    };
  }
}

// Augment a global
declare global {
  interface Window {
    analytics: AnalyticsClient;
  }

  interface Array<T> {
    last(): T | undefined;
  }
}
```

---

## 13. Decorators in TypeScript

Decorators are functions that can annotate and modify classes, methods, properties, and parameters. They run at class definition time, not at instantiation.

Enable in `tsconfig.json`:

```json
{
  "experimentalDecorators": true, // legacy TS decorators
  "emitDecoratorMetadata": true // needed for reflect-metadata
}
```

---

### Class Decorator

Receives the constructor. Can return a new constructor to replace the class.

```ts
function Singleton<T extends { new (...args: any[]): {} }>(constructor: T) {
  let instance: InstanceType<T>;
  return class extends constructor {
    constructor(...args: any[]) {
      if (instance) return instance;
      super(...args);
      instance = this as unknown as InstanceType<T>;
    }
  };
}

@Singleton
class Config {
  value = Math.random();
}

new Config() === new Config(); // true — same instance
```

---

### Method Decorator

Receives the target (prototype), method name, and property descriptor. Used for logging, timing, access control.

```ts
function Log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${key} with`, args);
    const result = original.apply(this, args);
    console.log(`${key} returned`, result);
    return result;
  };
  return descriptor;
}

function Memoize(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  const cache = new Map<string, unknown>();
  descriptor.value = function (...args: unknown[]) {
    const cacheKey = JSON.stringify(args);
    if (cache.has(cacheKey)) return cache.get(cacheKey);
    const result = original.apply(this, args);
    cache.set(cacheKey, result);
    return result;
  };
  return descriptor;
}

class MathService {
  @Log
  @Memoize
  fibonacci(n: number): number {
    if (n <= 1) return n;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }
}
```

---

### Property Decorator

Receives the target and property name. Cannot directly modify the property value — typically used to record metadata.

```ts
function Required(target: object, key: string) {
  const required: string[] = Reflect.getMetadata('required', target) ?? [];
  required.push(key);
  Reflect.defineMetadata('required', required, target);
}

function validate(obj: object): string[] {
  const required: string[] = Reflect.getMetadata('required', obj) ?? [];
  return required.filter((key) => (obj as any)[key] == null);
}

class CreateUserDto {
  @Required
  name!: string;

  @Required
  email!: string;

  age?: number;
}

const dto = new CreateUserDto();
validate(dto); // ['name', 'email']
```

---

### Parameter Decorator

Receives the target, method name, and parameter index. Used by frameworks like NestJS for dependency injection.

```ts
function Inject(token: string) {
  return function (target: object, _key: string | symbol, index: number) {
    const existing = Reflect.getMetadata('inject', target) ?? {};
    existing[index] = token;
    Reflect.defineMetadata('inject', existing, target);
  };
}
```

---

### TC39 Stage 3 Decorators (Modern)

The new spec-compliant decorators (TypeScript 5+) use a different API with a `context` object:

```ts
// tsconfig: "experimentalDecorators": false (default in TS 5+)

function logged<T extends (...args: any[]) => any>(fn: T, context: ClassMethodDecoratorContext) {
  return function (this: unknown, ...args: Parameters<T>): ReturnType<T> {
    console.log(`Calling ${String(context.name)}`);
    return fn.apply(this, args);
  };
}

class Service {
  @logged
  fetchData(id: number) {
    return fetch(`/api/data/${id}`);
  }
}
```

---

### NestJS/Angular Patterns

Common patterns you'll see in interviews for server-side TypeScript:

```ts
// NestJS controller — decorators define routing and DI
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get(':id')
  findOne(@Param('id') id: string): Promise<User> {
    return this.usersService.findById(+id);
  }

  @Post()
  @HttpCode(201)
  create(@Body() dto: CreateUserDto): Promise<User> {
    return this.usersService.create(dto);
  }
}
```

---

## 14. TypeScript Configuration

### Key `tsconfig.json` Options

```jsonc
{
  "compilerOptions": {
    // Strictness — always enable in new projects
    "strict": true, // enables all strict checks below
    "noImplicitAny": true, // error on inferred 'any'
    "strictNullChecks": true, // null/undefined not assignable to other types
    "strictFunctionTypes": true, // stricter function parameter checking
    "noImplicitThis": true, // error on 'this' with implicit 'any' type
    "useUnknownInCatchVariables": true, // catch (e: unknown) instead of any

    // Output
    "target": "ES2022", // compiled JS version
    "module": "NodeNext", // module system
    "outDir": "./dist",
    "rootDir": "./src",

    // Module resolution
    "moduleResolution": "NodeNext",
    "baseUrl": ".",
    "paths": {
      "@app/*": ["src/*"], // path aliases
    },

    // Extras
    "esModuleInterop": true, // default imports from CJS modules
    "skipLibCheck": true, // skip .d.ts checking (faster builds)
    "sourceMap": true,
    "declaration": true, // emit .d.ts files
    "declarationMap": true,

    // Safety
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true, // all code paths must return a value
    "noFallthroughCasesInSwitch": true,
  },
}
```

---

### Project References

Splits a large TypeScript project into smaller subprojects that can be built independently. Enables incremental builds and enforces layer boundaries.

```jsonc
// packages/core/tsconfig.json
{
  "compilerOptions": { "composite": true, "outDir": "dist" },
  "include": ["src"]
}

// packages/api/tsconfig.json
{
  "compilerOptions": { "composite": true },
  "references": [{ "path": "../core" }]
}

// root tsconfig.json
{
  "references": [
    { "path": "packages/core" },
    { "path": "packages/api" }
  ]
}
```

Build with `tsc --build` (or `tsc -b`) — only rebuilds changed packages.

---

### Declaration Files (`.d.ts`)

Declaration files describe the shape of JavaScript without any implementation. They're what `npm` packages ship to provide TypeScript support.

```ts
// types/legacy-lib.d.ts — typing an untyped JS library
declare module 'legacy-lib' {
  export function process(input: string): string;
  export interface Config {
    debug?: boolean;
    timeout?: number;
  }
  export default function init(config?: Config): void;
}

// Ambient declarations — describe globals that exist at runtime
declare const __DEV__: boolean;
declare const __VERSION__: string;

// .d.ts for a CommonJS module
declare function legacyFn(x: string): number;
declare namespace legacyFn {
  export interface Options {
    verbose: boolean;
  }
}
export = legacyFn;
```

**`@types/*` packages** on npm are community-maintained declaration files for popular JS libraries (e.g., `@types/node`, `@types/lodash`).

---

# Part 1 (continued):

---

## 15. Async Iteration

`for await...of` consumes async iterables. Async generators (`async function*`) produce them.

```js
// Async generator — yields values with async gaps between them
async function* paginate(url) {
  let cursor = null;
  do {
    const res = await fetch(`${url}${cursor ? `?cursor=${cursor}` : ''}`);
    const { data, nextCursor } = await res.json();
    yield* data;           // yield each item in the page
    cursor = nextCursor;
  } while (cursor);
}

// for await...of — consumes any async iterable
for await (const user of paginate('/api/users')) {
  console.log(user.name);
}

// Node.js Readable streams implement AsyncIterable (Node 12+)
import { createReadStream } from 'fs';
import { createInterface } from 'readline';

async function processLines(path) {
  const rl = createInterface({ input: createReadStream(path) });
  for await (const line of rl) {
    processLine(line); // constant memory — one line at a time
  }
}

// Implementing the async iterator protocol manually
const asyncRange = {
  [Symbol.asyncIterator]() {
    let i = 0;
    return {
      async next() {
        await new Promise(r => setTimeout(r, 10)); // simulate async work
        if (i < 3) return { value: i++, done: false };
        return { value: undefined, done: true };
      },
    };
  },
};

for await (const val of asyncRange) {
  console.log(val); // 0, 1, 2
}

// Early exit — finally in generator still runs
async function* withCleanup() {
  try {
    yield 1;
    yield 2;
  } finally {
    console.log('cleaned up'); // runs even if caller breaks early
  }
}

for await (const n of withCleanup()) {
  if (n === 1) break; // triggers finally block
}
```

**Key interview points:**
- `Symbol.asyncIterator` — makes any object async-iterable (same role as `Symbol.iterator` for sync)
- `yield*` inside an async generator delegates to another async iterable
- `for await...of` works on: async generators, Node.js streams, Web ReadableStreams, anything with `[Symbol.asyncIterator]`
- `break`/`return` inside `for await` calls `.return()` on the iterator, triggering `finally` blocks

---

## 16. Array Methods Deep Dive

```js
const nums = [1, 2, 3, 4, 5];

// find / findIndex — return first match (undefined / -1 if none)
nums.find(x => x > 3);       // 4
nums.findIndex(x => x > 3);  // 3 (index)

// findLast / findLastIndex (ES2023) — search from the end
[1, 2, 3, 2].findLast(x => x === 2);      // 2 (last occurrence)
[1, 2, 3, 2].findLastIndex(x => x === 2); // 3

// some / every
nums.some(x => x > 4);  // true — at least one match
nums.every(x => x > 0); // true — all match
nums.every(x => x > 1); // false

// at() — negative indexing (no more .length - 1)
nums.at(-1); // 5
nums.at(-2); // 4

// flat — flattens nested arrays (default depth: 1)
[[1, 2], [3, [4, 5]]].flat();         // [1, 2, 3, [4, 5]]
[[1, 2], [3, [4, 5]]].flat(2);        // [1, 2, 3, 4, 5]
[[1, [2, [3]]]].flat(Infinity);       // [1, 2, 3]

// flatMap — map then flat(1); more efficient than .map().flat()
const sentences = ['Hello world', 'foo bar'];
sentences.flatMap(s => s.split(' ')); // ['Hello', 'world', 'foo', 'bar']

// flatMap as filter+map in one pass (return [] to skip)
[-2, 1, -3, 4].flatMap(x => x > 0 ? [x * 2] : []); // [2, 8]

// Non-mutating variants (ES2023)
const arr = [3, 1, 2];
arr.toSorted();      // [1, 2, 3] — new array, original unchanged
arr.toReversed();    // [2, 1, 3]
arr.with(1, 99);     // [3, 99, 2] — replace index 1

// reduce — group-by pattern
const orders = [
  { product: 'A', qty: 2, price: 10 },
  { product: 'B', qty: 1, price: 25 },
  { product: 'A', qty: 3, price: 10 },
];
const totals = orders.reduce((acc, { product, qty, price }) => {
  acc[product] = (acc[product] ?? 0) + qty * price;
  return acc;
}, {}); // { A: 50, B: 25 }
```

**Distinctions interviewers probe:**
- `find` returns the **element**, `findIndex` returns the **index** — both stop at first match
- `some` short-circuits on first `true`; `every` short-circuits on first `false`
- `flatMap` only flattens **one level** — use `flat(n)` for deeper nesting
- `at()` works on strings and TypedArrays too, not just arrays
- `toSorted`/`toReversed`/`with` are the immutable counterparts to `sort`/`reverse`/direct assignment

---

## 17. Object Static Methods

```js
const user = { name: 'Alice', age: 30 };

// Keys / values / entries — own enumerable string keys only
Object.keys(user);    // ['name', 'age']
Object.values(user);  // ['Alice', 30]
Object.entries(user); // [['name', 'Alice'], ['age', 30]]

// fromEntries — inverse of entries; also accepts Map
Object.fromEntries([['name', 'Alice'], ['age', 30]]); // { name: 'Alice', age: 30 }
Object.fromEntries(new Map([['a', 1], ['b', 2]]));    // { a: 1, b: 2 }

// Transform object values without a library
const doubled = Object.fromEntries(
  Object.entries(user).map(([k, v]) => [k, typeof v === 'number' ? v * 2 : v])
); // { name: 'Alice', age: 60 }

// getOwnPropertyNames — includes non-enumerable keys (unlike Object.keys)
const obj = {};
Object.defineProperty(obj, 'hidden', { value: 42, enumerable: false });
obj.visible = 'yes';

Object.keys(obj);                // ['visible'] — enumerable only
Object.getOwnPropertyNames(obj); // ['visible', 'hidden'] — all own string keys
// Object.getOwnPropertySymbols(obj) — symbol keys only

// freeze — shallow immutability (no add, delete, or write)
const config = Object.freeze({ host: 'localhost', port: 3000 });
config.port = 5000;   // TypeError in strict mode, silent otherwise
config.extra = 'x';   // same — silently ignored

// Freeze is SHALLOW — nested objects remain mutable
const nested = Object.freeze({ db: { host: 'localhost' } });
nested.db.host = 'remote'; // still works — nested object not frozen

// seal — prevent add/delete, but allow writes to existing properties
const sealed = Object.seal({ x: 1 });
sealed.x = 2;      // OK — writable
sealed.y = 3;      // silently ignored — can't add
delete sealed.x;   // silently ignored — can't delete

// Introspection
Object.isFrozen(config); // true
Object.isSealed(sealed);  // true

Object.getOwnPropertyDescriptor(config, 'port');
// { value: 3000, writable: false, enumerable: true, configurable: false }
```

| Method | Own? | Enumerable-only? | Includes symbols? |
|---|---|---|---|
| `Object.keys` | ✓ | ✓ (yes, only) | ✗ |
| `Object.getOwnPropertyNames` | ✓ | ✗ (all string keys) | ✗ |
| `Object.getOwnPropertySymbols` | ✓ | ✗ | ✓ |
| `for...in` | ✗ (+ inherited) | ✓ | ✗ |

---

## 18. AggregateError

`AggregateError` wraps multiple errors into one. It's thrown by `Promise.any` when **all** promises reject.

```js
// Promise.any — resolves with the first fulfillment, rejects with AggregateError if all fail
try {
  const result = await Promise.any([
    fetch('https://cdn1.example.com/data.json'),
    fetch('https://cdn2.example.com/data.json'),
    fetch('https://cdn3.example.com/data.json'),
  ]);
  console.log(result); // fastest successful response
} catch (err) {
  if (err instanceof AggregateError) {
    console.log(err.message);        // 'All promises were rejected'
    console.log(err.errors.length);  // 3
    err.errors.forEach(e => console.error(e.message));
  }
}

// Creating AggregateError manually — useful for collecting all validation failures
function validateAll(value, rules) {
  const errors = rules
    .map(rule => rule(value))
    .filter(Boolean);
  if (errors.length) {
    throw new AggregateError(errors, `${errors.length} validation error(s)`);
  }
}

// Centralized error handler that unpacks AggregateError
function handleError(err) {
  if (err instanceof AggregateError) {
    for (const inner of err.errors) handleError(inner);
    return;
  }
  logger.error(err);
}
```

**`Promise.any` vs other combinators:**
- `Promise.all` — rejects on **first** rejection (single error)
- `Promise.allSettled` — never rejects; returns `{status, value/reason}[]`
- `Promise.race` — settles on **first** settlement (resolve or reject)
- `Promise.any` — rejects only when **all** reject; uses `AggregateError`

---

## 19. Intl API

The `Intl` namespace provides locale-aware formatting with no external dependencies.

```js
// Number formatting
const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
usd.format(1_234_567.89); // '$1,234,567.89'

const compact = new Intl.NumberFormat('en', { notation: 'compact' });
compact.format(1_500_000); // '1.5M'

const pct = new Intl.NumberFormat('en', { style: 'percent', maximumFractionDigits: 1 });
pct.format(0.1234); // '12.3%'

// Date/time formatting
const dtf = new Intl.DateTimeFormat('en-US', {
  dateStyle: 'full',
  timeStyle: 'short',
  timeZone: 'America/New_York',
});
dtf.format(new Date()); // 'Wednesday, June 4, 2026 at 3:45 PM'

// Relative time
const rel = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
rel.format(-1, 'day');   // 'yesterday'
rel.format(-3, 'month'); // '3 months ago'
rel.format(2, 'week');   // 'in 2 weeks'

// List formatting
const listFmt = new Intl.ListFormat('en', { type: 'conjunction' });
listFmt.format(['Alice', 'Bob', 'Carol']); // 'Alice, Bob, and Carol'

const orFmt = new Intl.ListFormat('en', { type: 'disjunction' });
orFmt.format(['email', 'phone']); // 'email or phone'

// Locale-aware string sorting (handles ä, ö, ü, etc. correctly)
const collator = new Intl.Collator('de');
['ä', 'z', 'a'].sort(collator.compare); // ['a', 'ä', 'z']

// Plural rules — pick the right translation key
const pr = new Intl.PluralRules('en');
const key = `item_${pr.select(count)}`; // 'item_one' vs 'item_other'
```

**Performance tip:** Constructing `Intl` objects is expensive — cache them at module level rather than re-creating per render/call. `formatToParts()` returns the parts array when you need to style components of the output separately (e.g., currency symbol vs number).

---

# Part 2 (continued):

---

## 20. `satisfies` Operator

`satisfies` (TS 4.9+) validates that a value matches a type **without widening the inferred type**.

```ts
type Colors = Record<string, string | number[]>;

// Explicit annotation — validates, but TypeScript widens the type
const palette1: Colors = {
  red: [255, 0, 0],
  green: '#00ff00',
};
palette1.red.map(x => x * 2); // Error: 'string | number[]' has no 'map'
// TypeScript sees red as string | number[] — lost the narrowed type

// satisfies — validates against the type AND keeps the inferred type
const palette2 = {
  red: [255, 0, 0],
  green: '#00ff00',
  blue: [0, 0, 255],
} satisfies Colors;

palette2.red.map(x => x * 2);    // OK — TypeScript still knows it's number[]
palette2.green.toUpperCase();     // OK — TypeScript still knows it's string
// @ts-expect-error
palette2.purple;                  // Error — unknown key detected

// Real-world: typed config without losing literal inference
const routes = {
  home: '/',
  about: '/about',
  api: { users: '/api/users', posts: '/api/posts' },
} satisfies Record<string, string | Record<string, string>>;

routes.api.users.startsWith('/'); // OK — TypeScript knows it's string, not string | Record<...>

// Combine with 'as const' for fully literal types
const theme = {
  colors: { primary: '#3b82f6', danger: '#ef4444' },
  spacing: [4, 8, 16, 32],
} as const satisfies {
  colors: Record<string, string>;
  spacing: number[];
};
// theme.colors.primary is '#3b82f6' (literal), validated against Record<string, string>
```

**When to use `satisfies` vs `: Type`:**
- `: Type` — you need the variable to be treated as the broad type downstream
- `satisfies` — you want validation at the definition site but need to retain the narrowed/literal types for usage

---

## 21. Explicit Resource Management (`using`)

TS 5.2+ / ES2025 — automatic cleanup via `Symbol.dispose` / `Symbol.asyncDispose`.

```ts
// Symbol.dispose — synchronous cleanup
class DbConnection {
  constructor(public url: string) {}
  query(sql: string) { return [] as Row[]; }
  [Symbol.dispose]() {
    console.log('connection closed');
  }
}

// 'using' — calls [Symbol.dispose] when the block exits, even on throw
function processUsers() {
  using db = new DbConnection('postgres://localhost/mydb');
  return db.query('SELECT * FROM users');
} // db[Symbol.dispose]() called automatically

// Symbol.asyncDispose — async cleanup
class FileHandle {
  constructor(public fd: number) {}
  async write(data: string) { /* ... */ }
  async [Symbol.asyncDispose]() {
    await fs.promises.close(this.fd);
  }
}

// 'await using' — for async cleanup
async function writeReport(path: string) {
  await using file = await openFile(path); // openFile returns FileHandle
  await file.write('report data');
} // await file[Symbol.asyncDispose]() on exit

// DisposableStack — group multiple resources, disposed in reverse order
function multiResource() {
  using stack = new DisposableStack();
  const conn = stack.use(new DbConnection('...'));
  const lock = stack.use(acquireLock());
  doWork(conn, lock);
} // lock disposed first, then conn

// Adapting non-Disposable resources
function withTimer() {
  const id = setInterval(tick, 1000);
  using _cleanup = {
    [Symbol.dispose]() { clearInterval(id); }
  };
  runWork();
} // interval cleared automatically
```

**Why it matters:** Eliminates `try/finally` boilerplate and makes resource leaks harder to introduce — the compiler enforces cleanup. Works with file handles, DB connections, locks, timers, and any object you add `[Symbol.dispose]` to.

---

## 22. `const` Type Parameters

TS 5.0+ — `<const T>` infers literal/tuple/readonly types from arguments without requiring `as const` at call sites.

```ts
// Without const — generic infers a wide type
function makeArray<T>(values: T[]): T[] {
  return values;
}
const arr1 = makeArray(['a', 'b', 'c']); // T = string, arr1: string[]
// arr1[0] is string, not 'a'

// With 'as const' at the call site — works but callers must remember
const arr2 = makeArray(['a', 'b', 'c'] as const); // T = readonly ['a', 'b', 'c']

// With <const T> — TS 5.0 — literal types inferred automatically
function makeArrayConst<const T>(values: T[]): T[] {
  return values;
}
const arr3 = makeArrayConst(['a', 'b', 'c']); // T = readonly ['a', 'b', 'c']
arr3[0]; // type: 'a'

// Typed event emitter — event names inferred as literals
function on<const T extends string>(event: T, handler: () => void): T {
  document.addEventListener(event, handler);
  return event;
}
const evt = on('click', handler); // type: 'click', not string

// Route builder — path inferred as literal
function createRoute<const Path extends string>(path: Path) {
  return { path, match: (url: string) => url === path };
}
const route = createRoute('/users/:id');
route.path; // type: '/users/:id'

// Object shapes preserved as literals
function createConfig<const T extends Record<string, unknown>>(config: T): T {
  return config;
}
const cfg = createConfig({ env: 'production', retries: 3 });
cfg.env;     // type: 'production', not string
cfg.retries; // type: 3, not number
```

**When `<const T>` applies:** Any generic that receives a literal value (string, number, object, array) and you want the return type or downstream types to reflect the exact value rather than the widened base type. The caller doesn't need `as const` — the constraint is encoded in the function signature.

---

_Last updated: 2026-06-04_
