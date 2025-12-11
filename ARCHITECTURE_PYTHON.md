# Clean/Hexagonal Architecture Guide for Python

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Project Structure](#project-structure)
4. [Core Layer (Domain)](#core-layer-domain)
5. [Infrastructure Layer](#infrastructure-layer)
6. [Naming Conventions](#naming-conventions)
7. [Dependency Rules](#dependency-rules)
8. [Implementation Guide](#implementation-guide)
9. [Best Practices](#best-practices)
10. [Testing Strategy](#testing-strategy)
11. [Common Pitfalls](#common-pitfalls)

---

## Overview

This document describes a **Clean Architecture** combined with **Hexagonal Architecture (Ports & Adapters)** pattern for Python applications. The goal is to create maintainable, testable, and framework-independent business logic.

### Key Benefits

- **Framework Independence**: Business logic has zero framework dependencies
- **Testability**: Core logic can be tested without databases, HTTP, or external services
- **Maintainability**: Clear boundaries and single responsibility principle
- **Flexibility**: Easy to swap implementations (database, message broker, APIs)
- **Domain-Driven**: Business concepts are first-class citizens
- **Type Safety**: Leverages Python's type hints for robust code

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      External Systems                           │
│            (HTTP, Database, Queue, APIs, etc.)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  Infrastructure Layer                           │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌────────────┐ │
│  │Controllers │  │  Adapters  │  │Presenters│  │  Factories │ │
│  └──────┬─────┘  └──────┬─────┘  └────┬─────┘  └──────┬─────┘ │
│         └────────────────┴─────────────┴────────────────┘       │
│                           │                                     │
│              Implements Gateway Protocols                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Core Layer (Domain)                          │
│  ┌──────────┐  ┌────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │ UseCases │  │Actions │  │Entities  │  │ Gateways (Ports)│  │
│  └──────────┘  └────────┘  └──────────┘  └─────────────────┘  │
│                                                                 │
│              Pure Business Logic (Framework Free)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture Principles

### 1. Dependency Rule

**Dependencies always point inward**: The Core layer NEVER depends on the Infrastructure layer.

```
✅ ALLOWED:
Infrastructure → Core     (Infrastructure depends on Domain)
Core → Core              (Domain depends on Domain)

❌ FORBIDDEN:
Core → Infrastructure    (Domain MUST NOT depend on Infrastructure)
Core → Framework         (Domain MUST NOT depend on Framework)
```

### 2. Interface Segregation (Ports)

External dependencies are abstracted behind protocols (interfaces) defined in Core layer.

```python
# ✅ Correct: Gateway protocol in core/
# core/modules/orders/create_order/gateways/order_gateway.py
from typing import Protocol, Optional
from core.modules.orders.generics.entities.order import Order

class OrderGateway(Protocol):
    def save(self, order: Order) -> Order: ...
    def exists(self, order_number: str) -> bool: ...
    def find_by_id(self, id: int) -> Optional[Order]: ...

# ✅ Correct: Adapter implementation in infrastructure
# infrastructure/adapters/orders/order_adapter.py
from core.modules.orders.create_order.gateways.order_gateway import OrderGateway

class OrderAdapter:
    """Implements OrderGateway protocol using SQLAlchemy ORM"""

    def save(self, order: Order) -> Order:
        # Uses database/ORM to implement the protocol
        pass
```

### 3. Single Responsibility

Each class has one reason to change:
- **UseCase**: Orchestrates a single business operation
- **Action**: Encapsulates a single business rule or operation
- **Entity**: Represents a business concept
- **Gateway**: Defines a contract for external dependency

---

## Project Structure

```
project/
├── src/
│   ├── core/                         # Domain Layer (Framework-free)
│   │   ├── collection.py            # Base collection class
│   │   ├── dependencies/             # Shared interfaces (Protocols)
│   │   │   ├── log_interface.py
│   │   │   ├── cache_interface.py
│   │   │   └── event_publisher_interface.py
│   │   │
│   │   ├── enums/                    # Domain enumerations
│   │   ├── events/                   # Domain events
│   │   │   ├── message.py            # Base event message
│   │   │   └── order_was_created_event.py
│   │   │
│   │   └── modules/                  # Business features
│   │       └── {module}/             # e.g., orders, products, users
│   │           ├── generics/         # Shared within module (optional)
│   │           │   ├── entities/     # Shared domain entities
│   │           │   └── collections/  # Shared domain collections
│   │           │
│   │           └── {use_case}/       # e.g., create_order, list_orders
│   │               ├── {use_case}_use_case.py  # Main orchestrator (REQUIRED)
│   │               ├── inputs/
│   │               │   └── {use_case}_input.py  # Input DTO (REQUIRED)
│   │               │
│   │               ├── responses/            # Output DTOs (REQUIRED)
│   │               │   ├── {use_case}_response.py  # Abstract base (optional)
│   │               │   ├── {use_case}_success.py
│   │               │   └── {use_case}_error.py
│   │               │
│   │               ├── actions/              # Business operations (REQUIRED)
│   │               │   └── *.py              # Single-purpose business logic
│   │               │
│   │               ├── gateways/             # Protocol definitions (REQUIRED)
│   │               │   └── *_gateway.py      # Contracts for external deps
│   │               │
│   │               ├── entities/             # Domain objects (optional)
│   │               │   └── *.py
│   │               │
│   │               ├── collections/          # Domain collections (optional)
│   │               │   └── *_collection.py
│   │               │
│   │               └── exceptions/           # Domain exceptions (optional)
│   │                   └── *_exception.py
│   │
│   └── infrastructure/               # Infrastructure Layer (Framework-specific)
│       ├── adapters/                 # Gateway implementations (Ports & Adapters)
│       │   ├── cache/                # Cache adapters
│       │   ├── event_publisher/      # Event publishing adapters
│       │   ├── logger/               # Logging adapters
│       │   └── modules/              # Module-specific adapters
│       │       └── {module}/
│       │           └── {use_case}/
│       │               ├── order_adapter.py
│       │               ├── payment_adapter.py
│       │               └── notification_adapter.py
│       │
│       ├── http/
│       │   ├── controllers/          # HTTP entry points
│       │   ├── middleware/
│       │   └── schemas/              # Pydantic schemas for validation
│       │
│       ├── cli/                      # CLI commands
│       ├── queue/                    # Queue/job consumers
│       ├── factories/                # Create domain objects from infrastructure data
│       ├── models/                   # ORM models (e.g., SQLAlchemy, Django ORM)
│       └── presenters/               # Transform domain responses to HTTP format
│
├── tests/
│   ├── unit/                         # Unit tests (Core layer)
│   ├── integration/                  # Integration tests (Adapters)
│   └── e2e/                          # End-to-end tests
│
├── alembic/                          # Database migrations (if using Alembic)
├── pyproject.toml                    # Project dependencies
└── README.md
```

---

## Core Layer (Domain)

The Core layer contains **pure business logic** with zero framework dependencies.

### Module Structure

```
core/modules/{module}/{use_case}/
```

**Naming Convention**: Use **snake_case** for files/directories and **PascalCase** for class names.

Examples:
- `orders/create_order/`
- `orders/cancel_order/`
- `products/update_stock/`
- `users/register_user/`

### Core Components

#### 1. UseCase (Required)

**File**: `{use_case}_use_case.py` (e.g., `create_order_use_case.py`)

**Purpose**: Orchestrates a single business operation by coordinating Actions and Gateways.

**Responsibilities**:
- Receive Input DTO
- Execute business actions in sequence
- Handle domain exceptions
- Return Response DTO
- Log execution flow

**Rules**:
- ✅ Must be named `{use_case}_use_case.py` (e.g., `create_order_use_case.py`)
- ✅ Must have an `execute()` method that receives Input and returns Response
- ✅ Must instantiate Actions in `__init__`
- ✅ Must inject Gateways (protocols) via `__init__`
- ✅ Must handle exceptions and log errors
- ❌ Must NOT contain business logic (delegate to Actions)
- ❌ Must NOT depend on framework classes

**Example**:

```python
# core/modules/orders/create_order/create_order_use_case.py
from core.dependencies.log_interface import LogInterface
from core.modules.orders.create_order.gateways.order_gateway import OrderGateway
from core.modules.orders.create_order.gateways.payment_gateway import PaymentGateway
from core.modules.orders.create_order.actions.validate_order_data_action import ValidateOrderDataAction
from core.modules.orders.create_order.actions.calculate_total_price_action import CalculateTotalPriceAction
from core.modules.orders.create_order.actions.process_payment_action import ProcessPaymentAction
from core.modules.orders.create_order.actions.save_order_action import SaveOrderAction
from core.modules.orders.create_order.inputs.create_order_input import CreateOrderInput
from core.modules.orders.create_order.responses.create_order_response import CreateOrderResponse
from core.modules.orders.create_order.responses.create_order_success import CreateOrderSuccess
from core.modules.orders.create_order.responses.create_order_error import CreateOrderError
from core.modules.orders.create_order.exceptions.duplicate_order_exception import DuplicateOrderException

class CreateOrderUseCase:
    def __init__(
        self,
        order_gateway: OrderGateway,
        payment_gateway: PaymentGateway,
        logger: LogInterface
    ):
        self.validate_order_data_action = ValidateOrderDataAction(order_gateway)
        self.calculate_total_price_action = CalculateTotalPriceAction()
        self.process_payment_action = ProcessPaymentAction(payment_gateway)
        self.save_order_action = SaveOrderAction(order_gateway)
        self.logger = logger

    def execute(self, input_data: CreateOrderInput) -> CreateOrderResponse:
        self.logger.info('[CreateOrder] Init Use Case', {
            'customer_id': input_data.customer_id
        })

        try:
            # Execute business actions in sequence
            self.validate_order_data_action.apply(input_data.order)

            order = input_data.order
            order = self.calculate_total_price_action.apply(order)

            self.process_payment_action.apply(order, input_data.payment_method)

            saved_order = self.save_order_action.apply(order)

            self.logger.info('[CreateOrder] Finish Use Case', {
                'order_id': saved_order.id
            })

            return CreateOrderSuccess(order=saved_order)

        except Exception as exception:
            self.logger.error('[CreateOrder] Domain error', {
                'exception': str(exception)
            })
            return CreateOrderError(throwable=exception)
```

---

#### 2. Input (Required)

**Location**: `inputs/{use_case}_input.py` (e.g., `create_order_input.py`)

**Purpose**: Input Data Transfer Object (DTO) that encapsulates all data needed by the UseCase.

**Responsibilities**:
- Receive input parameters
- Validate data types (via type hints)
- Provide immutable access to data

**Rules**:
- ✅ Must be named `{use_case}_input.py` (e.g., `create_order_input.py`)
- ✅ Must use `@dataclass(frozen=True)` for immutability
- ✅ Must contain only primitive types or domain Entities
- ❌ Must NOT contain validation logic (use framework validators in Infrastructure layer)
- ❌ Must NOT depend on framework classes

**Example**:

```python
# core/modules/orders/create_order/inputs/create_order_input.py
from dataclasses import dataclass
from core.modules.orders.generics.entities.order import Order

@dataclass(frozen=True)
class CreateOrderInput:
    order: Order
    customer_id: int
    payment_method: str
```

---

#### 3. Response (Required)

**Location**: `responses/`

**Purpose**: Output DTOs that encapsulate the result of a UseCase execution.

**Structure**:
- `{use_case}_response.py` - Abstract base class (optional)
- `{use_case}_success.py` - Success result
- `{use_case}_error.py` - Error result

**Responsibilities**:
- Return data from UseCase
- Indicate success or failure
- Carry domain entities or exceptions

**Rules**:
- ✅ Must extend abstract base Response class (if using one)
- ✅ Must be named `{use_case}_success.py` and `{use_case}_error.py`
- ✅ Must use `@dataclass(frozen=True)` for immutability
- ✅ Success responses carry domain entities or collections
- ✅ Error responses carry exceptions
- ❌ Must NOT contain presentation logic (use Presenters in Infrastructure layer)

**Example**:

```python
# Base class (optional)
# core/modules/orders/create_order/responses/create_order_response.py
from abc import ABC

class CreateOrderResponse(ABC):
    pass

# Success response
# core/modules/orders/create_order/responses/create_order_success.py
from dataclasses import dataclass
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.create_order.responses.create_order_response import CreateOrderResponse

@dataclass(frozen=True)
class CreateOrderSuccess(CreateOrderResponse):
    order: Order

# Error response
# core/modules/orders/create_order/responses/create_order_error.py
from dataclasses import dataclass
from core.modules.orders.create_order.responses.create_order_response import CreateOrderResponse

@dataclass(frozen=True)
class CreateOrderError(CreateOrderResponse):
    throwable: Exception
```

---

#### 4. Actions (Required)

**Location**: `actions/{name}_action.py`

**Purpose**: Encapsulate a single, testable business operation.

**Responsibilities**:
- Execute ONE specific business operation
- Apply business logic
- Use Gateways to interact with external systems
- Raise domain exceptions when operations fail

**Rules**:
- ✅ Must be named `{action}_action.py` (e.g., `calculate_total_price_action.py`)
- ✅ Must have an `apply()` method (may accept parameters and return values)
- ✅ Must inject dependencies (Gateways) via `__init__`
- ✅ Should be small and focused (Single Responsibility Principle)
- ❌ Must NOT orchestrate multiple actions (use UseCase for that)
- ❌ Must NOT depend on framework classes

**Example 1: Pure Business Logic**

```python
# core/modules/orders/create_order/actions/calculate_total_price_action.py
from core.modules.orders.generics.entities.order import Order

class CalculateTotalPriceAction:
    def apply(self, order: Order) -> Order:
        total = 0.0

        for item in order.items:
            total += item.price * item.quantity

        # Apply discount if applicable
        if order.has_discount_coupon():
            total = total * (1 - order.get_discount_percentage() / 100)

        # Add shipping cost
        total += self._calculate_shipping_cost(order)

        order.set_total_price(total)

        return order

    def _calculate_shipping_cost(self, order: Order) -> float:
        """Business logic for shipping calculation"""
        return 25.00 if order.get_weight() > 10 else 10.00
```

**Example 2: Using Gateway**

```python
# core/modules/orders/create_order/actions/save_order_action.py
from core.modules.orders.create_order.gateways.order_gateway import OrderGateway
from core.modules.orders.generics.entities.order import Order

class SaveOrderAction:
    def __init__(self, order_gateway: OrderGateway):
        self.order_gateway = order_gateway

    def apply(self, order: Order) -> Order:
        return self.order_gateway.save(order)
```

**Example 3: With Validation**

```python
# core/modules/orders/create_order/actions/validate_order_data_action.py
from core.modules.orders.create_order.gateways.order_gateway import OrderGateway
from core.modules.orders.create_order.exceptions.duplicate_order_exception import DuplicateOrderException
from core.modules.orders.create_order.exceptions.minimum_order_amount_exception import MinimumOrderAmountException
from core.modules.orders.create_order.exceptions.invalid_quantity_exception import InvalidQuantityException
from core.modules.orders.generics.entities.order import Order

class ValidateOrderDataAction:
    def __init__(self, order_gateway: OrderGateway):
        self.order_gateway = order_gateway

    def apply(self, order: Order) -> None:
        # Check for duplicate order number
        if self.order_gateway.exists(order.order_number):
            raise DuplicateOrderException(order.order_number)

        # Validate minimum order amount
        if order.get_subtotal() < 10.00:
            raise MinimumOrderAmountException(10.00)

        # Validate items availability
        for item in order.items:
            if item.quantity <= 0:
                raise InvalidQuantityException(item.product_id)
```

---

#### 5. Gateways (Required)

**Location**: `gateways/{name}_gateway.py`

**Purpose**: Define **protocols (contracts)** for external dependencies. These are the **PORTS** in Hexagonal Architecture.

**Responsibilities**:
- Define methods for accessing external systems
- Abstract database, API, event bus, cache, etc.
- Allow dependency inversion

**Rules**:
- ✅ Must be named `{resource}_gateway.py` (e.g., `order_gateway.py`, `payment_gateway.py`)
- ✅ Must be a Protocol (Python 3.8+)
- ✅ Must use domain types (Entities, Collections) in method signatures
- ✅ Method names should describe business operations, not technical details
- ❌ Must NOT contain implementation logic
- ❌ Must NOT reference framework classes

**Example**:

```python
# core/modules/orders/create_order/gateways/order_gateway.py
from typing import Protocol, Optional
from core.modules.orders.generics.entities.order import Order

class OrderGateway(Protocol):
    def save(self, order: Order) -> Order: ...
    def exists(self, order_number: str) -> bool: ...
    def find_by_id(self, id: int) -> Optional[Order]: ...
```

```python
# core/modules/orders/create_order/gateways/payment_gateway.py
from typing import Protocol
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.generics.entities.payment import Payment

class PaymentGateway(Protocol):
    def process_payment(self, order: Order, payment_method: str) -> Payment: ...
    def refund(self, payment_id: int, amount: float) -> None: ...
```

```python
# core/modules/orders/create_order/gateways/notification_gateway.py
from typing import Protocol
from core.modules.orders.generics.entities.order import Order

class NotificationGateway(Protocol):
    def send_order_confirmation(self, order: Order) -> None: ...
```

**Good Naming Examples**:
- ✅ `save()`, `update()`, `find_by_id()`, `fetch_by_customer_id()`
- ✅ `process_payment()`, `send_email()`, `publish_event()`
- ❌ `insert()`, `select()`, `query()` (too implementation-specific)

---

#### 6. Entities (Optional)

**Location**: `entities/{name}.py` or `{module}/generics/entities/{name}.py`

**Purpose**: Represent business concepts with behavior and state.

**Responsibilities**:
- Model domain concepts
- Encapsulate business state
- Provide domain methods
- Ensure invariants

**Rules**:
- ✅ Use snake_case for file names, PascalCase for class names
- ✅ May contain business logic methods
- ✅ Use type hints for all properties
- ✅ Provide setters only when state can change
- ✅ May have a `to_dict()` method for serialization
- ❌ Must NOT contain persistence logic (no database, ORM)
- ❌ Must NOT depend on framework classes

**Example**:

```python
# core/modules/orders/generics/entities/order.py
from datetime import datetime
from typing import Optional
from core.modules.orders.generics.collections.order_item_collection import OrderItemCollection
from core.modules.orders.generics.enums.order_status import OrderStatus
from core.modules.orders.generics.exceptions.order_already_shipped_exception import OrderAlreadyShippedException
import uuid

class Order:
    def __init__(
        self,
        customer_id: int,
        items: OrderItemCollection,
        discount_coupon: Optional[str] = None
    ):
        self.customer_id = customer_id
        self._items = items
        self.discount_coupon = discount_coupon

        self._id: Optional[int] = None
        self._order_number: str = self._generate_order_number()
        self._status: OrderStatus = OrderStatus.PENDING
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = datetime.now()
        self._total_price: float = 0.0
        self._cancellation_reason: Optional[str] = None
        self._cancelled_at: Optional[datetime] = None

    @property
    def id(self) -> Optional[int]:
        return self._id

    def set_id(self, id: int) -> 'Order':
        self._id = id
        return self

    @property
    def order_number(self) -> str:
        return self._order_number

    @property
    def status(self) -> OrderStatus:
        return self._status

    def set_status(self, status: OrderStatus) -> 'Order':
        self._status = status
        return self

    @property
    def items(self) -> OrderItemCollection:
        return self._items

    @property
    def total_price(self) -> float:
        return self._total_price

    def set_total_price(self, total_price: float) -> 'Order':
        self._total_price = total_price
        return self

    def get_subtotal(self) -> float:
        subtotal = 0.0
        for item in self._items:
            subtotal += item.price * item.quantity
        return subtotal

    def has_discount_coupon(self) -> bool:
        return self.discount_coupon is not None

    def get_discount_percentage(self) -> float:
        """Business logic to calculate discount based on coupon"""
        discount_map = {
            'SAVE10': 10.0,
            'SAVE20': 20.0,
        }
        return discount_map.get(self.discount_coupon, 0.0)

    def get_weight(self) -> float:
        weight = 0.0
        for item in self._items:
            weight += item.weight * item.quantity
        return weight

    def mark_as_paid(self) -> 'Order':
        self._status = OrderStatus.PAID
        return self

    def cancel(self) -> 'Order':
        if self._status == OrderStatus.SHIPPED:
            raise OrderAlreadyShippedException(self._id)
        self._status = OrderStatus.CANCELLED
        self._cancelled_at = datetime.now()
        return self

    def set_cancellation_reason(self, reason: str) -> 'Order':
        self._cancellation_reason = reason
        return self

    def get_cancellation_reason(self) -> Optional[str]:
        return self._cancellation_reason

    def get_cancelled_at(self) -> Optional[datetime]:
        return self._cancelled_at

    def _generate_order_number(self) -> str:
        date_str = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:6].upper()
        return f'ORD-{date_str}-{unique_id}'

    def to_dict(self) -> dict:
        return {
            'id': self._id,
            'order_number': self._order_number,
            'customer_id': self.customer_id,
            'status': self._status.value,
            'total_price': self._total_price,
            'items': self._items.to_list(),
            'created_at': self._created_at.isoformat()
        }
```

---

#### 7. Collections (Optional)

**Location**: `collections/{name}_collection.py`

**Purpose**: Type-safe collections of domain entities.

**Responsibilities**:
- Store and iterate over domain entities
- Provide collection operations
- Ensure type safety

**Rules**:
- ✅ Must extend base `Collection` class
- ✅ Must be named `{entity}_collection.py`
- ✅ Constructor should use type hints for type safety
- ✅ May provide custom methods (filter, map, etc.)

**Base Collection Class**:

```python
# core/collection.py
from typing import TypeVar, Generic, Iterator, Callable, List
from abc import ABC

T = TypeVar('T')

class Collection(ABC, Generic[T]):
    def __init__(self):
        self._elements: List[T] = []

    def __iter__(self) -> Iterator[T]:
        return iter(self._elements)

    def is_empty(self) -> bool:
        return len(self._elements) == 0

    def count(self) -> int:
        return len(self._elements)

    def to_list(self) -> List[T]:
        return self._elements.copy()

    def map(self, callback: Callable[[T], any]) -> List[any]:
        return [callback(element) for element in self._elements]

    def filter(self, callback: Callable[[T], bool]) -> 'Collection[T]':
        filtered = [element for element in self._elements if callback(element)]
        new_collection = self.__class__()
        new_collection._elements = filtered
        return new_collection
```

**Example Collection**:

```python
# core/modules/orders/generics/collections/order_item_collection.py
from typing import List, Optional
from core.collection import Collection
from core.modules.orders.generics.entities.order_item import OrderItem

class OrderItemCollection(Collection[OrderItem]):
    def __init__(self, *items: OrderItem):
        super().__init__()
        self._elements = list(items)

    def add(self, item: OrderItem) -> 'OrderItemCollection':
        self._elements.append(item)
        return self

    def get_total_quantity(self) -> int:
        total = 0
        for item in self._elements:
            total += item.quantity
        return total

    def find_by_product_id(self, product_id: int) -> Optional[OrderItem]:
        for item in self._elements:
            if item.product_id == product_id:
                return item
        return None

    def to_list(self) -> List[dict]:
        return [item.to_dict() for item in self._elements]
```

---

#### 8. Exceptions (Optional)

**Location**: `exceptions/{name}_exception.py`

**Purpose**: Domain-specific exceptions that represent business rule violations.

**Responsibilities**:
- Signal domain errors
- Carry context data
- Provide meaningful error messages

**Rules**:
- ✅ Must extend `Exception`
- ✅ Must be named `{context}_exception.py`
- ✅ May carry domain data as attributes
- ✅ Should have descriptive messages

**Example**:

```python
# core/modules/orders/create_order/exceptions/duplicate_order_exception.py
class DuplicateOrderException(Exception):
    def __init__(self, order_number: str):
        self.order_number = order_number
        super().__init__(f'Order with number "{order_number}" already exists')
```

```python
# core/modules/orders/create_order/exceptions/minimum_order_amount_exception.py
class MinimumOrderAmountException(Exception):
    def __init__(self, minimum_amount: float):
        self.minimum_amount = minimum_amount
        super().__init__(f'Order must be at least ${minimum_amount:.2f}')
```

```python
# core/modules/orders/create_order/exceptions/payment_failed_exception.py
class PaymentFailedException(Exception):
    def __init__(self, reason: str, transaction_id: str):
        self.reason = reason
        self.transaction_id = transaction_id
        super().__init__(f'Payment failed: {reason} (Transaction: {transaction_id})')
```

---

#### 9. Events (Optional)

**Location**: `core/events/{name}_event.py`

**Purpose**: Represent significant domain events that have occurred.

**Responsibilities**:
- Capture business events
- Carry event data
- Provide serialization for event publishing

**Rules**:
- ✅ Should extend base `Message` class
- ✅ Must be named `{action}_event.py` (past tense)
- ✅ Should be immutable (use `@dataclass(frozen=True)`)

**Base Message Class**:

```python
# core/events/message.py
from abc import ABC

class Message(ABC):
    def __init__(self, source: str, type: str, version: int, data: dict):
        self._source = source
        self._type = type
        self._version = version
        self._data = data

    @property
    def source(self) -> str:
        return self._source

    @property
    def type(self) -> str:
        return self._type

    @property
    def version(self) -> int:
        return self._version

    @property
    def data(self) -> dict:
        return self._data
```

**Example Event**:

```python
# core/events/order_was_created_event.py
from core.events.message import Message
from core.modules.orders.generics.entities.order import Order

class OrderWasCreatedEvent(Message):
    SOURCE = 'order-service'
    VERSION = 1
    TYPE = 'order-was-created'

    def __init__(self, order: Order):
        super().__init__(
            self.SOURCE,
            self.TYPE,
            self.VERSION,
            self._build_data(order)
        )

    def _build_data(self, order: Order) -> dict:
        return {
            'order_id': order.id,
            'order_number': order.order_number,
            'customer_id': order.customer_id,
            'total_price': order.total_price,
            'status': order.status.value,
            'created_at': order.to_dict()['created_at']
        }
```

---

## Infrastructure Layer

The Infrastructure layer contains **framework-specific** code that implements the protocols defined in the Core layer.

### Infrastructure Components

#### 1. Controllers

**Location**: `infrastructure/http/controllers/{name}_controller.py`

**Purpose**: HTTP entry points that handle requests and responses.

**Responsibilities**:
- Receive HTTP requests
- Validate input (using framework validators like Pydantic)
- Instantiate UseCase with dependencies
- Create Input DTO
- Call UseCase
- Transform Response to HTTP format
- Handle exceptions

**Rules**:
- ✅ Must validate input using framework validators
- ✅ Must instantiate UseCase in method (not `__init__`)
- ✅ Must use Factories to create domain objects
- ✅ Must use ResponseFactory or Presenters to transform responses
- ✅ Must catch and log exceptions
- ❌ Should NOT contain business logic
- ❌ Should NOT directly access ORM models in business flow

**Example (FastAPI)**:

```python
# infrastructure/http/controllers/order_controller.py
from fastapi import APIRouter, Depends, HTTPException
from infrastructure.adapters.orders.order_adapter import OrderAdapter
from infrastructure.adapters.orders.payment_adapter import PaymentAdapter
from infrastructure.factories.orders.order_factory import OrderFactory
from infrastructure.factories.orders.create_order.create_order_response_factory import CreateOrderResponseFactory
from infrastructure.http.schemas.create_order_schema import CreateOrderSchema
from core.modules.orders.create_order.create_order_use_case import CreateOrderUseCase
from core.modules.orders.create_order.inputs.create_order_input import CreateOrderInput
from core.dependencies.log_interface import LogInterface
from infrastructure.adapters.logger.logger_adapter import get_logger

router = APIRouter()

@router.post('/orders')
def create_order(
    schema: CreateOrderSchema,
    logger: LogInterface = Depends(get_logger)
):
    logger.info('[HTTP] Create order request received')

    try:
        # 1. Instantiate UseCase with Adapters
        use_case = CreateOrderUseCase(
            OrderAdapter(),
            PaymentAdapter(),
            logger
        )

        # 2. Create domain Input from HTTP data
        order = OrderFactory.create_from_dict(schema.dict())
        use_case_input = CreateOrderInput(
            order=order,
            customer_id=schema.customer_id,
            payment_method=schema.payment_method
        )

        # 3. Execute UseCase
        response = use_case.execute(use_case_input)

        # 4. Transform domain Response to HTTP Response
        return CreateOrderResponseFactory.to_http(response)

    except Exception as exception:
        logger.error('[HTTP] Unexpected error', {'exception': str(exception)})
        raise HTTPException(status_code=500, detail='Internal server error')
```

---

#### 2. Adapters (Ports & Adapters)

**Location**: `infrastructure/adapters/{module}/{name}_adapter.py`

**Purpose**: Implement Gateway protocols defined in Core layer. These are the **ADAPTERS** in Hexagonal Architecture.

**Responsibilities**:
- Implement Gateway protocols
- Access databases (using ORM)
- Call external APIs
- Publish events
- Transform between domain entities and infrastructure models

**Rules**:
- ✅ Must implement a Gateway protocol from Core layer
- ✅ Must be named `{resource}_adapter.py`
- ✅ May use framework features (ORM, HTTP client, etc.)
- ✅ Must convert ORM models to domain Entities
- ✅ Must convert domain Entities to ORM models
- ❌ Must NOT leak framework types into domain layer
- ❌ Must NOT contain business logic

**Example - Database Adapter (SQLAlchemy)**:

```python
# infrastructure/adapters/orders/order_adapter.py
from typing import Optional
from sqlalchemy.orm import Session
from infrastructure.models.order import Order as OrderModel
from infrastructure.models.order_item import OrderItem as OrderItemModel
from infrastructure.factories.orders.order_factory import OrderFactory
from core.modules.orders.create_order.gateways.order_gateway import OrderGateway
from core.modules.orders.generics.entities.order import Order
from infrastructure.database import get_db

class OrderAdapter:
    """Implements OrderGateway protocol using SQLAlchemy ORM"""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def save(self, order: Order) -> Order:
        # Convert domain Entity to ORM model
        order_model = OrderModel(
            order_number=order.order_number,
            customer_id=order.customer_id,
            status=order.status.value,
            total_price=order.total_price,
            discount_coupon=order.discount_coupon
        )
        self.db.add(order_model)
        self.db.commit()

        # Save order items
        for item in order.items:
            item_model = OrderItemModel(
                order_id=order_model.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price
            )
            self.db.add(item_model)

        self.db.commit()
        self.db.refresh(order_model)

        # Enrich domain Entity with persisted data
        order.set_id(order_model.id)

        return order

    def exists(self, order_number: str) -> bool:
        return self.db.query(OrderModel).filter(
            OrderModel.order_number == order_number
        ).first() is not None

    def find_by_id(self, id: int) -> Optional[Order]:
        order_model = self.db.query(OrderModel).filter(
            OrderModel.id == id
        ).first()

        if not order_model:
            return None

        # Convert ORM model to domain Entity
        return OrderFactory.create_from_model(order_model)
```

**Example - External API Adapter**:

```python
# infrastructure/adapters/orders/payment_adapter.py
import httpx
from core.modules.orders.create_order.gateways.payment_gateway import PaymentGateway
from core.modules.orders.create_order.exceptions.payment_failed_exception import PaymentFailedException
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.generics.entities.payment import Payment
from core.modules.orders.generics.enums.payment_status import PaymentStatus

class PaymentAdapter:
    """Implements PaymentGateway protocol using external payment API"""

    def __init__(self, api_url: str = "https://payment-api.example.com"):
        self.api_url = api_url
        self.client = httpx.Client()

    def process_payment(self, order: Order, payment_method: str) -> Payment:
        try:
            response = self.client.post(
                f'{self.api_url}/payments',
                json={
                    'amount': order.total_price,
                    'currency': 'USD',
                    'payment_method': payment_method,
                    'order_id': order.id,
                    'customer_id': order.customer_id
                }
            )
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'success':
                raise PaymentFailedException(
                    data['error_message'],
                    data['transaction_id']
                )

            return Payment(
                transaction_id=data['transaction_id'],
                amount=order.total_price,
                payment_method=payment_method,
                status=PaymentStatus.COMPLETED
            )

        except httpx.HTTPError as e:
            raise PaymentFailedException(
                'Payment service unavailable',
                ''
            )

    def refund(self, payment_id: int, amount: float) -> None:
        self.client.post(
            f'{self.api_url}/refunds',
            json={'payment_id': payment_id, 'amount': amount}
        )
```

**Example - Event Publisher Adapter**:

```python
# infrastructure/adapters/event_publisher/event_publisher_adapter.py
from core.events.message import Message
from core.dependencies.event_publisher_interface import EventPublisherInterface
from infrastructure.queue.message_broker import MessageBroker

class EventPublisherAdapter:
    """Implements EventPublisherInterface using message broker"""

    def __init__(self, broker: MessageBroker, topic_name: str):
        self.broker = broker
        self.topic_name = topic_name

    def publish(self, event: Message, key: str = None) -> None:
        import time

        self.broker.send(
            self.topic_name,
            {
                'source': event.source,
                'type': event.type,
                'version': event.version,
                'data': event.data,
                'timestamp': int(time.time())
            },
            key
        )
```

---

#### 3. Factories

**Location**: `infrastructure/factories/{module}/{name}_factory.py`

**Purpose**: Create domain objects from infrastructure data.

**Responsibilities**:
- Transform HTTP request data into domain Entities
- Create complex domain object graphs
- Handle optional parameters and defaults

**Rules**:
- ✅ Must have static `create()` or `create_from_dict()` method
- ✅ Must return domain objects (Entities, Collections)
- ✅ May accept infrastructure types as input (dicts, DTOs)
- ❌ Must NOT contain business logic

**Example**:

```python
# infrastructure/factories/orders/order_factory.py
from typing import Dict, Any
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.generics.entities.order_item import OrderItem
from core.modules.orders.generics.collections.order_item_collection import OrderItemCollection
from infrastructure.models.order import Order as OrderModel

class OrderFactory:
    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> Order:
        items = OrderItemCollection()

        for item_data in data['items']:
            item = OrderItem(
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            items.add(item)

        return Order(
            customer_id=data['customer_id'],
            items=items,
            discount_coupon=data.get('discount_coupon')
        )

    @staticmethod
    def create_from_model(model: OrderModel) -> Order:
        items = OrderItemCollection()

        for item_model in model.items:
            item = OrderItem(
                product_id=item_model.product_id,
                quantity=item_model.quantity,
                price=item_model.price
            )
            item.set_id(item_model.id)
            items.add(item)

        order = Order(
            customer_id=model.customer_id,
            items=items,
            discount_coupon=model.discount_coupon
        )

        order.set_id(model.id)
        order.set_status(OrderStatus(model.status))
        order.set_total_price(model.total_price)

        return order
```

---

#### 4. Presenters

**Location**: `infrastructure/presenters/{module}/{use_case}/{name}_presenter.py`

**Purpose**: Transform domain responses into HTTP response format.

**Responsibilities**:
- Convert domain entities to dicts/JSON
- Format dates, numbers, currencies
- Structure response payload

**Rules**:
- ✅ Must implement `Presenter` protocol (if using one)
- ✅ Must have a `present()` or `to_dict()` method
- ✅ Accept domain objects (Entities, Responses) in `__init__`
- ❌ Must NOT contain business logic

**Presenter Protocol**:

```python
# infrastructure/presenters/presenter.py
from typing import Protocol, Dict, Any

class Presenter(Protocol):
    def to_dict(self) -> Dict[str, Any]: ...
```

**Example**:

```python
# infrastructure/presenters/orders/create_order/create_order_success_presenter.py
from typing import Dict, Any, List
from core.modules.orders.generics.entities.order import Order

class CreateOrderSuccessPresenter:
    def __init__(self, order: Order):
        self.order = order

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': True,
            'message': 'Order created successfully',
            'data': {
                'order': {
                    'id': self.order.id,
                    'order_number': self.order.order_number,
                    'customer_id': self.order.customer_id,
                    'status': self.order.status.value,
                    'total_price': self._format_price(self.order.total_price),
                    'items': self._format_items(self.order.items),
                    'created_at': self.order.to_dict()['created_at']
                }
            }
        }

    def _format_price(self, price: float) -> str:
        return f'${price:.2f}'

    def _format_items(self, items) -> List[Dict[str, Any]]:
        formatted = []
        for item in items:
            formatted.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': self._format_price(item.price),
                'subtotal': self._format_price(item.price * item.quantity)
            })
        return formatted
```

---

#### 5. ResponseFactory

**Location**: `infrastructure/factories/{module}/{use_case}/response_factory.py`

**Purpose**: Convert domain Responses to HTTP responses.

**Responsibilities**:
- Route different Response types to appropriate Presenters
- Map domain exceptions to HTTP status codes
- Create framework response objects

**Rules**:
- ✅ Must have static method (e.g., `to_http()`, `create()`)
- ✅ Accept domain `Response` as parameter
- ✅ Return framework response object
- ✅ Use Presenters to format data

**Example (FastAPI)**:

```python
# infrastructure/factories/orders/create_order/create_order_response_factory.py
from fastapi.responses import JSONResponse
from infrastructure.presenters.orders.create_order.create_order_success_presenter import CreateOrderSuccessPresenter
from core.modules.orders.create_order.responses.create_order_response import CreateOrderResponse
from core.modules.orders.create_order.responses.create_order_success import CreateOrderSuccess
from core.modules.orders.create_order.responses.create_order_error import CreateOrderError
from core.modules.orders.create_order.exceptions.duplicate_order_exception import DuplicateOrderException
from core.modules.orders.create_order.exceptions.payment_failed_exception import PaymentFailedException

class CreateOrderResponseFactory:
    @staticmethod
    def to_http(response: CreateOrderResponse) -> JSONResponse:
        if isinstance(response, CreateOrderSuccess):
            presenter = CreateOrderSuccessPresenter(response.order)
            return JSONResponse(content=presenter.to_dict(), status_code=201)

        if isinstance(response, CreateOrderError):
            return CreateOrderResponseFactory._handle_error(response.throwable)

        return JSONResponse(
            content={'error': 'Internal server error'},
            status_code=500
        )

    @staticmethod
    def _handle_error(throwable: Exception) -> JSONResponse:
        if isinstance(throwable, DuplicateOrderException):
            return JSONResponse(
                content={
                    'success': False,
                    'error': 'Order already exists',
                    'message': str(throwable)
                },
                status_code=409
            )

        if isinstance(throwable, PaymentFailedException):
            return JSONResponse(
                content={
                    'success': False,
                    'error': 'Payment failed',
                    'message': str(throwable)
                },
                status_code=402
            )

        return JSONResponse(
            content={
                'success': False,
                'error': 'Bad request',
                'message': str(throwable)
            },
            status_code=400
        )
```

---

#### 6. Models (ORM)

**Location**: `infrastructure/models/{name}.py`

**Purpose**: Database access layer using ORM.

**Responsibilities**:
- Define database table mapping
- Define relationships
- Provide query scopes

**Rules**:
- ✅ Only used within Adapters
- ✅ Never exposed to Core layer
- ❌ Must NOT contain business logic

**Example (SQLAlchemy)**:

```python
# infrastructure/models/order.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False)
    customer_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    discount_coupon = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship('OrderItem', back_populates='order')
```

```python
# infrastructure/models/order_item.py
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database import Base

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
    order = relationship('Order', back_populates='items')
```

---

#### 7. Queue/Event Consumers

**Location**: `infrastructure/queue/{context}/{name}_consumer.py`

**Purpose**: Listen to queue messages/events and trigger UseCases.

**Responsibilities**:
- Consume messages from queue
- Deserialize messages
- Create Input DTOs
- Execute UseCases

**Rules**:
- ✅ Similar flow to Controllers (entry point → UseCase → response)
- ✅ Must handle deserialization errors
- ✅ Must log processing

**Example**:

```python
# infrastructure/queue/orders/payment_confirmed_consumer.py
from typing import Dict, Any
from infrastructure.adapters.orders.order_adapter import OrderAdapter
from core.modules.orders.process_payment.process_payment_use_case import ProcessPaymentUseCase
from core.modules.orders.process_payment.inputs.process_payment_input import ProcessPaymentInput
from core.dependencies.log_interface import LogInterface

class PaymentConfirmedConsumer:
    def __init__(self, logger: LogInterface):
        self.logger = logger

    def handle(self, message: Dict[str, Any]) -> None:
        self.logger.info('[Queue] Payment confirmed message received', {
            'order_id': message['order_id']
        })

        try:
            use_case = ProcessPaymentUseCase(
                OrderAdapter(),
                self.logger
            )

            input_data = ProcessPaymentInput(
                order_id=message['order_id'],
                transaction_id=message['transaction_id'],
                amount=message['amount']
            )

            use_case.execute(input_data)

            self.logger.info('[Queue] Payment processed successfully')

        except Exception as exception:
            self.logger.error('[Queue] Failed to process payment', {
                'exception': str(exception)
            })
            raise  # Re-raise to trigger retry mechanism
```

---

## Naming Conventions

### Design Philosophy

The naming convention prioritizes:
1. **Self-Documentation**: Names should clearly convey purpose
2. **IDE Navigation**: Unique names for better search and autocomplete
3. **Consistency**: Similar components follow the same patterns
4. **Clarity**: Avoid generic names that require context
5. **Python Standards**: Follow PEP 8 naming conventions

---

### Module Names

- **Format**: snake_case, plural
- **Purpose**: Represent bounded contexts/domains
- **Examples**: `orders`, `products`, `users`, `payments`, `inventory`

**Rationale**: Plural form represents the domain (e.g., "orders" domain contains all order-related operations)

---

### UseCase Directory Names

- **Format**: snake_case, verb + noun
- **Purpose**: Describe the business operation
- **Examples**: `create_order`, `cancel_order`, `update_stock`, `register_user`, `process_payment`

**Rationale**: Action-oriented names make the business capability clear

---

### File Naming Patterns

| Component | Pattern | Example | Notes |
|-----------|---------|---------|-------|
| **UseCase** | `{use_case}_use_case.py` | `create_order_use_case.py` | ✨ Full name for better IDE navigation |
| **Input** | `{use_case}_input.py` | `create_order_input.py` | ✨ Self-documenting imports |
| **Response** | `{use_case}_{type}.py` | `create_order_success.py`<br>`create_order_error.py` | ✨ Shorter, clear |
| **Action** | `{action}_action.py` | `calculate_total_price_action.py`<br>`validate_order_data_action.py` | Business operation units |
| **Gateway** | `{resource}_gateway.py` | `order_gateway.py`<br>`payment_gateway.py` | Protocol definition |
| **Adapter** | `{resource}_adapter.py` | `order_adapter.py`<br>`payment_adapter.py` | Implementation |
| **Entity** | `{name}.py` | `order.py`, `customer.py` | Singular, domain object |
| **Collection** | `{entity}_collection.py` | `order_item_collection.py` | Type-safe collections |
| **Exception** | `{context}_exception.py` | `order_not_found_exception.py`<br>`duplicate_order_exception.py` | Descriptive, specific |
| **Event** | `{subject}_{action}_event.py` | `order_was_created_event.py`<br>`payment_was_processed_event.py` | Past tense |
| **Presenter** | `{use_case}_{type}_presenter.py` | `create_order_success_presenter.py` | ✨ Context included |
| **Factory** | `{resource}_factory.py`<br>`{use_case}_response_factory.py` | `order_factory.py`<br>`create_order_response_factory.py` | Purpose-specific |

**✨ = Improved from basic conventions for better developer experience**

---

### Class Naming Conventions

Python classes use **PascalCase** (following PEP 8):

```python
# ✅ Good: PascalCase for classes
class CreateOrderUseCase:
    pass

class CreateOrderInput:
    pass

class OrderGateway(Protocol):
    pass

# ✅ Good: snake_case for modules/files
# create_order_use_case.py
# create_order_input.py
# order_gateway.py
```

---

### Import Examples

With improved naming, imports are self-documenting:

```python
# ✅ Clear what each import is for
from core.modules.orders.create_order.create_order_use_case import CreateOrderUseCase
from core.modules.orders.create_order.inputs.create_order_input import CreateOrderInput
from core.modules.orders.create_order.responses.create_order_success import CreateOrderSuccess
from core.modules.orders.create_order.actions.calculate_total_price_action import CalculateTotalPriceAction
from core.modules.orders.create_order.gateways.order_gateway import OrderGateway
from infrastructure.adapters.orders.order_adapter import OrderAdapter

# ❌ Compare to generic naming (avoid this)
from core.modules.orders.create_order.use_case import UseCase  # UseCase for what?
from core.modules.orders.create_order.inputs.input import Input  # Input for what?
from core.modules.orders.create_order.responses.success import Success  # Success of what?
```

---

## Dependency Rules

### ✅ Allowed Dependencies

```
Controllers → Adapters → External Systems (Database, APIs)
Controllers → Factories → Entities
Controllers → UseCases (injection)
Controllers → ResponseFactory → Presenters

Adapters → ORM Models
Adapters → External Libraries
Adapters → Gateway Protocols (implements)

UseCases → Actions
UseCases → Gateway Protocols (injection)
UseCases → Entities
UseCases → Input/Response DTOs
UseCases → Shared Dependencies (LogInterface, etc.)

Actions → Gateway Protocols
Actions → Entities
Actions → Exceptions

Entities → Collections
Entities → Value Objects

Everything → Python standard library
```

### ❌ Forbidden Dependencies

```
core/ → infrastructure/ (NEVER!)
core/ → Framework (NEVER!)
core/ → ORM Models (NEVER!)
core/ → HTTP (Request, Response classes)
core/ → Concrete implementations (only protocols)

Entities → Gateways (Entities should not depend on infrastructure)
```

---

## Dependency Injection

### Constructor Injection Pattern

**In UseCases (Core)**:
- Inject **Protocols** (Gateways, LogInterface, etc.)
- Instantiate Actions in `__init__`

```python
class CreateOrderUseCase:
    def __init__(
        self,
        gateway: OrderGateway,    # ← Protocol
        logger: LogInterface      # ← Protocol
    ):
        self.action = CalculateTotalPriceAction(gateway)
        self.logger = logger
```

**In Controllers (Infrastructure)**:
- Instantiate UseCases with **Concrete Adapters**
- Use framework's dependency injection for shared dependencies

```python
def create_order(
    request: CreateOrderSchema,
    logger: LogInterface = Depends(get_logger)
):
    use_case = CreateOrderUseCase(
        OrderAdapter(),           # ← Concrete implementation
        logger                    # ← From DI container
    )
```

---

## Implementation Guide

### Step-by-Step: Creating a New UseCase

This guide demonstrates how to implement a complete use case from scratch, following all architectural patterns and best practices.

#### Example: CancelOrder Use Case

**Business Requirements**:
- Users can cancel their orders
- Orders that have been shipped cannot be cancelled
- System must record the cancellation reason
- System must update order status to "cancelled"

---

### Step 1: Define Domain Structure (Core Layer)

#### 1.1 Create Directory Structure

```
core/modules/orders/cancel_order/
├── cancel_order_use_case.py
├── inputs/
│   └── cancel_order_input.py
├── responses/
│   ├── cancel_order_response.py
│   ├── cancel_order_success.py
│   └── cancel_order_error.py
├── actions/
│   ├── fetch_order_action.py
│   ├── validate_order_can_be_cancelled_action.py
│   └── cancel_order_action.py
├── gateways/
│   └── order_gateway.py
└── exceptions/
    ├── order_not_found_exception.py
    └── order_already_shipped_exception.py
```

#### 1.2 Create Gateway Protocol

File: `core/modules/orders/cancel_order/gateways/order_gateway.py`

```python
from typing import Protocol, Optional
from core.modules.orders.generics.entities.order import Order

class OrderGateway(Protocol):
    def find_by_id(self, id: int) -> Optional[Order]: ...
    def update(self, order: Order) -> Order: ...
```

#### 1.3 Create Input DTO

File: `core/modules/orders/cancel_order/inputs/cancel_order_input.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CancelOrderInput:
    order_id: int
    user_id: int
    cancellation_reason: str
```

#### 1.4 Create Response DTOs

File: `core/modules/orders/cancel_order/responses/cancel_order_response.py`

```python
from abc import ABC

class CancelOrderResponse(ABC):
    pass
```

File: `core/modules/orders/cancel_order/responses/cancel_order_success.py`

```python
from dataclasses import dataclass
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.cancel_order.responses.cancel_order_response import CancelOrderResponse

@dataclass(frozen=True)
class CancelOrderSuccess(CancelOrderResponse):
    order: Order
```

File: `core/modules/orders/cancel_order/responses/cancel_order_error.py`

```python
from dataclasses import dataclass
from core.modules.orders.cancel_order.responses.cancel_order_response import CancelOrderResponse

@dataclass(frozen=True)
class CancelOrderError(CancelOrderResponse):
    throwable: Exception
```

#### 1.5 Create Domain Exceptions

File: `core/modules/orders/cancel_order/exceptions/order_not_found_exception.py`

```python
class OrderNotFoundException(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f'Order with ID {order_id} not found')
```

File: `core/modules/orders/cancel_order/exceptions/order_already_shipped_exception.py`

```python
class OrderAlreadyShippedException(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f'Order {order_id} has already been shipped and cannot be cancelled')
```

#### 1.6 Create Business Actions

File: `core/modules/orders/cancel_order/actions/fetch_order_action.py`

```python
from core.modules.orders.cancel_order.gateways.order_gateway import OrderGateway
from core.modules.orders.cancel_order.exceptions.order_not_found_exception import OrderNotFoundException
from core.modules.orders.generics.entities.order import Order

class FetchOrderAction:
    def __init__(self, order_gateway: OrderGateway):
        self.order_gateway = order_gateway

    def apply(self, order_id: int) -> Order:
        order = self.order_gateway.find_by_id(order_id)

        if order is None:
            raise OrderNotFoundException(order_id)

        return order
```

File: `core/modules/orders/cancel_order/actions/validate_order_can_be_cancelled_action.py`

```python
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.generics.enums.order_status import OrderStatus
from core.modules.orders.cancel_order.exceptions.order_already_shipped_exception import OrderAlreadyShippedException

class ValidateOrderCanBeCancelledAction:
    def apply(self, order: Order) -> None:
        if order.status == OrderStatus.SHIPPED:
            raise OrderAlreadyShippedException(order.id)

        if order.status == OrderStatus.DELIVERED:
            raise OrderAlreadyShippedException(order.id)
```

File: `core/modules/orders/cancel_order/actions/cancel_order_action.py`

```python
from core.modules.orders.cancel_order.gateways.order_gateway import OrderGateway
from core.modules.orders.generics.entities.order import Order

class CancelOrderAction:
    def __init__(self, order_gateway: OrderGateway):
        self.order_gateway = order_gateway

    def apply(self, order: Order, reason: str) -> Order:
        order.cancel()
        order.set_cancellation_reason(reason)

        return self.order_gateway.update(order)
```

#### 1.7 Create UseCase

File: `core/modules/orders/cancel_order/cancel_order_use_case.py`

```python
from core.dependencies.log_interface import LogInterface
from core.modules.orders.cancel_order.gateways.order_gateway import OrderGateway
from core.modules.orders.cancel_order.inputs.cancel_order_input import CancelOrderInput
from core.modules.orders.cancel_order.responses.cancel_order_response import CancelOrderResponse
from core.modules.orders.cancel_order.responses.cancel_order_success import CancelOrderSuccess
from core.modules.orders.cancel_order.responses.cancel_order_error import CancelOrderError
from core.modules.orders.cancel_order.actions.fetch_order_action import FetchOrderAction
from core.modules.orders.cancel_order.actions.validate_order_can_be_cancelled_action import ValidateOrderCanBeCancelledAction
from core.modules.orders.cancel_order.actions.cancel_order_action import CancelOrderAction
from core.modules.orders.cancel_order.exceptions.order_not_found_exception import OrderNotFoundException
from core.modules.orders.cancel_order.exceptions.order_already_shipped_exception import OrderAlreadyShippedException

class CancelOrderUseCase:
    def __init__(
        self,
        order_gateway: OrderGateway,
        logger: LogInterface
    ):
        self.fetch_order_action = FetchOrderAction(order_gateway)
        self.validate_order_can_be_cancelled_action = ValidateOrderCanBeCancelledAction()
        self.cancel_order_action = CancelOrderAction(order_gateway)
        self.logger = logger

    def execute(self, input_data: CancelOrderInput) -> CancelOrderResponse:
        self.logger.info('[CancelOrder] Init Use Case', {
            'order_id': input_data.order_id,
            'user_id': input_data.user_id
        })

        try:
            # 1. Fetch order
            order = self.fetch_order_action.apply(input_data.order_id)

            # 2. Validate order can be cancelled
            self.validate_order_can_be_cancelled_action.apply(order)

            # 3. Cancel order
            cancelled_order = self.cancel_order_action.apply(
                order,
                input_data.cancellation_reason
            )

            self.logger.info('[CancelOrder] Finish Use Case', {
                'order_id': cancelled_order.id
            })

            return CancelOrderSuccess(order=cancelled_order)

        except (OrderNotFoundException, OrderAlreadyShippedException) as exception:
            self.logger.error('[CancelOrder] Domain error', {
                'exception': str(exception)
            })

            return CancelOrderError(throwable=exception)
```

---

### Step 2: Implement Infrastructure Layer

#### 2.1 Create Adapter

File: `infrastructure/adapters/orders/cancel_order/order_adapter.py`

```python
from typing import Optional
from sqlalchemy.orm import Session
from infrastructure.models.order import Order as OrderModel
from infrastructure.factories.orders.order_factory import OrderFactory
from core.modules.orders.cancel_order.gateways.order_gateway import OrderGateway
from core.modules.orders.generics.entities.order import Order

class OrderAdapter:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> Optional[Order]:
        order_model = self.db.query(OrderModel).filter(
            OrderModel.id == id
        ).first()

        if not order_model:
            return None

        return OrderFactory.create_from_model(order_model)

    def update(self, order: Order) -> Order:
        order_model = self.db.query(OrderModel).filter(
            OrderModel.id == order.id
        ).first()

        order_model.status = order.status.value
        order_model.cancellation_reason = order.get_cancellation_reason()
        order_model.cancelled_at = order.get_cancelled_at()

        self.db.commit()
        self.db.refresh(order_model)

        return order
```

#### 2.2 Create Presenters

File: `infrastructure/presenters/orders/cancel_order/cancel_order_success_presenter.py`

```python
from typing import Dict, Any
from core.modules.orders.generics.entities.order import Order

class CancelOrderSuccessPresenter:
    def __init__(self, order: Order):
        self.order = order

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': True,
            'message': 'Order cancelled successfully',
            'data': {
                'order_id': self.order.id,
                'order_number': self.order.order_number,
                'status': self.order.status.value,
                'cancelled_at': self.order.get_cancelled_at().isoformat()
            }
        }
```

#### 2.3 Create ResponseFactory

File: `infrastructure/factories/orders/cancel_order/cancel_order_response_factory.py`

```python
from fastapi.responses import JSONResponse
from infrastructure.presenters.orders.cancel_order.cancel_order_success_presenter import CancelOrderSuccessPresenter
from core.modules.orders.cancel_order.responses.cancel_order_response import CancelOrderResponse
from core.modules.orders.cancel_order.responses.cancel_order_success import CancelOrderSuccess
from core.modules.orders.cancel_order.responses.cancel_order_error import CancelOrderError
from core.modules.orders.cancel_order.exceptions.order_not_found_exception import OrderNotFoundException
from core.modules.orders.cancel_order.exceptions.order_already_shipped_exception import OrderAlreadyShippedException

class CancelOrderResponseFactory:
    @staticmethod
    def to_http(response: CancelOrderResponse) -> JSONResponse:
        if isinstance(response, CancelOrderSuccess):
            presenter = CancelOrderSuccessPresenter(response.order)
            return JSONResponse(content=presenter.to_dict(), status_code=200)

        if isinstance(response, CancelOrderError):
            if isinstance(response.throwable, OrderNotFoundException):
                return JSONResponse(
                    content={
                        'success': False,
                        'error': 'Order not found'
                    },
                    status_code=404
                )

            if isinstance(response.throwable, OrderAlreadyShippedException):
                return JSONResponse(
                    content={
                        'success': False,
                        'error': 'Cannot cancel shipped order',
                        'message': str(response.throwable)
                    },
                    status_code=422
                )

            return JSONResponse(
                content={
                    'success': False,
                    'error': 'Internal server error'
                },
                status_code=500
            )

        return JSONResponse(
            content={'error': 'Internal server error'},
            status_code=500
        )
```

#### 2.4 Add Controller Method

File: `infrastructure/http/controllers/order_controller.py`

```python
from fastapi import APIRouter, Depends
from infrastructure.adapters.orders.cancel_order.order_adapter import OrderAdapter
from infrastructure.factories.orders.cancel_order.cancel_order_response_factory import CancelOrderResponseFactory
from infrastructure.http.schemas.cancel_order_schema import CancelOrderSchema
from core.modules.orders.cancel_order.cancel_order_use_case import CancelOrderUseCase
from core.modules.orders.cancel_order.inputs.cancel_order_input import CancelOrderInput
from core.dependencies.log_interface import LogInterface
from infrastructure.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post('/orders/{order_id}/cancel')
def cancel_order(
    order_id: int,
    schema: CancelOrderSchema,
    db: Session = Depends(get_db),
    logger: LogInterface = Depends(get_logger)
):
    logger.info('[HTTP] Cancel order request', {'order_id': order_id})

    try:
        use_case = CancelOrderUseCase(
            OrderAdapter(db),
            logger
        )

        use_case_input = CancelOrderInput(
            order_id=order_id,
            user_id=1,  # Get from auth
            cancellation_reason=schema.reason
        )

        response = use_case.execute(use_case_input)

        return CancelOrderResponseFactory.to_http(response)

    except Exception as exception:
        logger.error('[HTTP] Unexpected error', {'exception': str(exception)})
        raise HTTPException(status_code=500, detail='Internal server error')
```

---

## Best Practices

### 1. Keep UseCases Focused

✅ **Good**: One UseCase per business operation
```
create_order/
cancel_order/
update_order_shipping_address/
list_orders/
```

❌ **Bad**: Generic CRUD UseCase
```
order_crud/  # Too generic!
```

### 2. Make Actions Single-Purpose

✅ **Good**: Small, testable actions
```python
ValidateOrderDataAction
CalculateTotalPriceAction
ProcessPaymentAction
SaveOrderAction
SendConfirmationEmailAction
```

❌ **Bad**: Large action doing multiple things
```python
CreateOrderAndProcessPaymentAndSendEmailAction  # Too much!
```

### 3. Use Frozen Dataclasses for DTOs

✅ **Good**: Immutable DTOs
```python
@dataclass(frozen=True)
class CreateOrderInput:
    order: Order
    customer_id: int
```

❌ **Bad**: Mutable DTOs
```python
@dataclass
class CreateOrderInput:
    order: Order  # Can be changed!
    customer_id: int
```

### 4. Always Use Type Hints

✅ **Good**: Explicit types
```python
def apply(self, order: Order) -> Order:
    return self.order_gateway.save(order)
```

❌ **Bad**: Missing types
```python
def apply(self, order):  # What type is this?
    return self.order_gateway.save(order)
```

### 5. Log at UseCase Level

✅ **Good**: Log in UseCase
```python
class CreateOrderUseCase:
    def execute(self, input_data: CreateOrderInput) -> CreateOrderResponse:
        self.logger.info('[UseCase] Init')
        # ...
        self.logger.info('[UseCase] Finish')
```

❌ **Bad**: Don't log in Actions (keep them pure and testable)

### 6. Handle Exceptions in UseCase

✅ **Good**: Catch domain exceptions and return ErrorResponse
```python
try:
    self.validate_rule.apply(order)
    return CreateOrderSuccess(order=order)
except ValidationException as e:
    return CreateOrderError(throwable=e)
```

❌ **Bad**: Let exceptions bubble up unhandled

### 7. Use Factories for Complex Object Creation

✅ **Good**: Use Factory when creating complex domain objects
```python
order = OrderFactory.create_from_dict(request.dict())
```

❌ **Bad**: Manually instantiate complex objects in Controller
```python
order = Order(
    request.customer_id,
    OrderItemCollection(
        OrderItem(...),
        OrderItem(...)
    )
)  # Too complex!
```

### 8. Keep Adapters Simple

✅ **Good**: Adapters only do infrastructure work
```python
def save(self, order: Order) -> Order:
    model = OrderModel(**order.to_dict())
    self.db.add(model)
    self.db.commit()
    order.set_id(model.id)
    return order
```

❌ **Bad**: Adapters with business logic
```python
def save(self, order: Order) -> Order:
    # ❌ Business logic in adapter!
    if order.total_price > 1000:
        order.apply_vip_discount()
    model.save()
    return order
```

### 9. Never Expose ORM Models to Core

✅ **Good**: Convert models to entities in Adapter
```python
# In Adapter
def find_by_id(self, id: int) -> Optional[Order]:
    model = OrderModel.query.get(id)
    return OrderFactory.create_from_model(model) if model else None  # ✅
```

❌ **Bad**: Return ORM model
```python
# In Adapter (Gateway implementation)
def find_by_id(self, id: int) -> Optional[Order]:
    return OrderModel.query.get(id)  # ❌ Returns SQLAlchemy model!
```

### 10. Test Core Without Infrastructure

✅ **Good**: Mock Gateways in tests
```python
mock_gateway = Mock(spec=OrderGateway)
mock_gateway.save.return_value = order

use_case = CreateOrderUseCase(mock_gateway, mock_logger)
response = use_case.execute(input_data)

assert isinstance(response, CreateOrderSuccess)
```

---

## Testing Strategy

### Unit Tests (Core Layer)

Test business logic in isolation by mocking Gateways.

**Testing Actions**:
```python
# tests/unit/core/modules/orders/create_order/actions/test_calculate_total_price_action.py
import pytest
from core.modules.orders.create_order.actions.calculate_total_price_action import CalculateTotalPriceAction
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.generics.entities.order_item import OrderItem
from core.modules.orders.generics.collections.order_item_collection import OrderItemCollection

def test_calculates_total_with_discount():
    # Arrange
    items = OrderItemCollection(
        OrderItem(product_id=1, quantity=2, price=10.00),  # 2 x $10 = $20
        OrderItem(product_id=2, quantity=1, price=15.00)   # 1 x $15 = $15
    )
    order = Order(customer_id=123, items=items, discount_coupon='SAVE10')  # 10% discount

    action = CalculateTotalPriceAction()

    # Act
    result = action.apply(order)

    # Assert
    assert result.total_price == 31.50  # (35 * 0.9) - 10% discount
```

**Testing UseCases**:
```python
# tests/unit/core/modules/orders/create_order/test_create_order_use_case.py
import pytest
from unittest.mock import Mock
from core.modules.orders.create_order.create_order_use_case import CreateOrderUseCase
from core.modules.orders.create_order.inputs.create_order_input import CreateOrderInput
from core.modules.orders.create_order.responses.create_order_success import CreateOrderSuccess
from core.modules.orders.create_order.responses.create_order_error import CreateOrderError
from core.modules.orders.create_order.exceptions.payment_failed_exception import PaymentFailedException
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.generics.entities.payment import Payment
from core.modules.orders.generics.collections.order_item_collection import OrderItemCollection

def test_creates_order_successfully():
    # Arrange
    mock_order_gateway = Mock()
    mock_payment_gateway = Mock()
    mock_logger = Mock()

    order = Order(customer_id=123, items=OrderItemCollection())
    order.set_total_price(100.00)

    mock_order_gateway.save.return_value = order
    mock_payment_gateway.process_payment.return_value = Payment(...)

    use_case = CreateOrderUseCase(mock_order_gateway, mock_payment_gateway, mock_logger)
    input_data = CreateOrderInput(order=order, customer_id=123, payment_method='credit_card')

    # Act
    response = use_case.execute(input_data)

    # Assert
    assert isinstance(response, CreateOrderSuccess)
    assert response.order.total_price == 100.00

def test_returns_error_when_payment_fails():
    # Arrange
    mock_order_gateway = Mock()
    mock_payment_gateway = Mock()
    mock_logger = Mock()

    mock_payment_gateway.process_payment.side_effect = PaymentFailedException(
        'Insufficient funds', 'TXN123'
    )

    use_case = CreateOrderUseCase(mock_order_gateway, mock_payment_gateway, mock_logger)
    input_data = CreateOrderInput(order=Order(...), customer_id=123, payment_method='credit_card')

    # Act
    response = use_case.execute(input_data)

    # Assert
    assert isinstance(response, CreateOrderError)
    assert isinstance(response.throwable, PaymentFailedException)
```

### Integration Tests (Infrastructure Layer)

Test Adapters with real infrastructure (test database, etc.).

**Testing Adapters**:
```python
# tests/integration/infrastructure/adapters/orders/test_order_adapter.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.adapters.orders.order_adapter import OrderAdapter
from infrastructure.models.order import Order as OrderModel
from core.modules.orders.generics.entities.order import Order
from core.modules.orders.generics.entities.order_item import OrderItem
from core.modules.orders.generics.collections.order_item_collection import OrderItemCollection

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()
    # Create tables
    Base.metadata.create_all(engine)
    yield session
    session.close()

def test_saves_order_to_database(db_session):
    # Arrange
    adapter = OrderAdapter(db_session)
    items = OrderItemCollection(
        OrderItem(product_id=1, quantity=2, price=10.00)
    )
    order = Order(customer_id=123, items=items)
    order.set_total_price(20.00)

    # Act
    saved_order = adapter.save(order)

    # Assert
    assert saved_order.id is not None
    assert db_session.query(OrderModel).filter(
        OrderModel.id == saved_order.id
    ).first() is not None

def test_finds_order_by_id(db_session):
    # Arrange
    order_model = OrderModel(
        id=1,
        customer_id=123,
        order_number='ORD-123',
        status='pending',
        total_price=20.00
    )
    db_session.add(order_model)
    db_session.commit()

    adapter = OrderAdapter(db_session)

    # Act
    order = adapter.find_by_id(1)

    # Assert
    assert order is not None
    assert order.customer_id == 123
```

### Feature Tests (End-to-End)

Test complete flows through HTTP endpoints.

```python
# tests/e2e/test_order_controller.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_creates_order_via_api():
    # Arrange
    payload = {
        'customer_id': 123,
        'items': [
            {'product_id': 1, 'quantity': 2, 'price': 10.00}
        ],
        'payment_method': 'credit_card'
    }

    # Act
    response = client.post('/api/orders', json=payload)

    # Assert
    assert response.status_code == 201
    assert response.json()['success'] is True
    assert 'order' in response.json()['data']
```

---

## Common Pitfalls

### ❌ Pitfall 1: Putting Business Logic in Controllers

**Bad**:
```python
@router.post('/orders')
def create_order(request: CreateOrderSchema):
    # ❌ Business logic in controller!
    if not request.items:
        raise HTTPException(status_code=400, detail='Items required')

    total = 0
    for item in request.items:
        total += item.price * item.quantity

    OrderModel.create(total=total)
```

**Good**:
```python
@router.post('/orders')
def create_order(request: CreateOrderSchema):
    use_case = CreateOrderUseCase(...)
    response = use_case.execute(CreateOrderInput(...))
    return CreateOrderResponseFactory.to_http(response)
```

---

### ❌ Pitfall 2: Exposing ORM Models to Core

**Bad**:
```python
# ❌ Gateway returns ORM model
from infrastructure.models.order import Order as OrderModel

class OrderGateway(Protocol):
    def find_by_id(self, id: int) -> OrderModel:  # ❌
        ...
```

**Good**:
```python
# ✅ Gateway returns domain Entity
from core.modules.orders.generics.entities.order import Order

class OrderGateway(Protocol):
    def find_by_id(self, id: int) -> Optional[Order]:  # ✅
        ...
```

---

### ❌ Pitfall 3: UseCase Doing Too Much

**Bad**:
```python
class CancelOrderUseCase:
    def execute(self, input_data: CancelOrderInput) -> CancelOrderResponse:
        # ❌ Too much logic in UseCase!
        order = OrderModel.query.get(input_data.id)
        if not order:
            raise NotFoundException()

        if order.status == 'shipped':
            raise CannotCancelException()

        order.status = 'cancelled'
        db.session.commit()
        # ...
```

**Good**:
```python
class CancelOrderUseCase:
    def execute(self, input_data: CancelOrderInput) -> CancelOrderResponse:
        # ✅ Delegate to Actions
        order = self.fetch_order_action.apply(input_data.order_id)
        self.validate_can_be_cancelled_action.apply(order)
        self.cancel_order_action.apply(order)
        return CancelOrderSuccess(order=order)
```

---

### ❌ Pitfall 4: Missing Dependency Inversion

**Bad**:
```python
# ❌ UseCase depends on concrete Adapter
from infrastructure.adapters.orders.order_adapter import OrderAdapter

class CreateOrderUseCase:
    def __init__(self, adapter: OrderAdapter):  # ❌ Concrete class
        self.adapter = adapter
```

**Good**:
```python
# ✅ UseCase depends on Gateway protocol
from core.modules.orders.create_order.gateways.order_gateway import OrderGateway

class CreateOrderUseCase:
    def __init__(self, gateway: OrderGateway):  # ✅ Protocol
        self.gateway = gateway
```

---

### ❌ Pitfall 5: Framework Dependencies in Core

**Bad**:
```python
# ❌ Using framework classes in Core
# core/modules/orders/create_order/actions/save_order_action.py

from sqlalchemy.orm import Session  # ❌

class SaveOrderAction:
    def apply(self, order: Order) -> Order:
        db.session.add(order)  # ❌
        db.session.commit()
```

**Good**:
```python
# ✅ Using Gateway protocol
# core/modules/orders/create_order/actions/save_order_action.py

from core.modules.orders.create_order.gateways.order_gateway import OrderGateway

class SaveOrderAction:
    def __init__(self, gateway: OrderGateway):  # ✅
        self.gateway = gateway

    def apply(self, order: Order) -> Order:
        return self.gateway.save(order)  # ✅
```

---

## Migration Checklist

When adopting this architecture in a new Python project:

### Core Layer Checklist

- [ ] Create `core/` directory
- [ ] Define module structure under `core/modules/`
- [ ] Create shared `dependencies/` protocols (LogInterface, etc.)
- [ ] Create base `Collection` class
- [ ] For each feature:
  - [ ] Create UseCase directory
  - [ ] Define Gateway protocols
  - [ ] Create Input DTO
  - [ ] Create Response DTOs (Success, Error)
  - [ ] Implement Actions
  - [ ] Implement UseCase
  - [ ] Create domain Entities (if needed)
  - [ ] Create Collections (if needed)
  - [ ] Create Exceptions (if needed)

### Infrastructure Layer Checklist

- [ ] Organize `infrastructure/` with adapters, presenters, factories
- [ ] For each feature:
  - [ ] Implement Adapters for Gateways
  - [ ] Create Presenters (Success, Error)
  - [ ] Create ResponseFactory
  - [ ] Create domain Factories (if needed)
  - [ ] Add Controller method
  - [ ] Add route
  - [ ] Add Pydantic schemas for validation (if needed)

### Testing Checklist

- [ ] Create unit tests for Actions (mock Gateways)
- [ ] Create unit tests for UseCases (mock Gateways)
- [ ] Create integration tests for Adapters (use test database)
- [ ] Create feature tests for HTTP endpoints

---

## Summary

This architecture provides:

1. **Clear Separation**: Business logic (Core) is completely isolated from infrastructure
2. **Testability**: UseCases and Actions can be tested without databases or HTTP
3. **Maintainability**: Each component has a single, well-defined responsibility
4. **Flexibility**: Easy to swap implementations (database, APIs, frameworks)
5. **Domain Focus**: Business concepts are modeled as first-class entities
6. **Type Safety**: Python's type hints provide excellent static type checking with mypy

By following these patterns and conventions, you can build scalable, maintainable Python applications that are easy to test and evolve over time.

---

## Additional Resources

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Python Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
- [Python Protocols (PEP 544)](https://www.python.org/dev/peps/pep-0544/)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-14
**Type**: Architecture Guide (Python)
**Framework Examples**: FastAPI, SQLAlchemy (adaptable to Django, Flask, etc.)
