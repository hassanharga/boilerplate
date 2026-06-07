# Go (Golang) Learning Reference

A comprehensive learning guide covering the full language from basics to advanced patterns. Not just interview prep — this is a working reference.

---

## Table of Contents

### Part 1: Language Fundamentals
1. [Go Philosophy & Hello World](#1-go-philosophy--hello-world)
2. [Variables, Constants & Types](#2-variables-constants--types)
3. [Control Flow](#3-control-flow)
4. [Functions](#4-functions)
5. [Pointers](#5-pointers)

### Part 2: Composite Types
6. [Arrays & Slices](#6-arrays--slices)
7. [Maps](#7-maps)
8. [Structs](#8-structs)

### Part 3: Interfaces & Methods
9. [Methods](#9-methods)
10. [Interfaces](#10-interfaces)
11. [Type Assertions & Type Switches](#11-type-assertions--type-switches)
12. [Embedding](#12-embedding)

### Part 4: Error Handling
13. [Errors as Values](#13-errors-as-values)
14. [Custom Errors & Wrapping](#14-custom-errors--wrapping)
15. [Panic & Recover](#15-panic--recover)

### Part 5: Concurrency
16. [Goroutines](#16-goroutines)
17. [Channels](#17-channels)
18. [Select](#18-select)
19. [sync Package](#19-sync-package)
20. [Context Package](#20-context-package)
21. [Concurrency Patterns](#21-concurrency-patterns)

### Part 6: Generics (Go 1.18+)
22. [Type Parameters & Constraints](#22-type-parameters--constraints)

### Part 7: Testing
23. [Unit Tests & Table-Driven Tests](#23-unit-tests--table-driven-tests)
24. [Benchmarks & Profiling](#24-benchmarks--profiling)
25. [Test Helpers & Mocking](#25-test-helpers--mocking)

### Part 8: Standard Library
26. [fmt, strings, strconv, unicode](#26-fmt-strings-strconv-unicode)
27. [os, io, bufio, filepath](#27-os-io-bufio-filepath)
28. [time](#28-time)
29. [net/http (Client & Server)](#29-nethttp-client--server)
30. [encoding/json](#30-encodingjson)
31. [sync/atomic & sync](#31-syncatomic--sync)
32. [context (revisited with stdlib)](#32-context-revisited-with-stdlib)
33. [sort, slices, maps (Go 1.21)](#33-sort-slices-maps-go-121)

### Part 9: Modules & Packages
34. [Go Modules](#34-go-modules)
35. [Package Design](#35-package-design)

### Part 10: Patterns & Idioms
36. [Functional Options Pattern](#36-functional-options-pattern)
37. [Error Handling Idioms](#37-error-handling-idioms)
38. [Common Pitfalls](#38-common-pitfalls)
39. [Performance Notes](#39-performance-notes)

### Part 11: Stdlib — Additional Packages
40. [log/slog (Go 1.21+)](#40-logslog-go-121)
41. [regexp](#41-regexp)
42. [embed (Go 1.16)](#42-embed-go-116)
43. [io/fs (Go 1.16)](#43-iofs-go-116)
44. [html/template & text/template](#44-htmltemplate--texttemplate)
45. [encoding/xml](#45-encodingxml)

### Part 12: Tooling & Production
46. [Build Tags & Cross-Compilation](#46-build-tags--cross-compilation)
47. [Graceful Shutdown](#47-graceful-shutdown)
48. [Dependency Injection in Go](#48-dependency-injection-in-go)
49. [runtime Package Basics](#49-runtime-package-basics)
50. [govulncheck & Security](#50-govulncheck--security)

---

# Part 1: Language Fundamentals

---

## 1. Go Philosophy & Hello World

Go was designed at Google for large-scale engineering: fast compilation, explicit error handling, built-in concurrency, and a minimal standard library with a strong stdlib.

**Key design choices:**
- **No exceptions** — errors are values returned explicitly
- **No inheritance** — composition via interfaces and embedding
- **Goroutines** — lightweight concurrency built into the language
- **Single binary output** — compiles to a statically-linked executable
- **gofmt** — one canonical code format; no style debates

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Go")
}
```

Run: `go run main.go`
Build: `go build -o app .`

---

## 2. Variables, Constants & Types

### Variable Declaration

```go
// Full declaration
var x int = 10

// Type inferred
var y = "hello"

// Short declaration (inside functions only)
z := 3.14

// Multiple variables
a, b, c := 1, "two", true

// Zero values: int=0, float=0.0, bool=false, string="", pointer=nil
var count int     // count == 0
var name string   // name == ""
```

### Constants

```go
const Pi = 3.14159
const MaxRetries = 3

// iota — auto-incrementing constant (resets per const block)
type Weekday int
const (
    Sunday Weekday = iota  // 0
    Monday                 // 1
    Tuesday                // 2
)

// Bit flags with iota
type Permission uint
const (
    Read    Permission = 1 << iota  // 1
    Write                           // 2
    Execute                         // 4
)
```

### Basic Types

| Type | Size | Range / Notes |
|------|------|---------------|
| `int` | platform (64-bit) | use for general integers |
| `int8/16/32/64` | 1/2/4/8 bytes | explicit widths |
| `uint`, `uint8/16/32/64` | — | unsigned |
| `float32`, `float64` | 4/8 bytes | prefer float64 |
| `complex64`, `complex128` | — | complex numbers |
| `bool` | 1 byte | true/false |
| `string` | — | immutable UTF-8 byte slice |
| `byte` | = uint8 | raw bytes |
| `rune` | = int32 | Unicode code point |

```go
// Type conversion is always explicit
var i int = 42
var f float64 = float64(i)
var u uint = uint(f)

// String ↔ byte slice
s := "hello"
b := []byte(s)
s2 := string(b)

// String ↔ rune slice (for Unicode-safe iteration)
r := []rune("héllo")
fmt.Println(len(r))  // 5 (characters), not len(s) which could be 6 (bytes)
```

---

## 3. Control Flow

### If / Else

```go
if x > 0 {
    fmt.Println("positive")
} else if x < 0 {
    fmt.Println("negative")
} else {
    fmt.Println("zero")
}

// Init statement — variable scoped to the if block
if err := doSomething(); err != nil {
    return fmt.Errorf("failed: %w", err)
}
```

### For (the only loop keyword in Go)

```go
// Classic C-style
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// While-style
for x > 0 {
    x--
}

// Infinite loop
for {
    // break or return to exit
}

// Range over slice
for i, v := range []string{"a", "b", "c"} {
    fmt.Println(i, v)
}

// Range over map
for k, v := range m {
    fmt.Println(k, v)
}

// Range over string (yields runes, not bytes)
for i, r := range "héllo" {
    fmt.Printf("%d: %c\n", i, r)  // i is byte offset
}

// Range over channel (blocks until channel closed)
for msg := range ch {
    fmt.Println(msg)
}

// Range over integer (Go 1.22+) — replaces for i := 0; i < N; i++
for i := range 10 {
    fmt.Println(i)  // 0..9
}
```

### Switch

```go
switch day {
case Monday, Tuesday:
    fmt.Println("early week")
case Friday:
    fmt.Println("almost weekend")
default:
    fmt.Println("mid week")
}

// No condition — acts like if-else chain
switch {
case x < 0:
    fmt.Println("negative")
case x == 0:
    fmt.Println("zero")
default:
    fmt.Println("positive")
}

// Fallthrough — explicit, unlike C (no implicit fallthrough in Go)
switch n {
case 1:
    fmt.Println("one")
    fallthrough
case 2:
    fmt.Println("one or two")
}
```

### Defer

`defer` schedules a function call to run when the surrounding function returns. Arguments are evaluated immediately.

```go
func writeFile() error {
    f, err := os.Open("file.txt")
    if err != nil {
        return err
    }
    defer f.Close()  // guaranteed to run when writeFile returns

    // ... work with f
    return nil
}
```

Multiple defers execute in **LIFO** (last in, first out) order:

```go
defer fmt.Println("3")
defer fmt.Println("2")
defer fmt.Println("1")
// Prints: 1, 2, 3
```

Defer + named return values = useful for wrapping errors:

```go
func doWork() (err error) {
    defer func() {
        if err != nil {
            err = fmt.Errorf("doWork: %w", err)
        }
    }()
    err = step1()
    if err != nil { return }
    err = step2()
    return
}
```

---

## 4. Functions

### Basic Functions

```go
func add(a, b int) int {
    return a + b
}

// Multiple parameters of same type (shorthand)
func minMax(a, b int) (int, int) {
    if a < b {
        return a, b
    }
    return b, a
}

// Named return values (useful for documentation; required for defer trick)
func divide(a, b float64) (result float64, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return  // naked return
    }
    result = a / b
    return
}
```

### Variadic Functions

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3)

// Spread a slice into variadic function
nums := []int{1, 2, 3}
sum(nums...)
```

### First-Class Functions

Functions are values. They can be passed as arguments, stored in variables, and returned.

```go
// Function type
type Predicate func(int) bool

func filter(nums []int, pred Predicate) []int {
    var result []int
    for _, n := range nums {
        if pred(n) {
            result = append(result, n)
        }
    }
    return result
}

evens := filter([]int{1, 2, 3, 4, 5}, func(n int) bool {
    return n%2 == 0
})
```

### Closures

Functions that capture variables from their enclosing scope:

```go
func counter() func() int {
    n := 0
    return func() int {
        n++
        return n
    }
}

c := counter()
c()  // 1
c()  // 2
c()  // 3

// Loop variable capture — pre-Go 1.22 pitfall
fns := make([]func(), 5)
for i := 0; i < 5; i++ {
    i := i  // shadow i — required pre-Go 1.22
    fns[i] = func() { fmt.Println(i) }
}
// Without `i := i` (pre-1.22): all fns print 5 (the final loop value)
// Go 1.22+: loop variables are per-iteration automatically — `i := i` no longer needed
```

### init Functions

Each package can have one or more `init()` functions. They run after all variable declarations, before `main()`. Used for registration patterns and side-effect setup.

```go
func init() {
    log.SetFlags(log.LstdFlags | log.Lshortfile)
}
```

---

## 5. Pointers

Go has pointers but no pointer arithmetic. They're used to pass values by reference (mutability) and to avoid copying large structs.

```go
x := 42
p := &x        // p is *int — a pointer to x
fmt.Println(*p) // dereference: prints 42
*p = 100        // mutate x through the pointer
fmt.Println(x)  // 100

// new() allocates zeroed memory and returns a pointer
p2 := new(int)  // *int pointing to 0
*p2 = 5
```

**When to use pointers:**

1. Mutate the original value in a function
2. Avoid copying large structs (pass `*BigStruct` not `BigStruct`)
3. Represent optional/nullable values (nil pointer = absent)

```go
// Method with pointer receiver can mutate the struct
func (u *User) SetEmail(email string) {
    u.Email = email
}

// Method with value receiver gets a copy
func (u User) FullName() string {
    return u.First + " " + u.Last
}
```

**Nil pointer dereference** is a runtime panic. Always check if a pointer is nil before dereferencing.

---

# Part 2: Composite Types

---

## 6. Arrays & Slices

### Arrays

Fixed-length. Rarely used directly — slices are almost always preferred.

```go
var a [3]int          // [0, 0, 0]
b := [3]int{1, 2, 3}
c := [...]int{4, 5, 6} // length inferred

// Arrays are values — assignment copies the whole array
d := b
d[0] = 99  // doesn't change b
```

### Slices

Dynamic-length view into an underlying array. The most important Go data structure.

```go
// Create
s := []int{1, 2, 3}
s2 := make([]int, 3)        // len=3, cap=3, all zeros
s3 := make([]int, 0, 10)    // len=0, cap=10 — pre-allocate

// Append
s = append(s, 4, 5)
s = append(s, []int{6, 7}...)  // spread

// Slicing (shares underlying array)
a := []int{0, 1, 2, 3, 4}
b := a[1:3]   // [1, 2] — includes index 1, excludes 3
c := a[:2]    // [0, 1]
d := a[2:]    // [2, 3, 4]

// len vs cap
s := make([]int, 3, 10)
fmt.Println(len(s), cap(s))  // 3, 10
```

**Slice internals:** A slice is a struct with three fields: `{pointer, len, cap}`. Slicing creates a new slice header pointing to the same underlying array. Appending beyond capacity allocates a new array (usually 2x growth).

```go
// copy — prevents aliasing when you need an independent slice
src := []int{1, 2, 3}
dst := make([]int, len(src))
copy(dst, src)
dst[0] = 99  // doesn't affect src
```

**2D slice:**

```go
matrix := make([][]int, rows)
for i := range matrix {
    matrix[i] = make([]int, cols)
}
```

**Delete element at index i (order-preserving):**

```go
s = append(s[:i], s[i+1:]...)
```

**Delete without preserving order (faster):**

```go
s[i] = s[len(s)-1]
s = s[:len(s)-1]
```

---

## 7. Maps

Hash maps. Keys must be comparable (no slices or maps as keys).

```go
// Create
m := map[string]int{}
m2 := make(map[string]int)

// Set
m["alice"] = 42
m["bob"] = 7

// Get
val := m["alice"]       // 42
val, ok := m["charlie"] // val=0, ok=false (zero value if absent)

// Delete
delete(m, "alice")

// Iterate (order is random each time)
for k, v := range m {
    fmt.Printf("%s: %d\n", k, v)
}

// Length
fmt.Println(len(m))
```

**Important:** Reading a missing key returns the zero value — no panic. Always use the two-value form when you need to distinguish "missing" from "zero":

```go
count, ok := m["key"]
if !ok {
    // key not present
}
```

**Maps are reference types.** Assigning a map to a variable copies the header (pointer) — both variables point to the same map.

**Concurrent access is NOT safe.** Use `sync.RWMutex` or `sync.Map` for concurrent access.

---

## 8. Structs

```go
type User struct {
    ID        int
    Email     string
    CreatedAt time.Time
    Address   *Address  // pointer — optional/nullable
}

// Instantiate
u := User{
    ID:    1,
    Email: "alice@example.com",
}

// Field access
fmt.Println(u.Email)
u.ID = 2

// Struct literal without field names (fragile — avoid)
u2 := User{1, "bob@example.com", time.Now(), nil}

// Anonymous struct (useful for JSON decoding one-offs)
resp := struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}{}
```

### Struct Tags

Used by reflection-based libraries (JSON, database, validation):

```go
type Product struct {
    ID    int    `json:"id"    db:"id"`
    Name  string `json:"name"  db:"name" validate:"required,min=1"`
    Price float64 `json:"price" db:"price"`
    // '-' means omit from JSON
    Internal string `json:"-"`
    // omitempty — skip field if zero value
    Description string `json:"description,omitempty"`
}
```

### Struct Comparison

Structs are comparable if all fields are comparable:

```go
type Point struct{ X, Y int }
p1 := Point{1, 2}
p2 := Point{1, 2}
fmt.Println(p1 == p2)  // true
```

---

# Part 3: Interfaces & Methods

---

## 9. Methods

Methods are functions with a receiver. The receiver is the first argument, written before the function name.

```go
type Rectangle struct {
    Width, Height float64
}

// Value receiver — gets a copy
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// Pointer receiver — can mutate
func (r *Rectangle) Scale(factor float64) {
    r.Width *= factor
    r.Height *= factor
}

rect := Rectangle{10, 5}
fmt.Println(rect.Area())  // 50
rect.Scale(2)
fmt.Println(rect.Area())  // 200
```

**Rule:** Use pointer receivers consistently on a type. Mixing value and pointer receivers for methods on the same type is valid but confusing.

**Calling:** Go auto-takes the address when calling a pointer-receiver method on an addressable value:
```go
rect.Scale(2)      // equivalent to (&rect).Scale(2)
```

---

## 10. Interfaces

An interface is a set of method signatures. A type implicitly satisfies an interface by implementing its methods — no `implements` keyword.

```go
type Shape interface {
    Area() float64
    Perimeter() float64
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

// Circle satisfies Shape — implicitly
func printShape(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\n", s.Area(), s.Perimeter())
}

printShape(Circle{5})
```

### Key Interfaces from stdlib

```go
// io.Reader — any type that can be read
type Reader interface {
    Read(p []byte) (n int, err error)
}

// io.Writer — any type that can be written to
type Writer interface {
    Write(p []byte) (n int, err error)
}

// io.Closer
type Closer interface {
    Close() error
}

// error
type error interface {
    Error() string
}

// fmt.Stringer — controls how a type is printed
type Stringer interface {
    String() string
}
```

### Empty Interface

`interface{}` (or `any` since Go 1.18) accepts any type. Avoid — loses type safety. Use generics instead where possible.

```go
func print(v any) {
    fmt.Println(v)
}
```

### Interface Values

An interface value has two components: `(type, value)`. A nil interface has both components nil. An interface holding a nil pointer is **not** nil:

```go
var s Shape                // nil interface: (nil, nil) — s == nil is true
var c *Circle              // nil pointer
s = c                      // s is now (Circle, nil) — s == nil is FALSE
```

This is the notorious "nil interface is not nil" gotcha.

---

## 11. Type Assertions & Type Switches

### Type Assertion

Extract the concrete type from an interface value:

```go
var s Shape = Circle{Radius: 5}

c, ok := s.(Circle)
if ok {
    fmt.Println("It's a circle with radius", c.Radius)
}

// Without ok — panics if wrong type
c2 := s.(Circle)
```

### Type Switch

```go
func describe(i interface{}) string {
    switch v := i.(type) {
    case int:
        return fmt.Sprintf("int: %d", v)
    case string:
        return fmt.Sprintf("string: %q", v)
    case []int:
        return fmt.Sprintf("[]int of length %d", len(v))
    case nil:
        return "nil"
    default:
        return fmt.Sprintf("unknown type: %T", v)
    }
}
```

---

## 12. Embedding

Go doesn't have inheritance but uses composition via embedding. Embedding promotes fields and methods.

```go
type Animal struct {
    Name string
}

func (a Animal) Speak() string {
    return a.Name + " speaks"
}

type Dog struct {
    Animal        // embedded — Dog gets Animal's fields and methods
    Breed string
}

d := Dog{
    Animal: Animal{Name: "Rex"},
    Breed:  "Labrador",
}
fmt.Println(d.Name)    // promoted field
fmt.Println(d.Speak()) // promoted method
```

**Interface embedding:**

```go
type ReadWriter interface {
    io.Reader
    io.Writer
}
```

**Method override:**

```go
func (d Dog) Speak() string {
    return d.Name + " barks"  // overrides Animal.Speak
}

d.Speak()         // "Rex barks"
d.Animal.Speak()  // "Rex speaks" — access embedded method directly
```

---

# Part 4: Error Handling

---

## 13. Errors as Values

In Go, errors are ordinary values — there's no exception mechanism. Functions return an `error` as their last return value.

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    log.Fatal(err)
}
fmt.Println(result)
```

**Convention:** Always check errors immediately. Never use `_` to discard an error unless you've thought about it.

```go
// Sentinel errors — predefined error values for comparison
var ErrNotFound = errors.New("not found")
var ErrTimeout = errors.New("timeout")

// Caller can compare
if err == ErrNotFound { ... }

// Since Go 1.13, prefer errors.Is for wrapped errors (see Section 14)
if errors.Is(err, ErrNotFound) { ... }
```

---

## 14. Custom Errors & Wrapping

### Custom Error Types

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on %s: %s", e.Field, e.Message)
}

// Caller can extract details
var ve *ValidationError
if errors.As(err, &ve) {
    fmt.Println("Invalid field:", ve.Field)
}
```

### Error Wrapping (Go 1.13+)

Use `%w` verb with `fmt.Errorf` to wrap an error while preserving the original.

```go
func fetchUser(id int) (*User, error) {
    user, err := db.QueryUser(id)
    if err != nil {
        return nil, fmt.Errorf("fetchUser %d: %w", id, err)
    }
    return user, nil
}
```

**Unwrapping:**

```go
// errors.Is — checks if any error in the chain matches the target
if errors.Is(err, sql.ErrNoRows) { ... }

// errors.As — extracts a specific error type from the chain
var pgErr *pgconn.PgError
if errors.As(err, &pgErr) {
    fmt.Println("PG code:", pgErr.Code)
}

// errors.Unwrap — get the next error in the chain
cause := errors.Unwrap(err)
```

### Error Handling Patterns

```go
// Early return pattern (most common)
func processOrder(id int) error {
    order, err := getOrder(id)
    if err != nil {
        return fmt.Errorf("processOrder: %w", err)
    }

    if err := validateOrder(order); err != nil {
        return fmt.Errorf("processOrder validate: %w", err)
    }

    return saveOrder(order)
}

// Sentinel error for expected "not found" — don't wrap as fatal
func getFromCache(key string) ([]byte, error) {
    v, ok := cache[key]
    if !ok {
        return nil, ErrCacheMiss  // caller decides what to do
    }
    return v, nil
}
```

---

## 15. Panic & Recover

Panic is for unrecoverable situations (programmer errors, invariant violations). It unwinds the stack and terminates the program unless recovered.

```go
// Trigger a panic
panic("this should never happen")

// Recover — must be called inside a deferred function
func safeDiv(a, b int) (result int, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic: %v", r)
        }
    }()
    result = a / b  // panics on b == 0
    return
}
```

**Rule:** Don't use panic for normal error handling. Use it for:
- Package initialization failures (in `init()`)
- Invariants that mean the program is corrupted
- Never across package boundaries (convert panic to error at your package boundary)

---

# Part 5: Concurrency

---

## 16. Goroutines

A goroutine is a lightweight thread managed by the Go runtime. Creating one is cheap (~2KB stack, grows as needed).

```go
go func() {
    fmt.Println("I run concurrently")
}()

// With a named function
go processRequest(req)

// The main goroutine doesn't wait — use sync mechanisms
func main() {
    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            fmt.Println("Worker", id)
        }(i)
    }
    wg.Wait()
}
```

**GOMAXPROCS:** Controls how many OS threads run goroutines in parallel. Default is the number of CPU cores.

---

## 17. Channels

Channels are typed conduits for communication between goroutines. They enforce synchronization.

```go
// Unbuffered channel — sender blocks until receiver is ready
ch := make(chan int)
go func() { ch <- 42 }()
val := <-ch

// Buffered channel — sender blocks only when buffer is full
ch2 := make(chan string, 10)
ch2 <- "hello"  // doesn't block (buffer has space)

// Directional channels — restrict usage
func producer(out chan<- int) {
    out <- 1
}
func consumer(in <-chan int) {
    v := <-in
    fmt.Println(v)
}

// Close a channel — signals no more values
close(ch)

// Range over channel — exits when channel is closed
for v := range ch {
    fmt.Println(v)
}

// Check if channel is closed
v, ok := <-ch
if !ok {
    fmt.Println("channel closed")
}
```

**Rules:**
- Only the **sender** should close a channel
- Sending to a closed channel panics
- Receiving from a closed channel returns zero value immediately
- Closing an already-closed channel panics

---

## 18. Select

`select` waits on multiple channel operations — whichever is ready first runs.

```go
select {
case msg := <-ch1:
    fmt.Println("from ch1:", msg)
case msg := <-ch2:
    fmt.Println("from ch2:", msg)
case ch3 <- "hello":
    fmt.Println("sent to ch3")
default:
    fmt.Println("no channel ready")  // non-blocking
}

// Timeout pattern
select {
case result := <-computeCh:
    fmt.Println("got:", result)
case <-time.After(5 * time.Second):
    fmt.Println("timed out")
}

// Done signal pattern (with context)
select {
case <-ctx.Done():
    return ctx.Err()
case result := <-work:
    return result
}
```

---

## 19. sync Package

### WaitGroup

Wait for a collection of goroutines to finish:

```go
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        process(n)
    }(i)
}
wg.Wait()  // blocks until all Done() calls
```

### Mutex & RWMutex

```go
type SafeCounter struct {
    mu sync.Mutex
    v  map[string]int
}

func (c *SafeCounter) Inc(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.v[key]++
}

// RWMutex: multiple readers OR one writer
type Cache struct {
    mu   sync.RWMutex
    data map[string]string
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    v, ok := c.data[key]
    return v, ok
}

func (c *Cache) Set(key, val string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.data[key] = val
}
```

### Once

Execute a function exactly once, even across goroutines:

```go
var once sync.Once
var instance *DB

func GetDB() *DB {
    once.Do(func() {
        instance = connectDB()
    })
    return instance
}
```

### sync.Map

Thread-safe map. Prefer `map + RWMutex` for most use cases. `sync.Map` is optimized for write-once-read-many or key sets that don't overlap between goroutines.

```go
var m sync.Map

m.Store("key", "value")

val, ok := m.Load("key")

m.Delete("key")

m.Range(func(k, v any) bool {
    fmt.Println(k, v)
    return true  // return false to stop iteration
})
```

### Cond

Condition variable — signal goroutines waiting on a condition:

```go
var mu sync.Mutex
cond := sync.NewCond(&mu)

// Waiter
mu.Lock()
for !ready {
    cond.Wait()  // releases lock, waits for signal, re-acquires lock
}
mu.Unlock()

// Signaler
mu.Lock()
ready = true
cond.Signal()   // wake one waiter
// or cond.Broadcast() — wake all waiters
mu.Unlock()
```

---

## 20. Context Package

Context carries deadlines, cancellation signals, and request-scoped values across API boundaries. Every long-running or blocking operation should accept a context.

```go
// Creating contexts
ctx := context.Background()  // root context — never cancelled
ctx2 := context.TODO()       // placeholder when unsure

// Cancellation
ctx, cancel := context.WithCancel(context.Background())
defer cancel()  // always call cancel to free resources

// Deadline
ctx, cancel := context.WithDeadline(ctx, time.Now().Add(5*time.Second))
defer cancel()

// Timeout (shorthand for WithDeadline)
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

// Values — for request-scoped data (not for passing function parameters)
type contextKey string
const userKey contextKey = "user"

ctx = context.WithValue(ctx, userKey, user)
u := ctx.Value(userKey).(*User)
```

**Checking cancellation:**

```go
func doWork(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()  // context.Canceled or context.DeadlineExceeded
        default:
            // do some work
        }
    }
}
```

**Pass context to all blocking calls:**

```go
// HTTP request with context
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := http.DefaultClient.Do(req)

// DB query with context
row := db.QueryRowContext(ctx, "SELECT * FROM users WHERE id = $1", id)
```

**Rules:**
- Context is the **first parameter** by convention: `func f(ctx context.Context, ...)`
- Never store context in a struct
- Don't pass nil — use `context.Background()` or `context.TODO()`

---

## 21. Concurrency Patterns

### Pipeline

Chain goroutines where each stage transforms data:

```go
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// Usage
for v := range square(generate(1, 2, 3, 4)) {
    fmt.Println(v)  // 1 4 9 16
}
```

### Fan-Out / Fan-In

Fan-out: distribute work across multiple goroutines.
Fan-in: merge multiple channels into one.

```go
func merge(cs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)

    output := func(c <-chan int) {
        for v := range c {
            out <- v
        }
        wg.Done()
    }

    wg.Add(len(cs))
    for _, c := range cs {
        go output(c)
    }

    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### Worker Pool

```go
func workerPool(jobs <-chan int, results chan<- int, numWorkers int) {
    var wg sync.WaitGroup
    for w := 0; w < numWorkers; w++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    go func() {
        wg.Wait()
        close(results)
    }()
}
```

### Done Channel Pattern

Signal goroutines to stop:

```go
done := make(chan struct{})
defer close(done)

go func() {
    for {
        select {
        case <-done:
            return
        case work := <-jobs:
            process(work)
        }
    }
}()
```

### errgroup

`golang.org/x/sync/errgroup` — run goroutines and collect the first error:

```go
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(context.Background())

g.Go(func() error {
    return fetchA(ctx)
})
g.Go(func() error {
    return fetchB(ctx)
})

if err := g.Wait(); err != nil {
    log.Fatal(err)
}
```

---

# Part 6: Generics (Go 1.18+)

---

## 22. Type Parameters & Constraints

Generics allow writing functions and types that work across multiple types while remaining type-safe.

```go
// Generic function
func Map[T, U any](slice []T, f func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = f(v)
    }
    return result
}

doubled := Map([]int{1, 2, 3}, func(n int) int { return n * 2 })
lengths := Map([]string{"hello", "world"}, func(s string) int { return len(s) })
```

### Constraints

Constraints restrict what types can be used as type parameters:

```go
// cmp.Ordered — built-in since Go 1.21 (use this, not golang.org/x/exp/constraints)
import "cmp"

func Min[T cmp.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// Custom constraint
type Number interface {
    int | int8 | int16 | int32 | int64 |
        float32 | float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// ~T — includes all types whose underlying type is T
type Integer interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64
}
```

### Generic Types

```go
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(v T) {
    s.items = append(s.items, v)
}

func (s *Stack[T]) Pop() (T, bool) {
    var zero T
    if len(s.items) == 0 {
        return zero, false
    }
    top := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return top, true
}

s := Stack[int]{}
s.Push(1)
s.Push(2)
v, _ := s.Pop()  // v == 2
```

---

# Part 7: Testing

---

## 23. Unit Tests & Table-Driven Tests

Go's testing is built in — no external framework needed for most cases.

```go
// File: math_test.go
package math

import "testing"

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("Add(2, 3) = %d, want %d", got, want)
    }
}
```

### Table-Driven Tests (the Go standard)

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    float64
        want    float64
        wantErr bool
    }{
        {"positive", 10, 2, 5, false},
        {"negative", -6, 3, -2, false},
        {"divide by zero", 5, 0, 0, true},
        {"fractional", 7, 2, 3.5, false},
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            got, err := Divide(tc.a, tc.b)
            if (err != nil) != tc.wantErr {
                t.Errorf("Divide(%v, %v) error = %v, wantErr %v", tc.a, tc.b, err, tc.wantErr)
                return
            }
            if !tc.wantErr && got != tc.want {
                t.Errorf("Divide(%v, %v) = %v, want %v", tc.a, tc.b, got, tc.want)
            }
        })
    }
}
```

### Running Tests

```bash
go test ./...                    # run all tests
go test -run TestDivide ./...   # run specific test
go test -v ./...                 # verbose output
go test -race ./...              # race condition detection (always run in CI)
go test -count=1 ./...          # disable test caching
```

### Subtests and Setup/Teardown

```go
func TestDB(t *testing.T) {
    db := setupTestDB(t)
    t.Cleanup(func() { db.Close() })  // runs after test (or subtest) completes

    t.Run("insert", func(t *testing.T) {
        // ...
    })
    t.Run("query", func(t *testing.T) {
        // ...
    })
}
```

---

## 24. Benchmarks & Profiling

```go
func BenchmarkFibonacci(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Fibonacci(20)
    }
}

// With setup time excluded
func BenchmarkExpensive(b *testing.B) {
    data := generateLargeData()  // not counted
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

```bash
go test -bench=. -benchmem ./...
# -benchmem shows allocations per op
```

### Profiling

```bash
go test -bench=. -cpuprofile=cpu.prof ./...
go tool pprof cpu.prof
# then: web, top, list FunctionName

go test -bench=. -memprofile=mem.prof ./...
go tool pprof mem.prof
```

---

## 25. Test Helpers & Mocking

### testify (popular third-party)

```go
import (
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestSomething(t *testing.T) {
    result, err := doWork()
    require.NoError(t, err)         // stops test on failure
    assert.Equal(t, "expected", result)
    assert.Contains(t, result, "sub")
    assert.Nil(t, something)
    assert.True(t, condition)
}
```

### Mocking with Interfaces

The idiomatic Go way: define an interface, implement a fake for tests:

```go
// Production code
type UserRepo interface {
    FindByID(ctx context.Context, id int) (*User, error)
    Save(ctx context.Context, user *User) error
}

type UserService struct {
    repo UserRepo
}

// Test fake
type fakeUserRepo struct {
    users map[int]*User
    err   error
}

func (f *fakeUserRepo) FindByID(_ context.Context, id int) (*User, error) {
    if f.err != nil {
        return nil, f.err
    }
    return f.users[id], nil
}

func (f *fakeUserRepo) Save(_ context.Context, u *User) error {
    f.users[u.ID] = u
    return f.err
}

func TestUserService_Get(t *testing.T) {
    repo := &fakeUserRepo{
        users: map[int]*User{1: {ID: 1, Name: "Alice"}},
    }
    svc := UserService{repo: repo}
    u, err := svc.Get(context.Background(), 1)
    require.NoError(t, err)
    assert.Equal(t, "Alice", u.Name)
}
```

### mockery (code-gen mocks)

```bash
go install github.com/vektra/mockery/v2@latest
mockery --name=UserRepo --output=mocks
```

---

# Part 8: Standard Library

---

## 26. fmt, strings, strconv, unicode

### fmt

```go
// Print
fmt.Print("no newline")
fmt.Println("with newline")
fmt.Printf("formatted %s %d %.2f\n", "hello", 42, 3.14)

// Sprintf — return string
s := fmt.Sprintf("Hello, %s", name)

// Fprintf — write to io.Writer
fmt.Fprintf(os.Stderr, "Error: %v\n", err)

// Errorf — create error
err := fmt.Errorf("failed to open %s: %w", path, cause)

// Verbs
%v   // default format
%+v  // struct with field names
%#v  // Go syntax representation
%T   // type
%d   // decimal integer
%x   // hex
%f   // float
%e   // scientific notation
%s   // string
%q   // quoted string
%p   // pointer
%t   // bool
```

### strings

```go
import "strings"

strings.Contains("hello", "ell")        // true
strings.HasPrefix("hello", "he")        // true
strings.HasSuffix("hello", "lo")        // true
strings.Index("hello", "ll")            // 2
strings.Count("cheese", "e")            // 3
strings.Replace("oink oink", "oink", "moo", 1) // "moo oink"
strings.ReplaceAll("oink oink", "oink", "moo") // "moo moo"
strings.ToUpper("hello")                // "HELLO"
strings.ToLower("HELLO")                // "hello"
strings.TrimSpace("  hi  ")            // "hi"
strings.Trim("###hi###", "#")          // "hi"
strings.TrimLeft / TrimRight
strings.Split("a,b,c", ",")            // ["a", "b", "c"]
strings.Join([]string{"a","b"}, "-")   // "a-b"
strings.Fields("  foo bar ")           // ["foo", "bar"]
strings.Repeat("ab", 3)                // "ababab"
strings.Title("hello world")           // deprecated — use golang.org/x/text

// Builder — efficient string concatenation
var sb strings.Builder
for _, s := range words {
    sb.WriteString(s)
    sb.WriteByte(' ')
}
result := sb.String()
```

### strconv

```go
import "strconv"

// int ↔ string
s := strconv.Itoa(42)          // "42"
n, err := strconv.Atoi("42")  // 42, nil

// float
f, err := strconv.ParseFloat("3.14", 64)
s2 := strconv.FormatFloat(3.14, 'f', 2, 64)  // "3.14"

// bool
b, err := strconv.ParseBool("true")  // true, nil
s3 := strconv.FormatBool(true)       // "true"

// int with base
n64, err := strconv.ParseInt("ff", 16, 64)  // 255
```

---

## 27. os, io, bufio, filepath

### os

```go
import "os"

// Files
f, err := os.Open("file.txt")           // read-only
f2, err := os.Create("out.txt")         // create/truncate
f3, err := os.OpenFile("log.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
defer f.Close()

// Read entire file
data, err := os.ReadFile("file.txt")    // returns []byte
err = os.WriteFile("out.txt", data, 0644)

// Environment
val := os.Getenv("HOME")
os.Setenv("KEY", "value")
envs := os.Environ()  // []"KEY=VALUE"

// Args
args := os.Args  // os.Args[0] is binary name

// Exit
os.Exit(1)  // immediate exit, defers don't run

// Stderr
fmt.Fprintln(os.Stderr, "error message")
```

### io

```go
import "io"

// Copy
n, err := io.Copy(dst, src)  // dst io.Writer, src io.Reader

// Read all
data, err := io.ReadAll(r)  // reads until EOF

// Discard
io.Copy(io.Discard, resp.Body)  // consume and discard

// Pipe
pr, pw := io.Pipe()  // connected io.Reader and io.Writer (blocking)

// LimitReader
limited := io.LimitReader(r, maxBytes)

// TeeReader — write to w while reading from r
tee := io.TeeReader(r, w)
```

### bufio

```go
import "bufio"

// Buffered reading
scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Text()
    fmt.Println(line)
}
if err := scanner.Err(); err != nil {
    log.Fatal(err)
}

// Custom split function
scanner.Split(bufio.ScanWords)  // or ScanLines, ScanBytes, ScanRunes

// Buffered writer
w := bufio.NewWriter(file)
w.WriteString("hello\n")
w.Flush()  // must flush!
```

### filepath

```go
import "path/filepath"

filepath.Join("dir", "sub", "file.txt")  // dir/sub/file.txt
filepath.Dir("/a/b/c.txt")               // /a/b
filepath.Base("/a/b/c.txt")              // c.txt
filepath.Ext("/a/b/c.txt")               // .txt
filepath.Abs("relative/path")           // absolute path
// filepath.WalkDir (Go 1.16+) is preferred — avoids the os.FileInfo stat call on every entry
filepath.WalkDir(".", func(path string, d fs.DirEntry, err error) error {
    if err != nil { return err }
    fmt.Println(path, d.IsDir())
    return nil
})

// filepath.Walk still works but allocates os.FileInfo for every entry (slower)
filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
    if err != nil { return err }
    fmt.Println(path)
    return nil
})
```

---

## 28. time

```go
import "time"

// Current time
now := time.Now()

// Durations
d := 5 * time.Second
d2 := 500 * time.Millisecond
d3 := 2*time.Hour + 30*time.Minute

// Sleep
time.Sleep(1 * time.Second)

// Timer (fire once)
timer := time.NewTimer(2 * time.Second)
<-timer.C  // blocks until timer fires
timer.Stop()

// Ticker (fire repeatedly)
ticker := time.NewTicker(500 * time.Millisecond)
defer ticker.Stop()
for tick := range ticker.C {
    fmt.Println("tick at", tick)
}

// time.After (sugar for timer — not for high-frequency use, leaks)
select {
case <-time.After(5 * time.Second):
    fmt.Println("timed out")
}

// Formatting & parsing
t := time.Now()
s := t.Format("2006-01-02 15:04:05")        // Go uses this reference time
s2 := t.Format(time.RFC3339)               // 2006-01-02T15:04:05Z07:00
t2, err := time.Parse("2006-01-02", "2024-01-15")

// Arithmetic
future := now.Add(24 * time.Hour)
past := now.Add(-7 * 24 * time.Hour)
diff := future.Sub(now)  // time.Duration

// Comparison
if t.Before(deadline) { ... }
if t.After(start) { ... }
t.Equal(t2)

// Timezone
loc, _ := time.LoadLocation("America/New_York")
t.In(loc)
t.UTC()
```

**Note:** Go's reference time is `Mon Jan 2 15:04:05 MST 2006` — not arbitrary. The values 1-2-3-4-5-6-7 (month-day-hour-min-sec-year-tz offset).

---

## 29. net/http (Client & Server)

### HTTP Server

```go
import "net/http"

// Handler function
func helloHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    fmt.Fprintln(w, `{"message": "hello"}`)
}

// ServeMux (default router)
mux := http.NewServeMux()
mux.HandleFunc("GET /users", listUsers)      // Go 1.22+ method+path routing
mux.HandleFunc("POST /users", createUser)
mux.HandleFunc("/health", healthCheck)

// Start server
srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  120 * time.Second,
}
log.Fatal(srv.ListenAndServe())

// Middleware pattern
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

// Request body
func createUser(w http.ResponseWriter, r *http.Request) {
    defer r.Body.Close()
    var user User
    if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    // ...
}

// Path variables (Go 1.22+)
mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    // ...
})

// Query params
q := r.URL.Query()
name := q.Get("name")
```

### HTTP Client

```go
// Simple GET
resp, err := http.Get("https://api.example.com/data")
if err != nil {
    return err
}
defer resp.Body.Close()
body, err := io.ReadAll(resp.Body)

// With context and timeout
client := &http.Client{Timeout: 10 * time.Second}

ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(jsonData))
req.Header.Set("Content-Type", "application/json")
req.Header.Set("Authorization", "Bearer "+token)

resp, err := client.Do(req)
if err != nil {
    return fmt.Errorf("request failed: %w", err)
}
defer resp.Body.Close()

if resp.StatusCode != http.StatusOK {
    return fmt.Errorf("unexpected status: %d", resp.StatusCode)
}

var result Response
if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
    return fmt.Errorf("decode response: %w", err)
}
```

---

## 30. encoding/json

```go
import "encoding/json"

type User struct {
    ID       int    `json:"id"`
    Name     string `json:"name"`
    Email    string `json:"email,omitempty"`
    Password string `json:"-"`  // never serialized
}

// Marshal (Go → JSON)
data, err := json.Marshal(user)
data, err = json.MarshalIndent(user, "", "  ")  // pretty print

// Unmarshal (JSON → Go)
var u User
err = json.Unmarshal(data, &u)

// Streaming encode/decode (preferred for HTTP)
json.NewEncoder(w).Encode(user)
json.NewDecoder(r.Body).Decode(&user)

// Unknown structure — use map or json.RawMessage
var m map[string]interface{}
json.Unmarshal(data, &m)

// Delay parsing part of JSON
type Event struct {
    Type    string          `json:"type"`
    Payload json.RawMessage `json:"payload"`
}

// Custom marshaling
type Duration time.Duration

func (d Duration) MarshalJSON() ([]byte, error) {
    return json.Marshal(time.Duration(d).String())
}

func (d *Duration) UnmarshalJSON(b []byte) error {
    var s string
    if err := json.Unmarshal(b, &s); err != nil {
        return err
    }
    dur, err := time.ParseDuration(s)
    *d = Duration(dur)
    return err
}
```

---

## 31. sync/atomic & sync

### atomic

For lock-free operations on single values. Faster than mutex for simple counters:

```go
import "sync/atomic"

var counter int64

// Increment
atomic.AddInt64(&counter, 1)

// Load / Store
val := atomic.LoadInt64(&counter)
atomic.StoreInt64(&counter, 0)

// Compare and swap — CAS
swapped := atomic.CompareAndSwapInt64(&counter, old, new)

// atomic.Value — store any value atomically
var config atomic.Value
config.Store(cfg)
current := config.Load().(*Config)
```

### Pool

`sync.Pool` recycles temporary objects to reduce GC pressure:

```go
var bufPool = sync.Pool{
    New: func() any {
        return new(bytes.Buffer)
    },
}

func process(data []byte) string {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()
    // use buf ...
    return buf.String()
}
```

---

## 32. context (revisited with stdlib)

Common context usage patterns in the standard library:

```go
// HTTP server — request context is automatically cancelled when client disconnects
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    result, err := db.QueryContext(ctx, "SELECT ...")
    // if client disconnects, ctx is cancelled, query is aborted
}

// Propagate context through call chain
func GetUser(ctx context.Context, id int) (*User, error) {
    return db.QueryRowContext(ctx, "SELECT * FROM users WHERE id=$1", id).Scan(...)
}
```

---

## 33. sort, slices, maps (Go 1.21)

### sort (legacy, type-specific)

```go
import "sort"

nums := []int{5, 2, 8, 1}
sort.Ints(nums)                          // [1, 2, 5, 8]
sort.Strings([]string{"b", "a", "c"})  // [a, b, c]
sort.Float64s([]float64{...})

// Custom sort
sort.Slice(users, func(i, j int) bool {
    return users[i].Name < users[j].Name
})

// Stable sort (preserves relative order of equal elements)
sort.SliceStable(users, func(i, j int) bool {
    return users[i].Age < users[j].Age
})

// Search — binary search (slice must be sorted)
i := sort.SearchInts(nums, 5)  // returns index where 5 is/would be
```

### slices package (Go 1.21)

```go
import "slices"

slices.Sort(nums)                        // generic sort
slices.SortFunc(users, func(a, b User) int {
    return strings.Compare(a.Name, b.Name)
})
slices.Contains(nums, 5)               // true/false
slices.Index(nums, 5)                  // index or -1
slices.Reverse(nums)                   // in-place
slices.Max(nums)                       // maximum value
slices.Min(nums)
slices.Equal(a, b)                     // element-wise equality
```

### maps package (Go 1.21)

```go
import "maps"

keys := maps.Keys(m)      // []K (unordered)
vals := maps.Values(m)    // []V (unordered)
maps.Copy(dst, src)       // copy src into dst
maps.Delete(m, func(k K, v V) bool { return condition })
maps.Equal(m1, m2)
```

---

# Part 9: Modules & Packages

---

## 34. Go Modules

Go modules are the standard dependency management system since Go 1.11.

```bash
# Initialize a new module
go mod init github.com/username/myproject

# Add a dependency (auto-run on import)
go get github.com/gin-gonic/gin@v1.9.1

# Update all dependencies to latest minor/patch
go get -u ./...

# Tidy — remove unused, add missing
go mod tidy

# Vendor dependencies (for reproducible builds without network)
go mod vendor

# Show module dependency graph
go mod graph

# Check for available updates
go list -m -u all
```

**go.mod:**
```
module github.com/username/myproject

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/stretchr/testify v1.8.4
)

require (
    // indirect dependencies
    github.com/bytedance/sonic v1.9.1 // indirect
)
```

**go.sum:** Cryptographic hashes of exact dependency versions. Always commit both `go.mod` and `go.sum`.

### Workspace Mode (Go 1.18+)

Work on multiple modules simultaneously without publishing:

```bash
go work init ./moduleA ./moduleB
go work use ./moduleC
```

---

## 35. Package Design

### Rules

- **One package per directory.** Package name = directory name (by convention).
- **Package name is lowercase, short, singular** — `http`, `sort`, `user`, not `httputils` or `users`.
- **Avoid `util`, `common`, `helpers`** — put code in a package that describes what it does, not that it's a helper.
- **Exported names start with uppercase.** Unexported stay in the package.
- **Circular imports are a compile error.** If A imports B and B imports A, restructure.

### Organizing Code

```
myapp/
├── cmd/
│   └── server/
│       └── main.go       // entry point — thin, just wires things up
├── internal/             // not importable outside this module
│   ├── user/
│   │   ├── user.go       // domain type
│   │   ├── service.go    // business logic
│   │   └── repo.go       // data access interface
│   └── auth/
├── pkg/                  // public API other modules can import
└── go.mod
```

### internal Package

Code in `internal/` can only be imported by code in the parent directory:

```
github.com/user/myapp/internal/user  // importable by myapp, not by external modules
```

---

# Part 10: Patterns & Idioms

---

## 36. Functional Options Pattern

Cleanly handles optional configuration without complex constructors or config structs:

```go
type Server struct {
    host    string
    port    int
    timeout time.Duration
    maxConn int
}

type Option func(*Server)

func WithHost(host string) Option {
    return func(s *Server) { s.host = host }
}

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func NewServer(opts ...Option) *Server {
    s := &Server{
        host:    "localhost",  // defaults
        port:    8080,
        timeout: 30 * time.Second,
        maxConn: 100,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage — caller only specifies what they want to override
srv := NewServer(
    WithPort(9090),
    WithTimeout(60 * time.Second),
)
```

---

## 37. Error Handling Idioms

### Centralized Error Wrapping

```go
// Define a wrap helper to avoid repetition
func wrap(err error, msg string) error {
    if err == nil { return nil }
    return fmt.Errorf("%s: %w", msg, err)
}

func processOrder(id int) error {
    order, err := fetchOrder(id)
    if err != nil {
        return wrap(err, "fetchOrder")
    }
    // ...
}
```

### Error Groups for Multiple Independent Errors

```go
type MultiError struct {
    errors []error
}

func (m *MultiError) Add(err error) {
    if err != nil {
        m.errors = append(m.errors, err)
    }
}

func (m *MultiError) Err() error {
    if len(m.errors) == 0 {
        return nil
    }
    return m
}

func (m *MultiError) Error() string {
    msgs := make([]string, len(m.errors))
    for i, e := range m.errors {
        msgs[i] = e.Error()
    }
    return strings.Join(msgs, "; ")
}
```

### Retry with Backoff

```go
func retry(ctx context.Context, maxAttempts int, f func() error) error {
    var err error
    for attempt := 0; attempt < maxAttempts; attempt++ {
        if attempt > 0 {
            backoff := time.Duration(attempt) * 100 * time.Millisecond
            select {
            case <-time.After(backoff):
            case <-ctx.Done():
                return ctx.Err()
            }
        }
        if err = f(); err == nil {
            return nil
        }
    }
    return fmt.Errorf("after %d attempts: %w", maxAttempts, err)
}
```

---

## 38. Common Pitfalls

### 1. Goroutine Leak

Goroutines that never terminate hold memory forever:

```go
// Leak — nothing closes the done channel
func leak() {
    ch := make(chan int)
    go func() {
        for v := range ch {  // stuck forever if ch never closed/receives
            fmt.Println(v)
        }
    }()
}

// Fix — use context or a done channel
func noLeak(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return
            case v := <-ch:
                fmt.Println(v)
            }
        }
    }()
}
```

### 2. Range Variable Capture (pre-Go 1.22)

```go
// Bug (pre-Go 1.22) — all goroutines capture the same v variable
for _, v := range items {
    go func() {
        fmt.Println(v)  // prints the last value of v, N times
    }()
}

// Fix (pre-Go 1.22) — shadow the loop variable
for _, v := range items {
    v := v  // new variable per iteration
    go func() {
        fmt.Println(v)
    }()
}
// Go 1.22+ fix: loop variables are per-iteration — the bug above no longer exists.
// The `v := v` workaround is safe to write but unnecessary on 1.22+.
```

### 3. Nil Map Write

```go
var m map[string]int
m["key"] = 1  // panic: assignment to entry in nil map

// Fix
m := make(map[string]int)
m["key"] = 1
```

### 4. Slice Aliasing After Append

```go
a := []int{1, 2, 3}
b := a[:2]   // shares underlying array
b = append(b, 99)  // if cap(a) > 2, modifies a[2]!

// Fix — use copy when you need independence
b := make([]int, 2)
copy(b, a[:2])
```

### 5. Using time.After in Hot Paths

`time.After` allocates a timer that isn't GC'd until it fires:

```go
// Leak in a hot loop
for {
    select {
    case <-time.After(1 * time.Second):  // new timer every iteration
    case msg := <-ch:
        process(msg)
    }
}

// Fix
ticker := time.NewTicker(1 * time.Second)
defer ticker.Stop()
for {
    select {
    case <-ticker.C:
    case msg := <-ch:
        process(msg)
    }
}
```

### 6. Defer in Loop

```go
// Defers pile up — file handles leak until function returns
for _, path := range paths {
    f, _ := os.Open(path)
    defer f.Close()  // all defers run at function end, not loop end
}

// Fix — use a function or close explicitly
for _, path := range paths {
    func() {
        f, _ := os.Open(path)
        defer f.Close()  // runs when anonymous function returns
        process(f)
    }()
}
```

### 7. Interface Nil Pitfall

```go
func getError() error {
    var p *PathError  // nil pointer
    return p          // returns non-nil error interface!
}

// Fix — return untyped nil
func getError() error {
    var p *PathError
    if p == nil { return nil }
    return p
}
```

---

## 39. Performance Notes

### Memory Allocation

- Avoid heap allocations in hot paths — prefer stack allocation
- Pre-allocate slices with `make([]T, 0, knownLen)` to avoid repeated copies
- Use `sync.Pool` for reusing temporary objects
- Prefer value receivers for small, frequently-called methods (no pointer indirection)

### String Concatenation

```go
// Slow — allocates a new string each +
s := ""
for _, word := range words {
    s += word + " "
}

// Fast — single allocation
var sb strings.Builder
sb.Grow(estimatedLen)
for _, word := range words {
    sb.WriteString(word)
    sb.WriteByte(' ')
}
s := sb.String()
```

### Profiling Workflow

```bash
# CPU profile from a running server
import _ "net/http/pprof"  // registers /debug/pprof handlers

go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
# Then: top, list FunctionName, web
```

### escape analysis

```bash
go build -gcflags="-m" ./...
# Shows which variables escape to heap ("x escapes to heap")
```

### Compiler Optimizations

- **Inlining:** Small functions are inlined automatically. Large functions won't be.
- **Bounds check elimination:** Compiler removes redundant bounds checks in tight loops.
- **SIMD:** `go build -gcflags="-d=ssa/check_bce/debug=1"` to see bounds check elimination.

---

# Part 11: Stdlib — Additional Packages

---

## 40. log/slog (Go 1.21+)

`slog` is the structured logging standard for Go. Prefer it over the `log` package for any non-trivial project.

```go
import "log/slog"

// Default logger (writes JSON to stderr)
slog.Info("server started", "port", 8080)
slog.Error("request failed", "err", err, "user_id", 42)
slog.Warn("rate limit approaching", "remaining", 5)

// Structured JSON output:
// {"time":"...","level":"INFO","msg":"server started","port":8080}
```

### Creating a Custom Logger

```go
// JSON handler (production)
logger := slog.New(slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{
    Level: slog.LevelInfo,  // filter below this level
}))

// Text handler (development — human-readable)
logger = slog.New(slog.NewTextHandler(os.Stdout, nil))

// Set as default (replaces slog.Info/Error/... calls)
slog.SetDefault(logger)
```

### Log Levels

`DEBUG < INFO < WARN < ERROR`. Set `Level: slog.LevelDebug` in dev, `LevelInfo` or `LevelWarn` in production.

### With Group / Context

```go
// Add common fields to every log from this logger
reqLogger := logger.With("request_id", reqID, "user_id", userID)
reqLogger.Info("processing order", "order_id", orderID)
// All fields: request_id, user_id, order_id, msg

// Group fields under a namespace
logger.Info("db stats",
    slog.Group("db",
        slog.Int("connections", 10),
        slog.Duration("avg_latency", 5*time.Millisecond),
    ),
)
// {"db":{"connections":10,"avg_latency":"5ms"}}
```

### Legacy log Package

```go
import "log"

log.Println("message")  // adds timestamp, writes to stderr
log.Fatalf("fatal: %v", err)  // calls os.Exit(1)
log.SetFlags(log.LstdFlags | log.Lshortfile)  // customize format
```

Use `log` only for simple scripts. Use `slog` for anything deployed.

---

## 41. regexp

```go
import "regexp"

// Compile — panics on invalid pattern (use in init/global)
re := regexp.MustCompile(`\d{4}-\d{2}-\d{2}`)

// Compile — returns error (use when pattern is dynamic)
re, err := regexp.Compile(`\d+`)

// Match
re.MatchString("2024-01-15")  // true

// Find first match
re.FindString("Order from 2024-01-15 total: 42")  // "2024"

// Find all matches
re.FindAllString("1 2 3", -1)  // ["1", "2", "3"]
// -1 means no limit; use n to get at most n matches

// Find with subgroups
re2 := regexp.MustCompile(`(\d{4})-(\d{2})-(\d{2})`)
matches := re2.FindStringSubmatch("2024-01-15")
// matches[0] = "2024-01-15" (full match)
// matches[1] = "2024", matches[2] = "01", matches[3] = "15"

// Named groups
re3 := regexp.MustCompile(`(?P<year>\d{4})-(?P<month>\d{2})`)
m := re3.FindStringSubmatch("2024-01")
year := m[re3.SubexpIndex("year")]  // "2024"

// Replace
re.ReplaceAllString("foo123bar456", "NUM")  // "fooNUMbarNUM"
re.ReplaceAllStringFunc("foo123", func(s string) string {
    return "[" + s + "]"
})

// Split
re.Split("one2three4five", -1)  // ["one", "three", "five"]
```

**Performance:** Compile regexps once at package level — `regexp.MustCompile` at package scope. Never compile inside a loop.

---

## 42. embed (Go 1.16)

Embed static files directly into the compiled binary. No more "file not found" errors in production.

```go
import (
    "embed"
    _ "embed"  // blank import required if only using //go:embed
)

// Embed a single file as a string
//go:embed version.txt
var version string

// Embed a single file as bytes
//go:embed config/default.json
var defaultConfig []byte

// Embed an entire directory as fs.FS
//go:embed static
var staticFiles embed.FS

// Use as http.FileServer
http.Handle("/static/", http.FileServer(http.FS(staticFiles)))

// Read a specific file from the embedded FS
data, err := staticFiles.ReadFile("static/index.html")

// Walk all embedded files
fs.WalkDir(staticFiles, ".", func(path string, d fs.DirEntry, err error) error {
    fmt.Println(path)
    return nil
})
```

**Rules:**
- The `//go:embed` directive must appear immediately before the variable declaration
- The path is relative to the Go source file containing the directive
- `embed.FS` is read-only
- Hidden files (starting with `.` or `_`) are excluded by default; use `all:` prefix to include them: `//go:embed all:static`

---

## 43. io/fs (Go 1.16)

`io/fs` defines a standard interface for read-only file systems. Lets you write code that works against the real OS filesystem, an embedded FS, a zip file, a test fixture, etc.

```go
import "io/fs"

// The core interface
type FS interface {
    Open(name string) (File, error)
}

// Additional optional interfaces a filesystem may implement
// fs.ReadFileFS, fs.ReadDirFS, fs.StatFS, fs.GlobFS, fs.SubFS

// Functions that accept any fs.FS
data, err := fs.ReadFile(myFS, "path/to/file")
entries, err := fs.ReadDir(myFS, ".")
info, err := fs.Stat(myFS, "file.txt")
matches, err := fs.Glob(myFS, "*.json")

// Sub — get a sub-tree as its own FS
subFS, err := fs.Sub(staticFiles, "static/css")

// WalkDir — walk any fs.FS
fs.WalkDir(myFS, ".", func(path string, d fs.DirEntry, err error) error {
    if err != nil { return err }
    if !d.IsDir() {
        fmt.Println(path)
    }
    return nil
})

// os.DirFS — wrap the real filesystem as an fs.FS
osFS := os.DirFS("/path/to/dir")
```

---

## 44. html/template & text/template

```go
import "html/template"  // always use this for HTML — auto-escapes to prevent XSS

// Parse a template string
tmpl := template.Must(template.New("page").Parse(`
<h1>{{.Title}}</h1>
<ul>
  {{range .Items}}<li>{{.}}</li>{{end}}
</ul>
`))

// Execute template to a writer
data := struct {
    Title string
    Items []string
}{
    Title: "My List",
    Items: []string{"apple", "banana"},
}
tmpl.Execute(w, data)  // w is an io.Writer (http.ResponseWriter, os.Stdout, etc.)

// Template from files
tmpl, err := template.ParseFiles("base.html", "content.html")
tmpl, err = template.ParseGlob("templates/*.html")

// Template functions
funcMap := template.FuncMap{
    "upper": strings.ToUpper,
    "join":  strings.Join,
}
tmpl = template.New("").Funcs(funcMap).Must(template.ParseFiles("tmpl.html"))
```

**html/template vs text/template:**
- `html/template`: context-aware auto-escaping — use for all HTML output
- `text/template`: no escaping — use for non-HTML text (config files, emails, code generation)

---

## 45. encoding/xml

```go
import "encoding/xml"

type Person struct {
    XMLName xml.Name `xml:"person"`
    Name    string   `xml:"name"`
    Age     int      `xml:"age,attr"`       // as attribute
    Address *Address `xml:"address"`
    Notes   string   `xml:",cdata"`         // CDATA section
    Ignored string   `xml:"-"`
}

// Marshal (Go → XML)
data, err := xml.Marshal(person)
data, err = xml.MarshalIndent(person, "", "  ")

// Unmarshal (XML → Go)
var p Person
err = xml.Unmarshal(data, &p)

// Streaming
encoder := xml.NewEncoder(w)
encoder.Encode(person)

decoder := xml.NewDecoder(r)
decoder.Decode(&p)
```

---

# Part 12: Tooling & Production

---

## 46. Build Tags & Cross-Compilation

### Build Tags (Build Constraints)

Control which files are included in a build. Placed at the top of the file before the package declaration.

```go
//go:build linux || darwin
// +build linux darwin  (old syntax, still valid, keep for compatibility)

package main
```

**Common uses:**
```go
//go:build !windows        // exclude from Windows builds
//go:build integration     // only include in integration test runs
//go:build go1.21          // only include if Go version >= 1.21
```

Run with tags:
```bash
go test -tags=integration ./...
go build -tags=production ./...
```

### Cross-Compilation

Go compiles to any target from any host — just set `GOOS` and `GOARCH`.

```bash
# Build for Linux AMD64 from macOS
GOOS=linux GOARCH=amd64 go build -o app-linux ./cmd/server

# Build for Windows
GOOS=windows GOARCH=amd64 go build -o app.exe ./cmd/server

# Build for ARM (Raspberry Pi)
GOOS=linux GOARCH=arm GOARM=7 go build -o app-pi ./cmd/server

# List all supported targets
go tool dist list
```

**Common GOOS values:** `linux`, `darwin`, `windows`, `freebsd`  
**Common GOARCH values:** `amd64`, `arm64`, `arm`, `386`, `riscv64`

CGO must be disabled for pure cross-compilation: `CGO_ENABLED=0 GOOS=linux go build ...`

---

## 47. Graceful Shutdown

A server that dies mid-request corrupts in-flight operations. Graceful shutdown:
1. Stop accepting new connections
2. Wait for in-flight requests to complete
3. Close resources (DB connections, caches)

```go
import (
    "context"
    "net/http"
    "os"
    "os/signal"
    "syscall"
)

func main() {
    srv := &http.Server{Addr: ":8080", Handler: handler}

    // Start server in a goroutine
    go func() {
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    // signal.NotifyContext (Go 1.16+) — cancel context on OS signal
    ctx, stop := signal.NotifyContext(context.Background(),
        os.Interrupt, syscall.SIGTERM)
    defer stop()

    <-ctx.Done()  // block until signal received

    log.Println("shutting down...")

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(shutdownCtx); err != nil {
        log.Printf("shutdown error: %v", err)
    }

    // Close other resources
    db.Close()
    redisClient.Close()

    log.Println("shutdown complete")
}
```

**`srv.Shutdown(ctx)`** stops the listener, waits for active connections to finish, and returns. The `ListenAndServe` goroutine returns `http.ErrServerClosed` — that's expected.

---

## 48. Dependency Injection in Go

Go favors explicit, constructor-based dependency injection over reflection-based frameworks.

### Constructor Functions

Pass dependencies as parameters to constructors. The type depends on abstractions (interfaces), not concretions.

```go
// Define interfaces for all external dependencies
type UserRepo interface {
    FindByID(ctx context.Context, id int) (*User, error)
    Save(ctx context.Context, u *User) error
}

type EmailSender interface {
    Send(to, subject, body string) error
}

// Service depends on interfaces, not concrete types
type UserService struct {
    repo  UserRepo
    email EmailSender
    log   *slog.Logger
}

// Constructor — inject at creation time
func NewUserService(repo UserRepo, email EmailSender, log *slog.Logger) *UserService {
    return &UserService{repo: repo, email: email, log: log}
}
```

### Wiring in main

Wire everything together in `main.go` — this is the only place that knows about concrete types:

```go
func main() {
    db, _ := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    logger := slog.New(slog.NewJSONHandler(os.Stderr, nil))

    repo := postgres.NewUserRepo(db)
    sender := smtp.NewEmailSender(os.Getenv("SMTP_HOST"))
    userSvc := NewUserService(repo, sender, logger)

    handler := api.NewHandler(userSvc)
    http.ListenAndServe(":8080", handler)
}
```

### Why Not a DI Framework?

- **wire** (Google): code-gen based, type-safe. Use for large codebases with many components.
- **fx** (Uber): runtime DI with reflection. Simpler for large apps.
- **Manual**: clear, explicit, fast compile times. Sufficient for most projects.

Manual DI is the Go idiom. Only reach for `wire`/`fx` when `main.go` becomes unwieldy (50+ wired types).

---

## 49. runtime Package Basics

```go
import "runtime"

// Goroutine count (useful for leak detection in tests)
n := runtime.NumGoroutine()
fmt.Printf("goroutines: %d\n", n)

// CPU cores available
cores := runtime.NumCPU()

// Set number of OS threads for goroutines (default: NumCPU)
runtime.GOMAXPROCS(4)
runtime.GOMAXPROCS(0)  // returns current value without changing

// Force a GC cycle (avoid in production — GC is automatic)
runtime.GC()

// Memory stats
var m runtime.MemStats
runtime.ReadMemStats(&m)
fmt.Printf("alloc: %d KB\n", m.Alloc/1024)
fmt.Printf("total alloc: %d KB\n", m.TotalAlloc/1024)
fmt.Printf("gc cycles: %d\n", m.NumGC)

// Goroutine stack trace (useful for debugging deadlocks)
buf := make([]byte, 1<<20)
n = runtime.Stack(buf, true)  // true = all goroutines
fmt.Printf("%s\n", buf[:n])

// Caller info (useful for loggers, error reporters)
_, file, line, ok := runtime.Caller(1)  // 1 = immediate caller
```

---

## 50. govulncheck & Security

### govulncheck

Scans your module for known vulnerabilities in dependencies.

```bash
# Install
go install golang.org/x/vuln/cmd/govulncheck@latest

# Scan your module
govulncheck ./...

# Output: lists affected packages, CVE IDs, and fix versions
# Example:
# Vulnerability #1: GO-2024-2687
# A malicious HTTP/2 server can cause a client to use excessive memory
# More info: https://pkg.go.dev/vuln/GO-2024-2687
# Module: golang.org/x/net@v0.17.0
# Fixed in: golang.org/x/net@v0.23.0
```

Run `govulncheck` in CI on every PR — it only reports vulnerabilities that are reachable in your code (not just present in dependencies).

### Other Security Tools

```bash
# staticcheck — static analysis (detects bugs, deprecated usage, unused code)
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...

# golangci-lint — runs many linters including staticcheck, errcheck, gosec
golangci-lint run ./...

# gosec — security-focused linter (SQL injection, hardcoded credentials, etc.)
gosec ./...
```
