# 🦎 Pangolin Platform - Complete Tech Stack Analysis

> **Data:** 2025-11-18
> **Scope:** Full system architecture + technology mapping
> **Objective:** Create comprehensive knowledge base for future development

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

### Core Components (5-Stack Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    Pangolin Ecosystem                      │
├─────────────────────────────────────────────────────────────┤
│ 1. PANGOLIN (Control Plane)                                │
│    - Web Dashboard (Next.js)                               │
│    - REST API (Express)                                     │
│    - WebSocket Server                                        │
│    - Authentication & AuthZ                                 │
│    - Database Layer (SQLite/PG)                             │
├─────────────────────────────────────────────────────────────┤
│ 2. TRAEFIK (Edge Router)                                   │
│    - Request Routing                                        │
│    - SSL Termination                                        │
│    - Middleware Chain                                       │
│    - Load Balancing                                         │
├─────────────────────────────────────────────────────────────┤
│ 3. BADGER (Auth Middleware)                                 │
│    - Request Interception                                   │
│    - Authentication Check                                    │
│    - Secure Redirects                                       │
│    - Plugin System                                          │
├─────────────────────────────────────────────────────────────┤
│ 4. GERBIL (WireGuard Manager)                              │
│    - WireGuard Interface Mgmt                               │
│    - Peer Management (HTTP API)                             │
│    - SNI Proxy for HTTPS Routing                             │
│    - UDP Tunnel Management                                  │
├─────────────────────────────────────────────────────────────┤
│ 5. NEWT (Tunnel Client)                                    │
│    - WireGuard Userspace Client                            │
│    - TCP/UDP Proxy                                          │
│    - Docker Socket Integration                             │
│    - Local Service Exposure                                │
└─────────────────────────────────────────────────────────────┘
```

### Traffic Flow Pattern

```
Internet User
    ↓ HTTPS (443)
┌─────────────┐
│  Traefik    │ ← SSL Termination + Routing
│  (Router)   │
└─────────────┘
    ↓ Auth Check
┌─────────────┐
│   Badger    │ ← Authentication Middleware
│  (Auth)     │
└─────────────┘
    ↓ HTTP/WS
┌─────────────┐
│  Pangolin    │ ← Management + Dashboard
│ (Control)   │
└─────────────┘
    ↓ WireGuard UDP (51820)
┌─────────────┐
│   Gerbil    │ ← WireGuard Manager
│  (Tunnel)   │
└─────────────┘
    ↓ Encrypted Tunnel
┌─────────────┐
│    Newt     │ ← Local Client
│ (Client)    │
└─────────────┘
    ↓ Local Service
┌─────────────┐
│ App Service │ ← Target Application
│ (Internal)  │
└─────────────┘
```

---

## 🛠️ TECHNOLOGY STACK DEEP DIVE

### 1. Backend Stack (API/WebSocket Server)

**Core Framework:**
- **Node.js v20.19.0** - LTS with latest security patches
- **TypeScript 5+** - Type safety + enhanced DX
- **Express 5.0.3** - REST API foundation
- **WebSocket (ws) 8.18.1** - Real-time communication

**Key Architectural Decisions:**

1. **Why Node.js v20.19.0?**
   - **Performance:** V20 introduces optimized async/await
   - **Security:** Latest LTS patches
   - **Compatibility:** Broad NPM ecosystem
   - **Memory:** Better V8 engine optimization

2. **TypeScript Benefits:**
   ```typescript
   // Interface-driven development
   interface PangolinConfig {
     gerbil: GerbilConfig;
     traefik: TraefikConfig;
     database: DatabaseConfig;
     auth: AuthConfig;
   }

   // Type-safe API routes
   app.post('/api/v1/targets', async (req: Request<{}, {}, TargetRequest>) => {
     // Compile-time validation
   });
   ```

3. **Express 5.0.3 Patterns:**
   ```javascript
   // Async route handlers (native in 5.x)
   app.get('/api/v1/status', async (req, res) => {
     const status = await pangolinService.getStatus();
     res.json(status);
   });

   // Middleware chain
   app.use('/api/v1', authMiddleware, rateLimitMiddleware, loggingMiddleware);
   ```

### 2. Frontend Stack (Dashboard)

**Framework Choice: Next.js (React Framework)**

**Why Next.js over vanilla React?**
- **SSR/SSG:** Better performance for dashboard
- **API Routes:** Unified codebase
- **TypeScript Support:** Native integration
- **Code Splitting:** Automatic optimization
- **Image Optimization:** Built-in

**Key Patterns:**
```typescript
// pages/api/targets.ts - API Routes
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const targets = await getTargets();
    res.status(200).json(targets);
  }
}

// components/TargetCard.tsx - Typed Components
interface TargetCardProps {
  target: Target;
  onEdit: (target: Target) => void;
  onDelete: (id: string) => void;
}

export const TargetCard: React.FC<TargetCardProps> = ({ target, onEdit, onDelete }) => {
  // Type-safe props + auto-completion
};
```

### 3. Database Layer

**SQLite (Default) + PostgreSQL (Production)**

**Architecture Decision Analysis:**

**SQLite Advantages:**
- ✅ **Zero-config:** No setup required
- ✅ **Portable:** Single file database
- ✅ **Fast:** In-process queries
- ✅ **ACID compliant:** Transaction safety
- ✅ **Low resource:** Perfect for edge deployments

**PostgreSQL Advantages (Production):**
- ✅ **Concurrent:** Multiple connections
- ✅ **Scalable:** Handle large datasets
- ✅ **Advanced:** JSON support, indexing strategies
- ✅ **HA:** Replication, backup strategies
- ✅ **Monitoring:** Rich tooling ecosystem

**Drizzle ORM Analysis:**
```typescript
// Schema definition with TypeScript
export const targets = pgTable('targets', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  domain: text('domain').notNull(),
  target: text('target').notNull(),
  active: boolean('active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

// Type-safe queries
const allTargets = await db.select().from(targets);
const activeTargets = await db.select().from(targets).where(eq(targets.active, true));
```

**Migration Strategy:**
```sql
-- PostgreSQL to SQLite migration pattern
CREATE TABLE targets (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  domain VARCHAR(255) NOT NULL,
  target TEXT NOT NULL,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_targets_active ON targets(active);
CREATE INDEX idx_targets_domain ON targets(domain);
```

### 4. Reverse Proxy & Networking

**Traefik v3.3-v3.5 Integration**

**Why Traefik over Nginx?**
- ✅ **Service Discovery:** Auto-detect containers
- ✅ **Let's Encrypt:** Automatic SSL certificates
- ✅ **Middleware:** Rich plugin ecosystem
- ✅ **Configuration:** Dynamic config updates
- ✅ **Monitoring:** Built-in metrics dashboard

**Key Configuration Patterns:**
```yaml
# traefik_config.yml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: "websecure"
          scheme: "https"
  websecure:
    address: ":443"

providers:
  docker: {}
  file:
    directory: /etc/traefik/dynamic

experimental:
  plugins:
    badger:
      moduleName: "github.com/fosrl/badger"
      version: "v1.2.0"  # Critical: Don't use "latest"
```

**WireGuard Architecture:**
```bash
# WireGuard Configuration Pattern
[Interface]
PrivateKey = <private-key>
Address = 10.0.0.2/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = <server-public-key>
Endpoint = pangolin.example.com:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

**Gerbil WireGuard Manager:**
- **Interface Management:** Dynamic wg interface creation
- **Peer Management:** HTTP API for peer operations
- **SNI Proxy:** HTTPS routing based on hostname
- **Port Management:** 51820 UDP + 21820 UDP (clients)

### 5. Security Architecture

**Multi-Layer Security Model:**

```
┌─────────────────────────────────────────────┐
│              Security Layers               │
├─────────────────────────────────────────────┤
│ 1. Network Security                        │
│    - WireGuard Encryption                   │
│    - Firewall Rules                         │
│    - Port Management                        │
├─────────────────────────────────────────────┤
│ 2. Transport Security                      │
│    - HTTPS/TLS 1.3                          │
│    - Let's Encrypt Certificates              │
│    - HSTS Headers                           │
├─────────────────────────────────────────────┤
│ 3. Application Security                    │
│    - JWT Authentication                    │
│    - Session Management                    │
│    - CSRF Protection                        │
├─────────────────────────────────────────────┤
│ 4. Data Security                           │
│    - Encrypted Database                    │
│    - Environment Variables                 │
│    - Secrets Management                    │
└─────────────────────────────────────────────┘
```

**Authentication Flow:**
```typescript
// JWT-based authentication
interface AuthToken {
  userId: string;
  email: string;
  role: 'admin' | 'user';
  permissions: string[];
  iat: number;
  exp: number;
}

// Middleware pattern
const authenticateToken = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.split(' ')[1];

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET) as AuthToken;
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};
```

---

## 🐳 CONTAINER & DEPLOYMENT PATTERNS

### Docker Compose Architecture

**Service Dependencies:**
```yaml
services:
  pangolin:
    image: fosrl/pangolin:latest
    depends_on:
      - postgres  # Wait for database
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/api/v1/"]
      interval: 3s
      timeout: 3s
      retries: 15

  gerbil:
    depends_on:
      pangolin:
        condition: service_healthy  # Wait for Pangolin API
    cap_add:
      - NET_ADMIN  # Required for WireGuard
      - SYS_MODULE

  traefik:
    network_mode: service:gerbil  # Share network namespace
    depends_on:
      pangolin:
        condition: service_healthy
```

**Production Optimizations:**
```yaml
# Resource limits
services:
  pangolin:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

    environment:
      - NODE_ENV=production
      - LOG_LEVEL=info

    restart: unless-stopped
```

### Deployment Patterns

**Single-Node Deployment:**
- **Development:** Docker Compose locally
- **Production:** Docker Compose on VPS
- **Edge:** Raspberry Pi with ARM images

**Multi-Node Considerations:**
- **Database:** External PostgreSQL cluster
- **Load Balancing:** Multiple Traefik instances
- **High Availability:** Active-passive Pangolin setup

---

## 🔍 PATTERNS & BEST PRACTICES IDENTIFIED

### 1. Error Handling Patterns

**Graceful Degradation:**
```typescript
// Service health check pattern
class PangolinService {
  async healthCheck(): Promise<HealthStatus> {
    try {
      await this.checkDatabase();
      await this.checkGerbilConnection();
      await this.checkWireGuardInterfaces();

      return { status: 'healthy', services: 'operational' };
    } catch (error) {
      logger.error('Health check failed:', error);
      return {
        status: 'degraded',
        services: this.identifyFailedServices(error)
      };
    }
  }
}
```

**Circuit Breaker Pattern:**
```typescript
class WireGuardService {
  private circuitBreaker = new CircuitBreaker({
    threshold: 5,
    timeout: 60000,
    resetTimeout: 30000
  });

  async createPeer(config: PeerConfig): Promise<Peer> {
    return this.circuitBreaker.execute(async () => {
      return await this.gerbilClient.createPeer(config);
    });
  }
}
```

### 2. Performance Patterns

**Connection Pooling:**
```typescript
// PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Efficient query batching
const batchCreateTargets = async (targets: Target[]): Promise<void[]> => {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    for (const target of targets) {
      await client.query(
        'INSERT INTO targets (name, domain, target) VALUES ($1, $2, $3)',
        [target.name, target.domain, target.target]
      );
    }

    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
};
```

### 3. Security Patterns

**Defense in Depth:**
```typescript
// Rate limiting per user
const rateLimit = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP',
  standardHeaders: true,
  legacyHeaders: false,
});

// Input validation
const validateTargetInput = (req: Request, res: Response, next: NextFunction) => {
  const schema = Joi.object({
    name: Joi.string().min(1).max(255).required(),
    domain: Joi.string().domain().required(),
    target: Joi.string().uri().required(),
  });

  const { error } = schema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: error.details[0].message });
  }

  next();
};
```

---

## 🚀 SCALABILITY & PERFORMANCE CONSIDERATIONS

### Bottleneck Analysis

**Identified Bottlenecks:**
1. **WireGuard Throughput:** Single UDP port limitation
2. **Database Queries:** N+1 queries in dashboard
3. **WebSocket Connections:** Memory usage per connection
4. **File System:** SQLite lock contention

**Scaling Strategies:**

1. **Horizontal Scaling (Multiple Nodes):**
   ```yaml
   # Load balancer configuration
   services:
     traefik-1:
       image: traefik:v3.5
       command: --api.insecure=true --providers.docker

     traefik-2:
       image: traefik:v3.5
       command: --api.insecure=true --providers.docker

   # External load balancer distributes traffic
   ```

2. **Database Scaling:**
   ```sql
   -- Read replicas for dashboard queries
   CREATE USER pangolin_readonly WITH PASSWORD 'readonly_password';
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO pangolin_readonly;

   -- Connection pooling with PgBouncer
   ```

3. **Caching Strategy:**
   ```typescript
   // Redis caching for frequently accessed data
   const cacheTargets = async () => {
     const cached = await redis.get('targets:all');
     if (cached) return JSON.parse(cached);

     const targets = await db.select().from(targets);
     await redis.setex('targets:all', 300, JSON.stringify(targets));
     return targets;
   };
   ```

### Performance Metrics to Monitor

**Key Metrics:**
- **WireGuard throughput:** MB/s per tunnel
- **API response time:** P95 latency
- **Database query time:** Slow query detection
- **WebSocket connections:** Concurrent connections
- **Memory usage:** Per container and total
- **CPU utilization:** Per service breakdown

---

## 🔮 FUTURE ROADMAP & ARCHITECTURAL DECISIONS

### Identified Evolution Paths

1. **Microservices Migration:**
   - Extract authentication service
   - Separate configuration management
   - Independent scaling per service

2. **Advanced Security:**
   - Zero-trust networking
   - Mutual TLS between services
   - Hardware security modules (HSM)

3. **Multi-Cloud Support:**
   - AWS/GCP/Azure integration
   - Kubernetes deployment
   - Service mesh (Istio/Linkerd)

### Technical Debt Analysis

**Current Limitations:**
- **SQLite:** Not suitable for high-concurrency
- **Single-node:** No built-in HA
- **Manual SSL:** Limited certificate management
- **Configuration:** File-based, not dynamic

**Recommended Improvements:**
```typescript
// Configuration service pattern
interface ConfigurationService {
  get(key: string): Promise<ConfigValue>;
  set(key: string, value: ConfigValue): Promise<void>;
  watch(key: string, callback: (value: ConfigValue) => void): void;
}

// Event-driven architecture
class EventBus {
  emit(event: string, data: any): void;
  on(event: string, handler: (data: any) => void): void;
  off(event: string, handler: (data: any) => void): void;
}
```

---

## 💡 STRATEGIC INSIGHTS FOR FUTURE DEVELOPMENT

### 1. Technology Selection Rationale

**Node.js vs Go/Rust for Backend:**
- **Chosen:** Node.js for ecosystem + TypeScript
- **Alternative:** Go for performance (WireGuard tools)
- **Decision:** Developer experience outweighs raw performance

**SQLite vs PostgreSQL:**
- **Chosen:** SQLite for simplicity + PostgreSQL for production
- **Pattern:** Start simple, scale when needed

**Next.js vs React SPA:**
- **Chosen:** Next.js for SSR + API routes
- **Benefit:** Unified codebase + better SEO/performance

### 2. Architecture Patterns

**Microkernel Pattern:**
- Core: Minimal routing + authentication
- Extensions: Protocol-specific handlers
- Benefit: Extensible without core changes

**Event-Driven Communication:**
- Components communicate via events
- Loose coupling between services
- Easy to add new components

### 3. Deployment Strategy

**Blue-Green Deployment:**
- Zero downtime updates
- Instant rollback capability
- Production safety

**Configuration Management:**
- External config service
- Environment-specific overrides
- Runtime config updates

---

## 📚 KNOWLEDGE GAPS & RESEARCH AREAS

### Areas for Further Investigation

1. **WireGuard Deep Dive:**
   - Protocol internals
   - Performance optimization
   - Custom extensions

2. **Advanced Networking:**
   - UDP optimization techniques
   - SNI proxy patterns
   - Load balancing strategies

3. **Security Hardening:**
   - Post-quantum cryptography
   - Zero-trust implementation
   - Compliance frameworks (SOC2, ISO27001)

4. **Performance Engineering:**
   - Profiling Node.js applications
   - Memory leak detection
   - CPU optimization patterns

### Recommended Learning Resources

**Technical Deep Dives:**
- WireGuard whitepaper
- Node.js performance patterns
- PostgreSQL optimization
- Container orchestration patterns

**Architecture Resources:**
- Microservices patterns
- Event-driven architecture
- System design principles
- Distributed systems fundamentals

---

**Last Updated:** 2025-11-18
**Next Review:** Architecture review in 6 months
**Maintainer:** Claude AI + Development Team
**Knowledge Base:** Indexed in RAG system for intelligent retrieval