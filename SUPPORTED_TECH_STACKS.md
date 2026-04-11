# Supported Technology Stacks

This document outlines all the technology stacks supported by the Code Intelligence System for indexing and analysis.

## 🎯 Overview

The system now supports **6 major technology layers** with comprehensive parsing capabilities:

1. **Angular (Frontend Web)** - Full Angular 18+ ecosystem
2. **React (Frontend Web)** - React with TypeScript
3. **Flutter (Mobile)** - Dart/Flutter applications
4. **NestJS (Backend)** - Enhanced Node.js/NestJS 8+ with full ecosystem
5. **Terraform (Infrastructure)** - Infrastructure as Code
6. **ArgoCD/Kubernetes (Deployment)** - Container orchestration

---

## 🅰️ Angular Support (Frontend Web)

### Core Framework
- **Angular 18.1.0**
- **TypeScript 5.4.5**
- **Node.js >=18.19.1**

### UI & Styling Components Detected
- Angular Material 16.2.14 (mat-button, mat-card, mat-form-field, mat-table, etc.)
- Angular CDK 16.2.14
- Angular Flex Layout 15.0.0-beta.42
- ngx-color-picker 17.0.0
- ngx-daterangepicker-material 6.0.4
- ngx-quill 26.0.5 (Rich text editor)
- Quill 2.0.2

### State Management (NgRx)
- Store 18.0.1
- Effects 18.0.1
- Entity 18.0.1
- Router Store 18.0.1
- Store Devtools 18.0.1
- Actions, Reducers, Selectors, Features

### Data & APIs
- Apollo Client 3.10.8 (GraphQL)
- apollo-angular 7.0.2
- GraphQL 16.9.0 (queries, mutations, subscriptions)
- Socket.io Client 4.7.5
- ngx-socket-io 4.7.0
- HTTP Client interceptors

### Third-Party Integrations
- Google Maps (@angular/google-maps 18.1.0)
- Stripe (@stripe/stripe-js 4.1.0, ngx-stripe 18.1.0)
- Twilio Voice SDK 2.11.2
- Plaid (ngx-plaid-link 14.0.0)
- Highcharts 11.2.0
- Hotjar 1.0.9

### Component Types Parsed
- **Components** (@Component) - with inputs, outputs, lifecycle hooks
- **Services** (@Injectable) - with HTTP, GraphQL, WebSocket usage
- **Modules** (@NgModule) - declarations, imports, providers, exports
- **Directives** (@Directive)
- **Pipes** (@Pipe)
- **Guards** (CanActivate, CanDeactivate, etc.)
- **Resolvers** (Resolve<T>)
- **Interceptors** (HttpInterceptor)
- **NgRx** - Actions, Reducers, Selectors, Effects, Features

### Angular Elements Detected
- Lifecycle hooks (ngOnInit, ngOnDestroy, etc.)
- @Input() and @Output() properties
- Constructor dependency injection
- Template URLs and style URLs
- Selectors
- Material component usage
- RxJS patterns
- Lazy loading indicators

---

## ⚛️ React Support (Frontend Web)

### Core
- React 18+ with TypeScript
- JSX/TSX components
- Functional components and hooks

### Component Types
- **Pages** - Route-level components
- **Components** - Reusable UI components
- **Hooks** - Custom hooks (use*)
- **Services** - API clients (axios, fetch)

### Detected Patterns
- React hooks (useState, useEffect, useContext, etc.)
- API calls (axios, fetch)
- State management
- Props interfaces
- Navigation (react-router)

---

## 📱 Flutter Support (Mobile)

### Core
- Dart language
- Flutter framework
- Widget-based architecture

### Component Types
- **Screens** - Full page widgets
- **Widgets** - Reusable components
- **Services** - API clients, business logic

---

## ⚙️ NestJS Support (Backend) - ENHANCED

### Core Framework
- **NestJS 8.4.7+** (now using Enhanced Parser)
- **TypeScript 4.9.5**
- **Node.js >=16**
- **Express.js 4.17.1**

### Architecture Components Parsed

#### Controllers
- @Controller decorators with base routes
- HTTP methods: @Get, @Post, @Put, @Delete, @Patch, @All, @Head, @Options
- Route parameters and query handling
- Swagger/OpenAPI decorators
- Authentication guards (@UseGuards)
- Throttling (@SkipThrottle, @Throttle)
- Request/Response DTOs

#### Services
- @Injectable services
- Constructor dependency injection
- Method extraction with async/Promise patterns
- Repository patterns

#### Data Layer
- **TypeORM Entities** - @Entity, @Column, relations
- **MongoDB/Mongoose** - @Schema, @Prop definitions
- **Repositories** - Custom repository classes
- **DTOs** - class-validator decorators (@IsString, @IsEmail, etc.)

#### GraphQL
- **Resolvers** - @Resolver, @Query, @Mutation, @Subscription
- **Field Resolvers** - @ResolveField
- Schema-first and code-first approaches

#### WebSocket/Socket.io
- **Gateways** - @WebSocketGateway
- **Message Handlers** - @SubscribeMessage
- **Server instances** - @WebSocketServer
- Redis adapter support

#### Job Queues (Bull)
- **Processors** - @Processor with queue names
- **Process handlers** - @Process decorators
- Job patterns and queue configuration

#### Authentication & Security
- **Guards** - CanActivate, CanActivateChild with JWT/Roles strategies
- **Passport** strategies
- JWT handling
- Role-based access control
- 2FA (otplib)

#### Microservices
- **NATS** message broker integration
- **@nestjs/microservices** patterns
- Event-driven architecture

#### Middleware & Interceptors
- **Middleware** - NestMiddleware implementations
- **Interceptors** - Logging, Transform, Cache, Error, Timeout
- Request/Response transformation

#### Scheduled Tasks
- **Cron jobs** - @Cron decorator
- **Intervals** - @Interval
- **Timeouts** - @Timeout
- @nestjs/schedule integration

#### Event System
- **EventEmitter** - @OnEvent listeners
- Custom event patterns

#### Modules
- @Module organization
- Controllers, Providers, Imports, Exports
- Feature modules
- Global modules

### Third-Party Integrations Detected

#### Payments
- Stripe 8.135.0
- Plaid 10.8.0
- Dwolla 3.4.0

#### Communication
- Twilio 3.50.0 (SMS, Voice)
- Slack Web API 6.7.0
- Mailchimp 1.0.47
- Urban Airship 0.1.0 (push notifications)

#### Maps & Geospatial
- Mapbox/Polyline 1.2.1
- @turf/turf 7.0.0
- node-geocoder 3.29.0
- geo-tz 6.0.0 (timezone)

#### Storage & File Processing
- AWS S3 (aws-sdk)
- XLSX 0.18.5 (Excel)
- ExcelJS 4.4.0
- PDF-Lib 1.17.1
- Jimp 0.16.2 (image processing)
- adm-zip 0.5.6
- SSH2 0.8.9 (SFTP)
- WebDAV 4.11.2
- FTP (basic-ftp 4.6.6)

#### External APIs
- GitHub (Octokit 3.5.1)
- EDI processing (ipworksedi)
- MS Teams webhooks 2.0.2

#### Caching & Message Brokers
- Redis 3.1.2 / ioredis
- Bull 3.29.2 (job queues)
- NATS 2.7.1

#### Database
- MongoDB / Mongoose 5.13.14
- mongoose-sequence 5.2.2
- TypeORM support

#### Validation & Transformation
- class-validator 0.14.0
- class-transformer 0.4.0
- Joi 17.6.0

#### Utilities
- RxJS 7.5.5
- Lodash 4.17.20
- Moment 2.24.0 / moment-timezone 0.5.27
- Axios 0.27.2
- Handlebars 4.7.6
- UUID 7.0.3
- QRCode 1.5.3
- Chance 1.1.4

#### Monitoring & Logging
- Datadog APM (dd-trace 2.22.3)
- Morgan 1.10.0 / morgan-body 2.6.8
- Loggly 1.1.1

---

## 🏗️ Terraform Support (Infrastructure)

### Core
- HCL (HashiCorp Configuration Language)
- Terraform 1.0+

### Resources Detected
- AWS resources (EC2, S3, RDS, Lambda, etc.)
- Azure resources
- Google Cloud resources
- Variables and outputs
- Modules
- Data sources
- Locals
- Secrets and sensitive data detection

---

## ☸️ ArgoCD/Kubernetes Support (Deployment)

### Core
- Kubernetes YAML manifests
- ArgoCD Application definitions

### Resources Detected
- **Deployments** - Container specs, replicas, images
- **Services** - ClusterIP, NodePort, LoadBalancer
- **ConfigMaps** - Configuration data
- **Secrets** - Sensitive data (base64 detection)
- **Ingress** - Routing rules
- **PersistentVolumes** - Storage
- **ServiceAccounts** - RBAC
- **Namespaces** - Resource organization
- Environment variables
- Volume mounts
- Health checks (liveness/readiness probes)

---

## 🔗 Cross-Layer Relationships

The system automatically detects and maps relationships between layers:

### Frontend → Backend
- **API Calls**: HTTP endpoints from Angular/React to NestJS controllers
- **GraphQL**: Apollo Client queries → NestJS resolvers
- **WebSocket**: Socket.io client → NestJS gateways
- **DTO Usage**: Frontend models matching backend DTOs

### Backend → Data
- **Service → Repository**: Method calls to data layer
- **Controller → Service**: Dependency injection chains
- **Schema/Entity links**: MongoDB schemas, TypeORM entities

### Backend → Infrastructure
- **Environment variables**: Usage in configs
- **Secret references**: Database passwords, API keys
- **Queue connections**: Bull → Redis
- **Microservice connections**: NATS, Socket.io Redis

### Frontend → Frontend
- **Navigation**: Route definitions, router links
- **State sharing**: NgRx store, React Context
- **Component composition**: Parent-child relationships
- **Service sharing**: Shared Angular services

---

## 📊 Indexing Output

For each technology, the system extracts:

### Common Fields (All Components)
- `id`: Unique identifier
- `name`: Component name
- `type`: Component type (component, service, controller, etc.)
- `layer`: Technology layer (frontend-web, frontend-mobile, backend, data, infrastructure)
- `file_path`: Source file location
- `line_start`: Line number in file
- `description`: Documentation comments

### Type-Specific Fields

**Angular Components**
- selector, template_url, style_urls
- inputs, outputs
- lifecycle_hooks
- material_components used
- ngrx (store, actions, selectors)
- graphql operations
- socket.io usage
- third-party integrations

**NestJS Controllers**
- base_route, routes[]
- swagger decorators
- auth_guards
- throttling config

**NestJS Services**
- methods[]
- mongo_usage (models, operations)
- redis_usage
- bull_usage (queues)
- http_usage (axios/HttpService)
- integrations (Stripe, Twilio, etc.)
- scheduled_jobs

**GraphQL Resolvers**
- queries[], mutations[], subscriptions[]
- field_resolvers[]
- resolver_type

**MongoDB Schemas**
- fields[] (name, type)
- schema_options

**Bull Processors**
- queue_name
- processes[]

**Socket Gateways**
- namespace
- message_handlers[]
- has_server flag

---

## 🚀 Usage Examples

### Index an Angular + NestJS Project
```bash
python -m code_intelligence index --repo ./my-angular-nestjs-app
```

### Query for GraphQL Resolvers
```bash
python -m code_intelligence query "Find all GraphQL mutations for payments"
```

### Search for NgRx Store Usage
```bash
python -m code_intelligence query "Components using user authentication state"
```

### Find WebSocket Gateways
```bash
python -m code_intelligence query "Socket.io gateways for real-time notifications"
```

---

## 📈 Supported Tech Stack Summary

| Category | Technologies | Version Range |
|----------|--------------|---------------|
| **Frontend Web** | Angular, React | Angular 18+, React 18+ |
| **Mobile** | Flutter | Flutter 3.x |
| **Backend** | NestJS, Express | NestJS 8.x |
| **Language** | TypeScript, Dart | TS 4.9+, Dart 3.x |
| **State Management** | NgRx, Redux | NgRx 18.x |
| **APIs** | GraphQL, REST | Apollo, Swagger |
| **Real-time** | Socket.io, WebSocket | Socket.io 4.x |
| **Database** | MongoDB, PostgreSQL, MySQL | Mongoose 5.x, TypeORM |
| **Caching** | Redis | Redis 3.x |
| **Queues** | Bull | Bull 3.x |
| **Message Broker** | NATS | NATS 2.x |
| **Authentication** | Passport, JWT, bcrypt | Passport 0.6 |
| **Payments** | Stripe, Plaid, Dwolla | Stripe 8.x, Plaid 10.x |
| **Communication** | Twilio, Slack, Mailchimp | Twilio 3.x |
| **Maps** | Google Maps, Mapbox | Google Maps 18.x |
| **Charts** | Highcharts | Highcharts 11.x |
| **File Processing** | ExcelJS, PDF-Lib, XLSX | ExcelJS 4.x |
| **Infrastructure** | Terraform, Kubernetes | Terraform 1.x |
| **CI/CD** | ArgoCD | ArgoCD 2.x |

---

## 🔧 Extending Support

To add support for additional technologies:

1. Create a new parser in `parsers/<technology>/`
2. Implement the parser class following existing patterns
3. Add detection logic to `unified_indexer.py`
4. Register in `parsers/__init__.py`
5. Update this documentation

---

## ✨ Recent Enhancements

### New in This Version
- ✅ **Angular 18.1.0** full ecosystem support
- ✅ **Enhanced NestJS Parser** with MongoDB, GraphQL, Socket.io, Bull, NATS
- ✅ **NgRx State Management** parsing (Store, Effects, Selectors, Actions)
- ✅ **Apollo GraphQL** client and server support
- ✅ **Third-party integrations** detection (Stripe, Twilio, Plaid, etc.)
- ✅ **Comprehensive component types** (Guards, Interceptors, Pipes, Directives)
- ✅ **Infrastructure awareness** (Redis, Bull queues, microservices)

---

For detailed usage instructions, see [USAGE_GUIDE.md](./USAGE_GUIDE.md)
For quick start, see [QUICK_START.md](./QUICK_START.md)
