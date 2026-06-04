# DDD + Hexagonal Architecture Reference

This document is a practical reference for learning Domain-Driven Design (DDD) and Hexagonal Architecture. It starts from the core ideas, then moves into tactical DDD, hexagonal architecture, strategic DDD, testing, and implementation guidance.

## 1. The Big Idea

DDD exists because the hardest complexity in many systems is not technical complexity. It is business complexity.

Frameworks, databases, APIs, queues, and cloud services matter, but they are usually not the center of the problem. The center is understanding the domain:

- What is an order?
- When is an order confirmed?
- Can a cancelled order be paid?
- Can a customer cancel after payment?
- What does "customer" mean in sales, billing, and support?
- Which rules must always be true?

DDD helps you model the business directly in code.

Hexagonal Architecture helps you protect that model from technical details.

Together:

```text
DDD tells you how to model the business.
Hexagonal Architecture tells you how to protect that model from frameworks, databases, APIs, and infrastructure.
```

The core principle:

```text
Business rules should not depend on technical details.
Technical details should depend on business rules.
```

## 2. CRUD Thinking vs Domain Thinking

CRUD thinking starts with data:

```text
orders table
- id
- customer_id
- status
- total
- created_at
```

Then it often creates services around table operations:

```ts
class OrderService {
  createOrder() {}
  updateOrder() {}
  deleteOrder() {}
  payOrder() {}
}
```

This can be fine for simple systems.

DDD thinking starts with business behavior:

```text
Can an order be confirmed without items?
Can a confirmed order accept more items?
Can a shipped order be cancelled?
Who is allowed to change the shipping address?
When does inventory get reserved?
```

Instead of scattering these rules across controllers, validators, services, and database queries, DDD tries to put them in the domain model.

Example:

```ts
class Order {
  private status: OrderStatus;
  private items: OrderItem[];

  confirm() {
    if (this.items.length === 0) {
      throw new Error("Cannot confirm an order without items");
    }

    if (this.status !== "DRAFT") {
      throw new Error("Only draft orders can be confirmed");
    }

    this.status = "CONFIRMED";
  }
}
```

The rule belongs to `Order`, so `Order` protects it.

## 3. Core Vocabulary

### Domain

The domain is the business area your software is about.

Examples:

- Ordering
- Banking
- Insurance
- Logistics
- Healthcare appointments
- Food delivery
- Inventory management

The domain is not the database. It is the business world being modeled.

### Domain Model

The domain model is the code representation of business concepts and rules.

It includes objects like:

- `Order`
- `Money`
- `Customer`
- `Invoice`
- `Shipment`
- `Payment`

But more importantly, it includes behavior:

- `order.confirm()`
- `invoice.markAsPaid()`
- `account.withdraw(amount)`
- `shipment.deliver()`

### Invariant

An invariant is a rule that must always remain true.

Examples:

```text
An order cannot be confirmed without items.
An account balance cannot go below zero.
Money cannot have a negative amount.
A delivered shipment cannot be cancelled.
```

DDD design is largely about deciding who protects which invariants.

## 4. Entity

An entity is a domain object defined by identity.

Its identity matters over time, even if its attributes change.

Examples:

- `Order`
- `Customer`
- `Product`
- `Invoice`
- `BankAccount`

An order can change from `DRAFT` to `CONFIRMED`, but it is still the same order because it has the same `OrderId`.

```ts
class Order {
  constructor(
    public readonly id: OrderId,
    private status: OrderStatus
  ) {}
}
```

Simple rule:

```text
If two objects have the same attributes but are still different things, they are probably entities.
```

Example:

```text
Two customers with the same name are not necessarily the same customer.
Two orders with the same items are not necessarily the same order.
```

## 5. Value Object

A value object is defined by its values, not identity.

Examples:

- `Money`
- `EmailAddress`
- `Address`
- `Quantity`
- `DateRange`
- `Coordinates`
- `FullName`

Two value objects with the same values are conceptually equal.

```ts
const a = new Money(100, "USD");
const b = new Money(100, "USD");
```

These represent the same value.

Value objects should usually be immutable.

```ts
class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: string
  ) {
    if (amount < 0) {
      throw new Error("Money cannot be negative");
    }

    if (!currency) {
      throw new Error("Currency is required");
    }
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error("Cannot add money with different currencies");
    }

    return new Money(this.amount + other.amount, this.currency);
  }
}
```

The method returns a new `Money`. It does not mutate the original object.

### Entity vs Value Object

Ask:

```text
If two objects have the same values, are they the same thing?
```

If yes, it is probably a value object.

If no, it is probably an entity.

Examples:

```text
User              -> Entity
EmailAddress      -> Value Object
Money             -> Value Object
Order             -> Entity
ShippingAddress   -> Value Object
Product           -> Usually Entity
DateRange         -> Value Object
CartItem          -> Usually Value Object, sometimes Entity
BankTransaction   -> Entity
GPSCoordinate     -> Value Object
```

Important: an ID in the database does not automatically make something a domain entity. Sometimes a table has an ID for technical reasons, while the domain concept is still a value object.

## 6. Aggregate

An aggregate is a consistency boundary.

It is a cluster of domain objects that are treated as one unit for business consistency.

Example:

```text
Order Aggregate
- Order
- OrderItem
- ShippingAddress
- Money
```

The aggregate protects rules like:

```text
An order cannot be confirmed without items.
A confirmed order cannot accept new items.
The order total must match its items.
A cancelled order cannot be shipped.
```

An aggregate is not just an object tree. It is not "everything related to an order." It is the boundary inside which rules must be immediately consistent.

## 7. Aggregate Root

The aggregate root is the main object through which the aggregate is accessed and changed.

For an order aggregate:

```text
Order Aggregate
- Order          <- Aggregate Root
- OrderItem
- ShippingAddress
- Money
```

External code should call:

```ts
order.addItem(productId, price, quantity);
order.confirm();
order.cancel();
```

External code should not do:

```ts
order.items.push(item);
order.status = "CONFIRMED";
```

The aggregate root guards the invariants.

### Entity vs Aggregate vs Aggregate Root

```text
Entity:
A domain object identified by identity.

Aggregate:
A consistency boundary around objects that must stay valid together.

Aggregate Root:
The main entity that controls access to an aggregate.
```

Usually the aggregate root is also an entity.

Not every entity is necessarily an aggregate root.

Repositories usually work with aggregate roots, not every entity.

Good:

```ts
orderRepository.save(order);
```

Suspicious:

```ts
orderItemRepository.save(orderItem);
```

Saving an internal object directly can bypass the aggregate root and break invariants.

## 8. Aggregate Design Rules

Design aggregates by business rules, not by database relationships.

Do not start with:

```text
Customer has Orders.
Order has Products.
Product has Supplier.
Supplier has Contracts.
```

That is data modeling.

Instead ask:

```text
What rule must always be true?
Who protects that rule?
What must change together in one transaction?
What can be eventually consistent?
```

Rule of thumb:

```text
Put objects in the same aggregate only when they must be strongly consistent immediately.
```

If one concept can be updated later through an event, it may belong in a separate aggregate.

Example:

```text
Order and OrderItem:
Usually same aggregate.

Order and Customer:
Usually separate aggregates.

Order and Shipment:
Usually separate aggregates.

Order and Inventory:
Usually separate aggregates.
```

Reference other aggregates by ID:

```ts
class Order {
  constructor(
    public readonly id: OrderId,
    public readonly customerId: CustomerId
  ) {}
}
```

Avoid holding a full `Customer` object inside `Order` unless there is a strong reason.

## 9. Repository

A repository gives the application layer access to aggregate roots.

It behaves like a collection of aggregates.

```ts
interface OrderRepository {
  findById(id: OrderId): Promise<Order>;
  save(order: Order): Promise<void>;
}
```

The repository interface should speak domain language. It should return domain objects, not database rows or ORM models.

Repositories are usually defined for aggregate roots:

```text
OrderRepository
CustomerRepository
ProductRepository
AccountRepository
```

Usually suspicious:

```text
OrderItemRepository
MoneyRepository
AddressRepository
```

Those are often internal parts of an aggregate or value objects.

## 10. Application Service / Use Case

An application service represents a use case.

Examples:

- `CreateOrderUseCase`
- `AddItemToOrderUseCase`
- `ConfirmOrderUseCase`
- `CancelOrderUseCase`
- `PayInvoiceUseCase`
- `TransferMoneyUseCase`

Application services coordinate workflow. They should not usually contain deep business rules.

Typical responsibilities:

```text
Load aggregate.
Call domain behavior.
Save aggregate.
Publish events.
Call external ports.
Handle transaction boundary.
Perform use-case-level authorization.
```

Example:

```ts
class ConfirmOrderUseCase {
  constructor(
    private readonly orders: OrderRepository,
    private readonly eventBus: EventBus
  ) {}

  async execute(command: ConfirmOrderCommand): Promise<void> {
    const order = await this.orders.findById(command.orderId);

    order.confirm();

    await this.orders.save(order);
    await this.eventBus.publishAll(order.pullEvents());
  }
}
```

The use case coordinates. The domain decides if the operation is valid.

Bad:

```ts
class ConfirmOrderUseCase {
  async execute(orderId: string) {
    const order = await this.orders.findById(orderId);

    if (order.items.length === 0) {
      throw new Error("Cannot confirm empty order");
    }

    order.status = "CONFIRMED";

    await this.orders.save(order);
  }
}
```

Better:

```ts
class ConfirmOrderUseCase {
  async execute(orderId: string) {
    const order = await this.orders.findById(orderId);
    order.confirm();
    await this.orders.save(order);
  }
}
```

## 11. Domain Service

A domain service contains business logic that does not naturally belong to one entity or value object.

It is still domain logic.

Examples:

- `MoneyTransferService`
- `DiscountPolicy`
- `PricingService`
- `FraudPolicy`
- `CourierAssignmentPolicy`
- `ExchangeRateCalculator`

Example:

```ts
class DiscountPolicy {
  calculateDiscount(customer: Customer, order: Order): Money {
    if (customer.isVip() && order.total().isGreaterThan(new Money(100, "USD"))) {
      return new Money(10, "USD");
    }

    return new Money(0, "USD");
  }
}
```

### Application Service vs Domain Service

```text
Application Service:
Coordinates a use case.

Domain Service:
Makes a business decision that does not naturally fit inside one entity or value object.
```

Example:

```ts
class MoneyTransferService {
  transfer(from: Account, to: Account, amount: Money) {
    from.withdraw(amount);
    to.deposit(amount);
  }
}
```

The application service loads and saves:

```ts
class TransferMoneyUseCase {
  constructor(
    private readonly accounts: AccountRepository,
    private readonly transferService: MoneyTransferService
  ) {}

  async execute(command: TransferMoneyCommand): Promise<void> {
    const from = await this.accounts.findById(command.fromAccountId);
    const to = await this.accounts.findById(command.toAccountId);

    this.transferService.transfer(from, to, command.amount);

    await this.accounts.save(from);
    await this.accounts.save(to);
  }
}
```

Default rule:

```text
Application service loads things.
Domain service decides domain logic.
```

## 12. Domain Events

A domain event records something meaningful that already happened in the domain.

Examples:

- `OrderConfirmed`
- `PaymentCaptured`
- `InvoiceIssued`
- `CustomerRegistered`
- `CourierAssigned`
- `ShipmentDelivered`

Command:

```text
Confirm this order.
```

Event:

```text
This order was confirmed.
```

Commands request something. Events state that something happened.

Example:

```ts
class Order {
  private events: DomainEvent[] = [];

  confirm() {
    if (this.items.length === 0) {
      throw new Error("Cannot confirm empty order");
    }

    if (this.status !== "DRAFT") {
      throw new Error("Only draft orders can be confirmed");
    }

    this.status = "CONFIRMED";
    this.events.push(new OrderConfirmed(this.id));
  }

  pullEvents(): DomainEvent[] {
    const events = this.events;
    this.events = [];
    return events;
  }
}
```

The application service publishes after saving:

```ts
class ConfirmOrderUseCase {
  constructor(
    private readonly orders: OrderRepository,
    private readonly eventBus: EventBus
  ) {}

  async execute(command: ConfirmOrderCommand): Promise<void> {
    const order = await this.orders.findById(command.orderId);

    order.confirm();

    await this.orders.save(order);
    await this.eventBus.publishAll(order.pullEvents());
  }
}
```

Use domain events when:

```text
Multiple things react to the same domain fact.
You want to decouple workflows.
You cross aggregate boundaries.
You cross bounded contexts.
You need eventual consistency.
```

Avoid events when:

```text
A direct method call is clearer.
The workflow must be immediately consistent.
Handlers create surprising hidden side effects.
```

### Domain Events vs Integration Events

Domain event:

```text
Internal fact inside your domain/application.
```

Integration event:

```text
External contract published to other systems or bounded contexts.
```

Do not expose internal domain event classes casually as external contracts.

## 13. Outbox Pattern

Problem:

```text
1. Save order to database.
2. Publish event to message broker.
```

What if saving succeeds but publishing fails?

The order is confirmed, but no one receives the event.

The outbox pattern solves this by saving the event in the same transaction as the aggregate:

```text
Transaction:
- Save aggregate.
- Insert event into outbox table.

Background publisher:
- Read unpublished outbox events.
- Publish to broker.
- Mark as published.
```

This makes event publication reliable.

## 14. Hexagonal Architecture

Hexagonal Architecture is also called Ports and Adapters.

The goal:

```text
Keep business logic independent from external technology.
```

External technology includes:

- HTTP
- Database
- Message broker
- File system
- Email provider
- Payment provider
- Framework
- CLI
- Cron job

The inside:

```text
Domain
Application use cases
```

The outside:

```text
Controllers
Database adapters
API clients
Message consumers
Framework code
```

Dependency direction:

```text
Infrastructure -> Application -> Domain
```

The domain should not depend on infrastructure.

## 15. Port

A port is an interface representing a capability.

Example outbound port:

```ts
interface OrderRepository {
  findById(id: OrderId): Promise<Order>;
  save(order: Order): Promise<void>;
}
```

This says:

```text
The application needs a way to load and save orders.
```

It does not say:

```text
Use PostgreSQL.
Use MongoDB.
Use Prisma.
Use TypeORM.
```

That belongs in an adapter.

## 16. Adapter

An adapter connects the outside world to a port.

Example outbound adapter:

```ts
class PostgresOrderRepository implements OrderRepository {
  async findById(id: OrderId): Promise<Order> {
    // SQL or ORM logic
  }

  async save(order: Order): Promise<void> {
    // SQL or ORM logic
  }
}
```

Example inbound adapter:

```ts
class OrderController {
  constructor(private readonly confirmOrder: ConfirmOrderUseCase) {}

  async confirm(request: HttpRequest): Promise<HttpResponse> {
    await this.confirmOrder.execute({
      orderId: request.params.orderId
    });

    return { status: 204 };
  }
}
```

The controller translates HTTP into a use case call. It should not contain business rules.

## 17. Inbound and Outbound Ports

Inbound ports describe what the application can do.

Example:

```ts
interface ConfirmOrder {
  execute(command: ConfirmOrderCommand): Promise<void>;
}
```

Inbound adapters call inbound ports:

```text
HTTP Controller
GraphQL Resolver
CLI Command
Queue Consumer
Cron Job
```

Outbound ports describe what the application needs from the outside world:

```ts
interface PaymentGateway {
  charge(request: ChargePaymentRequest): Promise<PaymentResult>;
}

interface EmailSender {
  send(message: EmailMessage): Promise<void>;
}

interface EventBus {
  publishAll(events: DomainEvent[]): Promise<void>;
}
```

Outbound adapters implement outbound ports:

```text
StripePaymentGateway
SendgridEmailSender
KafkaEventBus
PostgresOrderRepository
```

Memory aid:

```text
Inbound adapter drives the application.
Outbound adapter is driven by the application.
```

## 18. Typical Folder Structure

Folder structure is less important than dependency direction, but a common structure is:

```text
src/
  domain/
    order/
      Order.ts
      OrderItem.ts
      OrderId.ts
      Money.ts
      OrderConfirmed.ts

  application/
    order/
      ConfirmOrderUseCase.ts
      AddItemToOrderUseCase.ts
      ports/
        OrderRepository.ts
        EventBus.ts

  infrastructure/
    http/
      OrderController.ts
    persistence/
      PostgresOrderRepository.ts
    messaging/
      KafkaEventBus.ts
```

The important rule:

```text
Domain should not import application or infrastructure.
Application may import domain.
Infrastructure may import application and domain.
```

Folder names do not create architecture. Dependency direction does.

## 19. Strategic DDD

Tactical DDD is about code patterns:

- Entity
- Value Object
- Aggregate
- Repository
- Domain Service
- Domain Event

Strategic DDD is about system boundaries and language:

- Bounded Context
- Ubiquitous Language
- Subdomain
- Context Map
- Anti-Corruption Layer
- Shared Kernel

Strategic DDD is often more important than tactical patterns.

## 20. Ubiquitous Language

Ubiquitous Language means the team uses the same business language in conversation, code, tests, documentation, and user stories.

If the business says:

```text
An order is confirmed.
```

The code should probably say:

```ts
order.confirm();
```

Not:

```ts
order.updateStatus("C");
```

The goal is to reduce translation between business conversations and code.

Warning sign:

```text
Business people use one vocabulary.
Developers use another vocabulary.
Database columns use a third vocabulary.
```

That creates confusion and bugs.

## 21. Bounded Context

A bounded context is a boundary inside which a model and language are consistent.

The same word can mean different things in different contexts.

Example: `Customer`

In Sales:

```text
A potential buyer or lead.
```

In Billing:

```text
Someone with payment details and invoices.
```

In Support:

```text
Someone who can open tickets.
```

Trying to create one universal `Customer` model often creates a messy object that means too many things.

Better:

```text
Sales Context:
Lead / Prospect / Account

Billing Context:
BillingCustomer / Payer

Support Context:
SupportCustomer / TicketRequester
```

A bounded context protects language and model clarity.

## 22. Subdomains

A subdomain is part of the business domain.

Common categories:

```text
Core Subdomain:
The area that gives the business competitive advantage.

Supporting Subdomain:
Business-specific but not the main differentiator.

Generic Subdomain:
Common capability that can often be bought or reused.
```

Example for food delivery:

```text
Core:
Dispatching and matching orders to couriers.

Supporting:
Restaurant onboarding.

Generic:
Authentication, payments, email delivery.
```

Spend the most design energy on the core subdomain.

Do not over-engineer generic subdomains.

## 23. Context Map

A context map describes relationships between bounded contexts.

Example:

```text
Ordering Context
  -> publishes OrderConfirmed

Inventory Context
  -> consumes OrderConfirmed
  -> reserves stock

Billing Context
  -> consumes OrderConfirmed
  -> creates invoice
```

Context maps help you see:

- Who depends on whom
- Which team owns which model
- Where translation is needed
- Which events or APIs connect contexts

## 24. Anti-Corruption Layer

An Anti-Corruption Layer, or ACL, protects your model from another model.

Use it when integrating with an external system or another bounded context whose language does not match yours.

Example:

Your domain says:

```text
OrderConfirmed
```

External system says:

```json
{
  "state": 7,
  "process_type": "O_PROC",
  "flag": "Y"
}
```

Do not let that language leak into your domain.

Create a translator:

```ts
class ExternalOrderStatusTranslator {
  toDomainStatus(response: ExternalOrderResponse): OrderStatus {
    if (response.state === 7 && response.flag === "Y") {
      return "CONFIRMED";
    }

    return "PENDING";
  }
}
```

The ACL keeps your domain clean.

## 25. Shared Kernel

A shared kernel is a small shared model used by multiple bounded contexts.

It should be used carefully because it creates coupling.

Good candidates:

- Very stable value objects
- Shared IDs
- Common primitives

Example:

```text
Money
Currency
CustomerId
```

Bad shared kernel:

```text
A giant shared domain library used by every team.
```

That usually becomes a bottleneck.

## 26. Factories

A factory creates complex domain objects while protecting invariants.

Use a factory when object creation is not simple.

Simple creation can stay in the constructor:

```ts
const money = new Money(100, "USD");
```

Use a factory when creation has rules:

```ts
class OrderFactory {
  createDraftOrder(customerId: CustomerId): Order {
    return Order.createDraft({
      id: OrderId.generate(),
      customerId
    });
  }
}
```

Do not create factories for everything. Use them when they simplify real creation complexity.

## 27. Specification

A specification represents a reusable business rule.

Example:

```ts
class CustomerEligibleForDiscount {
  isSatisfiedBy(customer: Customer): boolean {
    return customer.isVip() && customer.hasNoOverdueInvoices();
  }
}
```

Specifications are useful when rules need to be:

- Reused
- Combined
- Tested independently
- Expressed clearly as business concepts

Do not use specifications for every `if` statement.

## 28. CQRS

CQRS means Command Query Responsibility Segregation.

It separates writes from reads.

Commands change state:

```text
ConfirmOrder
CancelOrder
PayInvoice
```

Queries read data:

```text
GetOrderDetails
ListCustomerOrders
GetDashboardStats
```

In DDD systems, commands often use aggregates:

```text
Load Order aggregate -> call behavior -> save
```

Queries often use optimized read models:

```text
SELECT data for screen directly
```

You do not always need full CQRS with separate databases. Sometimes it simply means not forcing every read through aggregates.

Important:

```text
Aggregates are for protecting business rules during writes.
They are not always the best shape for reads.
```

## 29. Testing Strategy

DDD and hexagonal architecture make testing easier because business logic can be tested without infrastructure.

### Domain Tests

Test entities, value objects, aggregates, and domain services directly.

Example:

```ts
it("does not confirm an empty order", () => {
  const order = Order.createDraft(new OrderId("order-1"));

  expect(() => order.confirm()).toThrow("Cannot confirm empty order");
});
```

These tests should be fast and not require a database.

### Application Tests

Test use cases with fake repositories and fake ports.

```ts
it("saves the order after confirming it", async () => {
  const orders = new FakeOrderRepository();
  const eventBus = new FakeEventBus();
  const useCase = new ConfirmOrderUseCase(orders, eventBus);

  await useCase.execute({ orderId: "order-1" });

  expect(orders.savedOrder.status()).toBe("CONFIRMED");
});
```

### Adapter Tests

Test infrastructure separately:

- Repository mapping
- HTTP request/response behavior
- Message serialization
- External API integration

The domain should not need infrastructure tests to prove its rules.

## 30. Common Mistakes

### Mistake 1: Treating DDD as Folder Structure

Bad:

```text
domain/
application/
infrastructure/
```

But every layer imports everything.

Architecture is dependency direction, not folder names.

### Mistake 2: Anemic Domain Model

Entities have only data:

```ts
class Order {
  id: string;
  status: string;
  items: OrderItem[];
}
```

All rules live in services:

```ts
class OrderService {
  confirm(order: Order) {
    if (order.items.length === 0) {
      throw new Error("Cannot confirm empty order");
    }

    order.status = "CONFIRMED";
  }
}
```

This is not always wrong for simple CRUD, but it weakens rich domain models.

### Mistake 3: Giant Aggregates

Bad:

```text
Customer
- Orders
- Payments
- Invoices
- Shipments
- SupportTickets
```

This creates huge transaction boundaries and complicated persistence.

Prefer smaller aggregates connected by IDs and events.

### Mistake 4: Repositories for Everything

Avoid repositories for internal aggregate parts and value objects unless there is a strong reason.

Repositories are usually for aggregate roots.

### Mistake 5: Domain Depends on Infrastructure

Bad:

```ts
class Order {
  async confirm(db: Database, email: EmailSender) {
    // ...
  }
}
```

The domain should not know technical details.

### Mistake 6: Overusing Events

Events are useful, but they can hide control flow.

Use direct calls when they are clearer and consistency must be immediate.

### Mistake 7: Overengineering Simple CRUD

DDD is most useful when business rules are complex.

For simple CRUD, a simpler architecture may be better.

## 31. Decision Checklist

When modeling a feature, ask:

```text
1. What business action is happening?
2. What words does the business use for this action?
3. What invariants must always hold?
4. Which aggregate protects those invariants?
5. What is the aggregate root?
6. What value objects make invalid states harder?
7. What should be immediately consistent?
8. What can be eventually consistent?
9. What external systems are involved?
10. Which ports does the application need?
11. Which adapters implement those ports?
12. What domain events should be emitted?
13. What tests prove the business rules?
```

## 32. Example: Online Order

Business rules:

```text
An order starts as DRAFT.
Items can be added only while the order is DRAFT.
An order cannot be confirmed without items.
A confirmed order cannot accept more items.
```

Domain:

```ts
type OrderStatus = "DRAFT" | "CONFIRMED" | "CANCELLED";

class Order {
  private items: OrderItem[] = [];
  private status: OrderStatus = "DRAFT";

  constructor(public readonly id: OrderId) {}

  addItem(productId: ProductId, unitPrice: Money, quantity: Quantity) {
    if (this.status !== "DRAFT") {
      throw new Error("Cannot add items unless order is draft");
    }

    this.items.push(new OrderItem(productId, unitPrice, quantity));
  }

  confirm() {
    if (this.items.length === 0) {
      throw new Error("Cannot confirm empty order");
    }

    if (this.status !== "DRAFT") {
      throw new Error("Only draft orders can be confirmed");
    }

    this.status = "CONFIRMED";
  }
}
```

Application:

```ts
class ConfirmOrderUseCase {
  constructor(private readonly orders: OrderRepository) {}

  async execute(command: ConfirmOrderCommand): Promise<void> {
    const order = await this.orders.findById(new OrderId(command.orderId));

    order.confirm();

    await this.orders.save(order);
  }
}
```

Infrastructure:

```ts
class OrderController {
  constructor(private readonly confirmOrder: ConfirmOrderUseCase) {}

  async confirm(req: Request, res: Response) {
    await this.confirmOrder.execute({
      orderId: req.params.orderId
    });

    res.status(204).send();
  }
}
```

The responsibilities are clear:

```text
Order:
Business rules.

ConfirmOrderUseCase:
Workflow.

OrderController:
HTTP translation.

OrderRepository implementation:
Persistence.
```

## 33. Learning Roadmap

Recommended order:

```text
1. Entity vs Value Object
2. Aggregate and Aggregate Root
3. Repositories
4. Application Services
5. Domain Services
6. Domain Events
7. Ports and Adapters
8. Testing domain logic
9. Bounded Contexts
10. Ubiquitous Language
11. Context Maps
12. Anti-Corruption Layers
13. CQRS
14. Outbox Pattern
15. Eventual Consistency
16. Real project implementation
```

## 34. Short Glossary

```text
Domain:
The business area being modeled.

Entity:
Object with identity.

Value Object:
Object defined by values.

Aggregate:
Consistency boundary.

Aggregate Root:
Main object that controls aggregate access.

Invariant:
Rule that must always be true.

Repository:
Collection-like abstraction for aggregate persistence.

Application Service:
Use case coordinator.

Domain Service:
Business logic that does not fit one entity/value object.

Domain Event:
Business-significant fact that happened.

Port:
Interface representing a capability.

Adapter:
Technical implementation or caller of a port.

Bounded Context:
Boundary where a model and language are consistent.

Ubiquitous Language:
Shared language used by business, code, tests, and documentation.

Anti-Corruption Layer:
Translator that protects your model from another model.

CQRS:
Separate command/write concerns from query/read concerns.
```

## 35. Final Mental Model

When building a feature, think in this order:

```text
Business language first.
Business rules second.
Aggregate boundary third.
Use case workflow fourth.
Ports fifth.
Adapters last.
```

Do not start with the database.

Do not start with the framework.

Start with the business action and the rules that must remain true.

