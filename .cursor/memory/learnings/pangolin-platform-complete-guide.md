# 🦎 Pangolin Platform - Guia Completo de Conhecimento

> **LEIA ESTE ARQUIVO PARA SE TORNAR ESPECIALISTA EM PANGOLIN**
> **Data de Criação:** 2025-11-18
> **Status:** Documentação Completa e Atualizada
> **Versão Documentada:** Pangolin 1.12.2 | Gerbil 1.2.2 | Traefik v3.6.1

---

## 📋 ÍNDICE

1. [O Que é Pangolin](#o-que-é-pangolin)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Stack Tecnológica](#stack-tecnológica)
4. [Componentes Principais](#componentes-principais)
5. [API e Endpoints](#api-e-endpoints)
6. [Autenticação e Segurança](#autenticação-e-segurança)
7. [Servidor GCP](#servidor-gcp)
8. [Funcionalidades Avançadas](#funcionalidades-avançadas)
9. [Comandos Úteis](#comandos-úteis)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 O QUE É PANGOLIN

### Definição

**Pangolin** é um **Tunneled Reverse Proxy Management Server** open-source com:
- Gerenciamento de identidade e acesso (IAM)
- Dashboard UI web intuitivo
- Tunelamento seguro via WireGuard
- Controle de acesso baseado em contexto e identidade
- Alternativa self-hosted ao Cloudflare Tunnel e Tailscale

### Propósito

Conectar redes isoladas através de túneis criptografados, permitindo acesso fácil a serviços remotos **SEM**:
- Abrir portas no firewall
- Configurar VPN tradicional
- Expor serviços publicamente
- Depender de serviços cloud proprietários

### Casos de Uso

1. **Acesso Remoto Seguro**: Acessar serviços internos de qualquer lugar
2. **Load Balancing**: Distribuir tráfego entre múltiplos backends
3. **Proxy HTTP/HTTPS**: Roteamento inteligente de aplicações web
4. **Proxy TCP/UDP**: Suporte a qualquer protocolo (SSH, RDP, Databases, etc)
5. **Shareable Links**: Links temporários ou permanentes para compartilhar recursos
6. **Geo-blocking**: Bloqueio de acesso por região geográfica
7. **SSO/OIDC**: Integração com provedores de identidade corporativos

---

## 🏗️ ARQUITETURA DO SISTEMA

### Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│              Internet (Clientes)                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ WireGuard VPN (51820/UDP)
                 │ HTTP/HTTPS (80/443)
                 │
┌────────────────▼────────────────────────────────────────┐
│              VM GCP (34.9.79.106)                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │       Docker Network (172.18.0.0/16)             │   │
│  │                                                    │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────┐ │   │
│  │  │  Traefik    │  │   Gerbil     │  │Pangolin │ │   │
│  │  │  v3.6.1     │→│   v1.2.2     │→│ v1.12.2 │ │   │
│  │  │             │  │              │  │         │ │   │
│  │  │ Proxy       │  │ WireGuard    │  │Dashboard│ │   │
│  │  │ Load Bal.   │  │ Management   │  │+ API    │ │   │
│  │  └─────────────┘  └──────────────┘  └─────────┘ │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Fluxo de Tráfego

**Cliente → Serviço Interno**
```
1. Cliente (Newt/Browser)
   ↓
2. WireGuard Tunnel (criptografado)
   ↓
3. Traefik (proxy reverso, SSL termination)
   ↓
4. Gerbil (gerenciamento WireGuard, routing)
   ↓
5. Pangolin (autenticação, autorização, logging)
   ↓
6. Serviço de Destino (app interno)
```

**Configuração e Controle**
```
Gerbil ←→ Pangolin API
  │          │
  │          ├─ GET /api/v1/gerbil/get-config
  │          └─ POST /api/v1/gerbil/receive-bandwidth
  │
  └─ WebSocket Connection (real-time peer management)
```

---

## 💻 STACK TECNOLÓGICA

### Backend

| Componente | Versão | Função |
|-----------|--------|---------|
| **Node.js** | 20.19.2 | Runtime JavaScript |
| **Express.js** | 4.21.2 | Framework web backend |
| **TypeScript** | 5.x | Linguagem tipada |
| **SQLite** | via better-sqlite3 11.7.0 | Banco de dados |
| **PostgreSQL** | Suporte opcional | Banco produção (alternativa) |
| **Drizzle ORM** | 0.38.3 | ORM moderno |
| **WebSocket** | ws 8.18.2 | Comunicação real-time |
| **Winston** | 3.17.0 | Logging com rotação diária |

### Frontend

| Componente | Versão | Função |
|-----------|--------|---------|
| **Next.js** | 15.3.3 | Framework React SSR |
| **React** | 19.1.0 | UI library |
| **Radix UI** | Latest | Componentes acessíveis |
| **Tailwind CSS** | 4.1.4 | Styling utility-first |
| **Lucide React** | 0.511.0 | Ícones modernos |
| **React Email** | Latest | Templates de email |

### Segurança

| Componente | Versão | Função |
|-----------|--------|---------|
| **Arctic** | 3.7.0 | OAuth/OIDC authentication |
| **Oslo** | 1.2.1 | Security utilities |
| **JWT** | jsonwebtoken 9.0.2 | Token authentication |
| **Argon2** | @node-rs/argon2 | Password hashing |
| **Helmet** | 8.1.0 | Security headers |
| **CORS** | Configurado | Cross-origin control |
| **Rate Limiting** | express-rate-limit | DoS protection |

### DevOps

| Componente | Versão | Função |
|-----------|--------|---------|
| **Docker** | 29.0.1 | Containerização |
| **containerd** | 2.1.5 | Container runtime |
| **Traefik** | v3.6.1 | Proxy reverso |
| **WireGuard** | Latest | VPN tunnel |
| **Let's Encrypt** | Via Traefik | Certificados SSL |

---

## 🧩 COMPONENTES PRINCIPAIS

### 1. Pangolin Server (fosrl/pangolin:1.12.2)

**Container Docker Principal**

**Responsabilidades:**
- ✅ Gerenciamento de identidades (users, roles, organizations)
- ✅ Dashboard Web (Next.js UI)
- ✅ API REST completa
- ✅ WebSocket server para clientes
- ✅ Registro e rastreamento de peers
- ✅ Banco de dados (SQLite ou PostgreSQL)
- ✅ Audit logging
- ✅ Health checks
- ✅ Blueprints (templates de infraestrutura)

**Configuração:**
```yaml
Container: pangolin
Image: fosrl/pangolin:1.12.2
IP: 172.18.0.3
Porta interna: 3001
Volume: /home/admin/config:/app/config
Health check: curl -f http://localhost:3001/api/v1/health
Restart: unless-stopped
Command: npm run start:sqlite
```

**Processos:**
- PID 1: node dist/server.mjs
- Threads: Node.js single-thread + worker threads
- CPU: ~0.4%
- RAM: ~237 MB (5.9%)

**Arquivos Importantes:**
```
/app/
├── dist/
│   ├── server.mjs         # Servidor compilado
│   └── migrations.mjs     # Database migrations
├── config/ (volume montado)
│   ├── config.yml         # Configuração principal
│   ├── db/sqlite.db       # Banco SQLite
│   ├── key                # Chave autenticação
│   ├── logs/              # Winston logs (rotação diária)
│   └── letsencrypt/       # Certificados SSL
```

**Novos Recursos (v1.12.2):**
- Blueprints: Templates declarativos de configuração
- Geo-blocking: Bloqueio por região geográfica
- Advanced Health Checks: Monitoramento de targets
- Audit Logging: Rastreabilidade completa de ações
- Telemetry: Coleta de métricas (opt-in)

---

### 2. Gerbil (fosrl/gerbil:1.2.2)

**Cliente de Túnel WireGuard**

**Responsabilidades:**
- ✅ Gerenciar interfaces WireGuard
- ✅ Adicionar/remover peers dinamicamente
- ✅ Reportar métricas de bandwidth (a cada 10s)
- ✅ Buscar configuração remota do Pangolin
- ✅ Proxy de tráfego entre túneis e serviços
- ✅ Hole punching para conexões P2P

**Configuração:**
```yaml
Container: gerbil
Image: fosrl/gerbil:1.2.2
IP: 172.18.0.2
Portas expostas: 80, 443, 3389, 51820/UDP
Reachable at: http://gerbil:3003
```

**Comando de Inicialização:**
```bash
gerbil \
  --reachableAt=http://gerbil:3003 \
  --generateAndSaveKeyTo=/var/config/key \
  --remoteConfig=http://pangolin:3001/api/v1/gerbil/get-config \
  --reportBandwidthTo=http://pangolin:3001/api/v1/gerbil/receive-bandwidth
```

**API HTTP:**
- GET /config - Configuração atual
- POST /peers - Adicionar peer
- DELETE /peers/:id - Remover peer
- PUT /peers/:id - Atualizar peer
- GET /peers - Listar todos peers

**Métricas Reportadas:**
```json
{
  "peer_id": "2cr58yn1a5rdl13",
  "bytes_in": 1024576,
  "bytes_out": 2048000,
  "timestamp": "2025-11-18T10:30:00Z"
}
```

---

### 3. Traefik (v3.6.1)

**Proxy Reverso e Load Balancer**

**Responsabilidades:**
- ✅ Roteamento de tráfego HTTP/HTTPS
- ✅ Terminação SSL (Let's Encrypt automático)
- ✅ Load balancing entre backends
- ✅ Health checks de serviços
- ✅ Rate limiting
- ✅ Middlewares (auth, headers, redirect)

**Configuração:**
```yaml
Processo: PID 561660
CPU: 0.1%
Memória: 130 MB (3.2%)
Config: /etc/traefik/traefik_config.yml
Certificados: /app/config/letsencrypt/
```

**Rotas Principais:**
```
80/443 → gerbil:3003 → pangolin:3001
```

---

### 4. Newt (Cliente Desktop/Mobile)

**Cliente Tunelamento para Usuários Finais**

**Responsabilidades:**
- ✅ Conectar ao Pangolin via WireGuard
- ✅ Estabelecer túnel VPN seguro
- ✅ Registrar peer no servidor
- ✅ Manter conexão ativa
- ✅ Rotear tráfego através do túnel

**Tipos de Clientes:**
- Newt Desktop (Windows, macOS, Linux)
- Newt Mobile (iOS, Android)
- Olm (cliente web-based via WebRTC)

**Comunicação:**
- WebSocket persistente com Pangolin
- Mensagens: register, ping/pong, peer updates
- Heartbeat a cada 30s

---

## 🌐 API E ENDPOINTS

### API Base URL

```
Production: https://pangolin.keyanders.me
Local: http://localhost:3001
Internal: http://pangolin:3001
```

### API Key

```
API Key: io8yxoaf3emjt7n.dx2rr4bdcyjp42sc4wzddqixdbuywtatreudeb5g
Header: Authorization: Bearer <API_KEY>
```

### Endpoints Documentados

#### Gerbil Management

**1. Get Gerbil Configuration**
```http
GET /api/v1/gerbil/get-config
Authorization: Bearer <API_KEY>

Response:
{
  "peers": [...],
  "interface": {...},
  "routes": [...],
  "dns": {...}
}
```

**2. Report Bandwidth**
```http
POST /api/v1/gerbil/receive-bandwidth
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "peer_id": "2cr58yn1a5rdl13",
  "bytes_in": 1024,
  "bytes_out": 2048,
  "timestamp": "2025-11-18T10:30:00Z"
}
```

#### Organization Management

**3. Create Organization**
```http
POST /api/v1/organizations
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "name": "My Organization",
  "description": "Organization description"
}
```

**4. List Organizations**
```http
GET /api/v1/organizations
Authorization: Bearer <API_KEY>
```

**5. Update Organization**
```http
PUT /api/v1/organizations/:id
Content-Type: application/json
Authorization: Bearer <API_KEY>
```

#### Site Management

**6. Create Site**
```http
POST /api/v1/sites
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "organization_id": "org_123",
  "name": "Production Site",
  "subnet": "10.10.0.0/24"
}
```

**7. List Sites**
```http
GET /api/v1/sites?organization_id=org_123
Authorization: Bearer <API_KEY>
```

#### Resource Management

**8. Create Resource**
```http
POST /api/v1/resources
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "site_id": "site_456",
  "name": "Internal API",
  "type": "http",  // http | https | tcp | udp
  "target": "192.168.1.10:8080",
  "health_check": {
    "enabled": true,
    "endpoint": "/health",
    "interval": 30
  }
}
```

**9. List Resources**
```http
GET /api/v1/resources?site_id=site_456
Authorization: Bearer <API_KEY>
```

#### User Management

**10. Create User**
```http
POST /api/v1/users
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "email": "user@example.com",
  "name": "John Doe",
  "role_id": "role_789"
}
```

**11. List Users**
```http
GET /api/v1/users?organization_id=org_123
Authorization: Bearer <API_KEY>
```

#### Role Management

**12. Create Role**
```http
POST /api/v1/roles
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "organization_id": "org_123",
  "name": "Developer",
  "permissions": ["read", "write", "execute"]
}
```

**13. List Roles**
```http
GET /api/v1/roles?organization_id=org_123
Authorization: Bearer <API_KEY>
```

#### Shareable Links

**14. Create Shareable Link**
```http
POST /api/v1/shareable-links
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "resource_id": "res_999",
  "expires_at": "2025-12-31T23:59:59Z",  // null = permanent
  "max_uses": 100,  // null = unlimited
  "requires_pin": true,
  "pin": "1234"
}
```

**15. List Shareable Links**
```http
GET /api/v1/shareable-links
Authorization: Bearer <API_KEY>
```

#### API Keys

**16. Generate API Key**
```http
POST /api/v1/api-keys
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "name": "Production API Key",
  "scopes": ["organizations:read", "sites:write", "resources:*"],
  "expires_at": "2026-01-01T00:00:00Z"
}
```

**17. List API Keys**
```http
GET /api/v1/api-keys
Authorization: Bearer <API_KEY>
```

#### Blueprints (New in v1.12.2)

**18. Apply Blueprint**
```http
POST /api/v1/blueprints/apply
Content-Type: application/json
Authorization: Bearer <API_KEY>

Body:
{
  "blueprint": {
    "organizations": [...],
    "sites": [...],
    "resources": [...],
    "users": [...],
    "roles": [...]
  }
}
```

#### Health Check

**19. System Health**
```http
GET /api/v1/health

Response:
{
  "status": "healthy",
  "uptime": 1036800,
  "version": "1.12.2",
  "database": "connected",
  "peers": 7
}
```

#### Audit Logging (New in v1.12.2)

**20. Get Audit Logs**
```http
GET /api/v1/audit-logs?from=2025-11-01&to=2025-11-18
Authorization: Bearer <API_KEY>

Response:
{
  "logs": [
    {
      "timestamp": "2025-11-18T10:30:00Z",
      "user": "user@example.com",
      "action": "resource.create",
      "resource_id": "res_999",
      "ip": "203.0.113.1",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

### Swagger Documentation

**URL:** `https://pangolin.keyanders.me/api/docs`

Documentação interativa completa da API com:
- ✅ Todos endpoints disponíveis
- ✅ Schemas de request/response
- ✅ Try it out (testar direto no navegador)
- ✅ Exemplos de código (curl, JS, Python)

---

## 🔐 AUTENTICAÇÃO E SEGURANÇA

### Métodos de Autenticação

**1. Username/Password**
```http
POST /api/v1/auth/login
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "..."
}
```

**2. Email OTP (One-Time Password)**
```http
POST /api/v1/auth/otp/request
Body: { "email": "user@example.com" }

POST /api/v1/auth/otp/verify
Body: { "email": "user@example.com", "code": "123456" }
```

**3. PIN Code Protection**
```http
POST /api/v1/auth/pin
Body: { "resource_id": "res_999", "pin": "1234" }
```

**4. Two-Factor Authentication (2FA)**
```http
POST /api/v1/auth/2fa/enable
POST /api/v1/auth/2fa/verify
Body: { "code": "123456", "backup_code": "abc-def-123" }
```

**5. Security Keys (WebAuthn)**
```http
POST /api/v1/auth/webauthn/register
POST /api/v1/auth/webauthn/authenticate
```

**6. OAuth2/OIDC (SSO)**
```http
GET /api/v1/auth/oauth/authorize?provider=google
GET /api/v1/auth/oauth/callback?code=...
```

Provedores suportados:
- Google
- Microsoft Azure AD
- Okta
- Auth0
- Keycloak
- Generic OIDC

**7. API Keys**
```http
Header: Authorization: Bearer io8yxoaf3emjt7n.dx2rr4bdcyjp42sc4wzddqixdbuywtatreudeb5g
```

### Segurança de Rede

**Camadas de Proteção:**

1. **Firewall GCP**
   - Rules: http-server, https, lb-health-check
   - Apenas portas necessárias abertas

2. **SSL/TLS (Traefik + Let's Encrypt)**
   - Certificados automáticos
   - Renovação automática
   - TLS 1.2+ apenas

3. **Proxy Layer (Traefik)**
   - Rate limiting
   - Load balancing
   - DDoS protection básica

4. **Tunnel Layer (WireGuard)**
   - Criptografia de ponta-a-ponta
   - Key authentication
   - Perfect forward secrecy

5. **Application Layer (Pangolin)**
   - Helmet (security headers)
   - CORS configurado
   - Rate limiting (express-rate-limit)
   - JWT authentication
   - Argon2 password hashing
   - Input sanitization
   - SQL injection protection (ORM)
   - XSS protection

### Headers de Segurança (Helmet)

```http
X-DNS-Prefetch-Control: off
X-Frame-Options: SAMEORIGIN
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Download-Options: noopen
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### Criptografia

**Password Hashing:**
```javascript
// Argon2 settings
{
  timeCost: 3,
  memoryCost: 4096,
  parallelism: 1,
  hashLength: 32,
  type: argon2id
}
```

**JWT Tokens:**
```javascript
{
  algorithm: "HS256",
  expiresIn: "24h",  // access token
  refreshExpiresIn: "7d"  // refresh token
}
```

**WireGuard:**
```
Key Exchange: Curve25519
Cipher: ChaCha20-Poly1305
Hash: BLAKE2s
```

---

## 🖥️ SERVIDOR GCP

### Especificações da VM

**Informações Básicas:**
```yaml
Nome: pangolin
IP Externo: 34.9.79.106 (Premium tier)
IP Interno: 10.128.0.26
Zona: us-central1-c
Projeto: Mysql-OsTicket (iurd.mx)
Instance ID: 5883389919025055246
Machine Type: e2-medium
```

**Recursos:**
```yaml
vCPUs: 2 (Intel Broadwell)
RAM: 4 GB
Disco: 10 GB SSD (67% usado = 6.7GB)
Network: default (nic0)
```

**Sistema Operacional:**
```yaml
OS: Debian 12 (Bookworm)
Kernel: Linux 6.1.0
Arquitetura: x86_64
```

### Acesso SSH

**Método 1: SSH Direto**
```bash
ssh -i ~/.ssh/id_ed25519 admin@34.9.79.106
# ou
ssh admin@34.9.79.106  # se chave no ssh-agent
```

**Método 2: gcloud CLI**
```bash
gcloud compute ssh pangolin --project=Mysql-OsTicket --zone=us-central1-c
```

**Credenciais:**
```yaml
Host: 34.9.79.106
User: admin (ou andersongoliveira)
Key Type: ssh-ed25519
Key Email: andlee21@hotmail.com
Key Location (Mac): ~/.ssh/id_ed25519
```

### Docker Containers Status

```bash
CONTAINER ID   NAME       STATUS       PORTS                    UPTIME
2b575c707259   pangolin   Up 12 days   3001/tcp                 Healthy
...            gerbil     Up 12 days   80,443,3389,51820/udp    Healthy
...            traefik    Up 12 days   80,443                   Healthy
```

**Network:**
```yaml
Name: pangolin
Type: bridge
Subnet: 172.18.0.0/16
Gateway: 172.18.0.1

IPs:
- pangolin: 172.18.0.3
- gerbil: 172.18.0.2
```

### Uso de Recursos

**Estado Atual:**
```yaml
CPU Total: 2 vCPUs
CPU Uso: ~2-5% (idle)

RAM Total: 4 GB
RAM Usado: 971 MB (24%)
RAM Disponível: 2.9 GB (73%)

Disco Total: 10 GB
Disco Usado: 6.7 GB (67%)
Disco Livre: 3.1 GB (33%)
```

**Por Container:**
```yaml
Pangolin:
  CPU: 0.4%
  RAM: 237 MB (5.9%)

Gerbil:
  CPU: 0.0%
  RAM: 12 MB (0.3%)

Traefik:
  CPU: 0.1%
  RAM: 130 MB (3.2%)
```

### Backups

**Snapshots GCP:**
- Frequência: A cada 8 horas
- Retenção: 7 dias
- Automático: ✅ Ativo

**Backup Manual do Pangolin:**
```bash
# Backup completo do config
ssh admin@34.9.79.106 "sudo tar -czf /backup/pangolin_config_$(date +%Y%m%d_%H%M%S).tar.gz /home/admin/config/"

# Backup apenas SQLite
ssh admin@34.9.79.106 "sudo cp /home/admin/config/db/sqlite.db /backup/sqlite_$(date +%Y%m%d_%H%M%S).db"
```

**Localização Backups:**
```
/backup/20251117_030916/  # Último backup completo (824KB)
```

### Monitoramento

**Comandos de Status:**
```bash
# Status containers
ssh admin@34.9.79.106 "docker ps"

# Health checks
ssh admin@34.9.79.106 "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# Logs em tempo real
ssh admin@34.9.79.106 "docker logs -f pangolin"

# Uso de recursos
ssh admin@34.9.79.106 "docker stats --no-stream"
```

---

## 🚀 FUNCIONALIDADES AVANÇADAS

### 1. Blueprints (New in v1.12.2)

**O Que São:**
Templates declarativos para criar infraestrutura como código.

**Exemplo de Blueprint:**
```json
{
  "version": "1.0",
  "organizations": [
    {
      "name": "Production Org",
      "sites": [
        {
          "name": "Main Site",
          "subnet": "10.10.0.0/24",
          "resources": [
            {
              "name": "API Server",
              "type": "http",
              "target": "192.168.1.10:8080",
              "health_check": {
                "enabled": true,
                "endpoint": "/health",
                "interval": 30
              }
            }
          ]
        }
      ],
      "users": [
        {
          "email": "admin@company.com",
          "role": "admin"
        }
      ]
    }
  ]
}
```

**Como Aplicar:**
```bash
# Via API
curl -X POST https://pangolin.keyanders.me/api/v1/blueprints/apply \
  -H "Authorization: Bearer io8yxoaf3emjt7n..." \
  -H "Content-Type: application/json" \
  -d @blueprint.json

# Via Dashboard
# Settings → Blueprints → Import → Paste JSON → Apply
```

**Benefícios:**
- ✅ Infraestrutura como código
- ✅ Versionamento via Git
- ✅ Reprodutível e auditável
- ✅ Rollback fácil
- ✅ CI/CD integration

---

### 2. Geo-blocking (New in v1.12.2)

**Bloquear Acesso por País:**
```http
POST /api/v1/resources/:id/geo-blocking
Body:
{
  "mode": "blacklist",  // ou "whitelist"
  "countries": ["CN", "RU", "KP"]
}
```

**IP-based Blocking:**
```http
POST /api/v1/resources/:id/ip-blocking
Body:
{
  "mode": "blacklist",
  "ips": ["203.0.113.0/24", "198.51.100.5"]
}
```

**Uso no Dashboard:**
```
Resources → [Select Resource] → Access Control → Geo-blocking
- Select Mode: Blacklist / Whitelist
- Select Countries: [Multi-select dropdown]
- Save
```

---

### 3. Advanced Health Checks

**Configuração Completa:**
```json
{
  "health_check": {
    "enabled": true,
    "type": "http",  // http | https | tcp | icmp
    "endpoint": "/health",
    "method": "GET",
    "interval": 30,  // segundos
    "timeout": 5,
    "retries": 3,
    "expected_status": 200,
    "expected_body": "OK",
    "headers": {
      "Authorization": "Bearer token123"
    }
  }
}
```

**Estados:**
- 🟢 **Healthy**: Todos checks passando
- 🟡 **Degraded**: Alguns checks falhando
- 🔴 **Unhealthy**: Todos checks falhando

**Ações Automáticas:**
- Unhealthy → Remove do pool de load balancing
- Healthy → Adiciona de volta ao pool
- Alertas via webhook/email (configurável)

---

### 4. Audit Logging

**Eventos Rastreados:**
```
- User login/logout
- Resource creation/update/deletion
- Site creation/update/deletion
- Organization changes
- Role assignments
- Permission changes
- API key generation
- Failed authentication attempts
- Configuration changes
```

**Formato de Log:**
```json
{
  "timestamp": "2025-11-18T10:30:00.000Z",
  "event_id": "evt_abc123",
  "user_id": "usr_456",
  "user_email": "admin@company.com",
  "ip_address": "203.0.113.1",
  "user_agent": "Mozilla/5.0...",
  "action": "resource.create",
  "resource_type": "http_proxy",
  "resource_id": "res_999",
  "organization_id": "org_123",
  "details": {
    "name": "Production API",
    "target": "192.168.1.10:8080"
  },
  "result": "success"
}
```

**Consultar Logs:**
```bash
# Via API
curl https://pangolin.keyanders.me/api/v1/audit-logs?from=2025-11-01&to=2025-11-18 \
  -H "Authorization: Bearer io8yxoaf3emjt7n..."

# Via Dashboard
# Settings → Audit Logs → [Filter by date/user/action]
```

**Exportar:**
```bash
# JSON
GET /api/v1/audit-logs/export?format=json

# CSV
GET /api/v1/audit-logs/export?format=csv

# SIEM Integration (Syslog)
POST /api/v1/audit-logs/siem-webhook
```

---

### 5. Load Balancing

**Algoritmos Suportados:**
- Round Robin (padrão)
- Least Connections
- IP Hash (sticky sessions)
- Weighted Round Robin

**Configuração:**
```json
{
  "name": "API Load Balancer",
  "type": "http",
  "load_balancing": {
    "algorithm": "round_robin",
    "targets": [
      {
        "address": "192.168.1.10:8080",
        "weight": 1,
        "health_check": true
      },
      {
        "address": "192.168.1.11:8080",
        "weight": 2,
        "health_check": true
      }
    ]
  }
}
```

**Health Check Integration:**
- Targets unhealthy são removidos automaticamente
- Targets que voltam a healthy são re-adicionados
- Balanceamento só entre targets healthy

---

### 6. Shareable Links Avançado

**Configurações:**
```json
{
  "resource_id": "res_999",
  "expires_at": "2025-12-31T23:59:59Z",  // null = permanent
  "max_uses": 100,  // null = unlimited
  "requires_pin": true,
  "pin": "1234",
  "require_email_verification": true,
  "allowed_domains": ["company.com", "partner.com"],
  "require_2fa": false,
  "custom_slug": "prod-api-access",  // null = auto-generated
  "metadata": {
    "created_for": "External auditor",
    "purpose": "Q4 audit"
  }
}
```

**Link Gerado:**
```
https://pangolin.keyanders.me/share/prod-api-access
```

**Fluxo de Acesso:**
```
1. User clica no link
   ↓
2. Se requires_pin: Solicita PIN
   ↓
3. Se require_email_verification: Envia OTP
   ↓
4. Se require_2fa: Solicita 2FA
   ↓
5. Valida allowed_domains (se configurado)
   ↓
6. Incrementa uses_count
   ↓
7. Se uses_count > max_uses: Bloqueia
   ↓
8. Se expires_at < now: Bloqueia
   ↓
9. Grants access ✅
```

**Analytics:**
```http
GET /api/v1/shareable-links/:id/analytics

Response:
{
  "total_uses": 87,
  "unique_ips": 12,
  "last_access": "2025-11-18T09:00:00Z",
  "top_countries": ["US", "UK", "DE"],
  "top_user_agents": ["Chrome", "Firefox"]
}
```

---

## 💡 COMANDOS ÚTEIS

### Docker Management

**Ver Status:**
```bash
# Lista containers
ssh admin@34.9.79.106 "docker ps"

# Status detalhado com health
ssh admin@34.9.79.106 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# Uso de recursos
ssh admin@34.9.79.106 "docker stats --no-stream"
```

**Logs:**
```bash
# Logs do Pangolin (últimas 100 linhas)
ssh admin@34.9.79.106 "docker logs --tail 100 pangolin"

# Logs em tempo real
ssh admin@34.9.79.106 "docker logs -f pangolin"

# Logs com timestamp
ssh admin@34.9.79.106 "docker logs -t pangolin"

# Logs de todos containers
ssh admin@34.9.79.106 "docker compose -f /home/admin/docker-compose.yml logs -f"
```

**Restart:**
```bash
# Restart específico
ssh admin@34.9.79.106 "docker restart pangolin"

# Restart todos
ssh admin@34.9.79.106 "cd /home/admin && docker compose restart"

# Restart com rebuild
ssh admin@34.9.79.106 "cd /home/admin && docker compose up -d --force-recreate"
```

**Entrar no Container:**
```bash
# Shell interativo
ssh admin@34.9.79.106 "docker exec -it pangolin sh"

# Executar comando
ssh admin@34.9.79.106 "docker exec pangolin ls -la /app/config"
```

### Database Operations

**Acessar SQLite:**
```bash
# Entrar no SQLite
ssh admin@34.9.79.106 "docker exec -it pangolin sqlite3 /app/config/db/sqlite.db"

# Executar query
ssh admin@34.9.79.106 "docker exec pangolin sqlite3 /app/config/db/sqlite.db 'SELECT * FROM users LIMIT 5;'"

# Export database
ssh admin@34.9.79.106 "docker exec pangolin sqlite3 /app/config/db/sqlite.db '.dump'" > pangolin_dump.sql
```

**Queries Úteis:**
```sql
-- Listar tabelas
.tables

-- Schema de uma tabela
.schema users

-- Contar registros
SELECT COUNT(*) FROM users;

-- Últimos 10 audit logs
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;

-- Peers ativos
SELECT * FROM peers WHERE status = 'active';

-- Resources por tipo
SELECT type, COUNT(*) FROM resources GROUP BY type;
```

### Configuration Management

**Ver Configuração:**
```bash
# Config principal
ssh admin@34.9.79.106 "sudo cat /home/admin/config/config.yml"

# Docker Compose
ssh admin@34.9.79.106 "cat /home/admin/docker-compose.yml"

# Traefik config
ssh admin@34.9.79.106 "sudo cat /home/admin/config/traefik/traefik_config.yml"
```

**Editar Configuração:**
```bash
# Backup antes de editar
ssh admin@34.9.79.106 "sudo cp /home/admin/config/config.yml /backup/config.yml.$(date +%Y%m%d_%H%M%S)"

# Editar
ssh admin@34.9.79.106 "sudo nano /home/admin/config/config.yml"

# Aplicar mudanças (restart)
ssh admin@34.9.79.106 "docker restart pangolin"
```

### Backup e Restore

**Backup Completo:**
```bash
# Backup de tudo
ssh admin@34.9.79.106 "sudo tar -czf /backup/pangolin_full_$(date +%Y%m%d_%H%M%S).tar.gz /home/admin/config/ /home/admin/docker-compose.yml"

# Download backup
scp admin@34.9.79.106:/backup/pangolin_full_*.tar.gz ./backups/
```

**Backup Incremental:**
```bash
# Apenas database
ssh admin@34.9.79.106 "sudo cp /home/admin/config/db/sqlite.db /backup/sqlite_$(date +%Y%m%d_%H%M%S).db"

# Apenas configs
ssh admin@34.9.79.106 "sudo tar -czf /backup/configs_$(date +%Y%m%d_%H%M%S).tar.gz /home/admin/config/*.yml"
```

**Restore:**
```bash
# Upload backup
scp ./backups/pangolin_full_20251118.tar.gz admin@34.9.79.106:/tmp/

# Parar serviços
ssh admin@34.9.79.106 "cd /home/admin && docker compose down"

# Restaurar
ssh admin@34.9.79.106 "sudo tar -xzf /tmp/pangolin_full_20251118.tar.gz -C /"

# Reiniciar
ssh admin@34.9.79.106 "cd /home/admin && docker compose up -d"
```

### Atualização de Versões

**Atualizar Pangolin:**
```bash
# Backup primeiro!
ssh admin@34.9.79.106 "sudo tar -czf /backup/pre_update_$(date +%Y%m%d_%H%M%S).tar.gz /home/admin/config/"

# Pull nova imagem
ssh admin@34.9.79.106 "docker pull fosrl/pangolin:latest"

# Atualizar docker-compose.yml com nova versão
ssh admin@34.9.79.106 "sed -i 's/fosrl\/pangolin:1.12.2/fosrl\/pangolin:1.13.0/g' /home/admin/docker-compose.yml"

# Recreate container
ssh admin@34.9.79.106 "cd /home/admin && docker compose up -d --force-recreate pangolin"

# Verificar logs
ssh admin@34.9.79.106 "docker logs -f pangolin"
```

### Monitoramento

**Check Health:**
```bash
# Health check endpoint
curl -f https://pangolin.keyanders.me/api/v1/health

# Via SSH
ssh admin@34.9.79.106 "curl -f http://localhost:3001/api/v1/health"
```

**Peers Conectados:**
```bash
# Via API
curl https://pangolin.keyanders.me/api/v1/peers \
  -H "Authorization: Bearer io8yxoaf3emjt7n..."

# Via database
ssh admin@34.9.79.106 "docker exec pangolin sqlite3 /app/config/db/sqlite.db 'SELECT COUNT(*) FROM peers WHERE status=\"active\";'"
```

**Uso de Recursos:**
```bash
# CPU e RAM de todos containers
ssh admin@34.9.79.106 "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'"

# Disco
ssh admin@34.9.79.106 "df -h /home/admin/config"

# Network stats
ssh admin@34.9.79.106 "docker stats --no-stream --format 'table {{.Name}}\t{{.NetIO}}'"
```

---

## ⚠️ TROUBLESHOOTING

### Problema 1: Container Unhealthy

**Sintomas:**
```
docker ps mostra (unhealthy) para pangolin
```

**Diagnóstico:**
```bash
# Ver health check logs
ssh admin@34.9.79.106 "docker inspect pangolin | grep -A 10 Health"

# Testar health endpoint manualmente
ssh admin@34.9.79.106 "docker exec pangolin curl -f http://localhost:3001/api/v1/health"
```

**Soluções:**
1. Ver logs de erro
2. Restart container
3. Verificar config.yml
4. Verificar porta 3001 livre

---

### Problema 2: Peers Não Conectando

**Sintomas:**
```
Clientes Newt não conseguem estabelecer túnel
```

**Diagnóstico:**
```bash
# Ver logs do Gerbil
ssh admin@34.9.79.106 "docker logs gerbil | tail -50"

# Verificar WireGuard
ssh admin@34.9.79.106 "docker exec gerbil wg show"

# Verificar portas
ssh admin@34.9.79.106 "sudo netstat -tulpn | grep 51820"
```

**Soluções:**
1. Verificar firewall (porta 51820/UDP aberta)
2. Restart Gerbil
3. Verificar configuração WireGuard
4. Regenerar chaves se necessário

---

### Problema 3: Disco Cheio

**Sintomas:**
```
docker ps mostra erro ou containers param
df -h mostra 100% uso
```

**Diagnóstico:**
```bash
# Ver uso detalhado
ssh admin@34.9.79.106 "du -sh /home/admin/config/*"

# Verificar logs grandes
ssh admin@34.9.79.106 "du -sh /home/admin/config/logs/*"
```

**Soluções:**
```bash
# Limpar logs antigos (>30 dias)
ssh admin@34.9.79.106 "find /home/admin/config/logs/ -name '*.log' -mtime +30 -delete"

# Limpar imagens Docker não usadas
ssh admin@34.9.79.106 "docker system prune -a -f"

# Limpar volumes órfãos
ssh admin@34.9.79.106 "docker volume prune -f"
```

---

### Problema 4: SSL Certificate Error

**Sintomas:**
```
HTTPS não funciona ou certificado expirado
```

**Diagnóstico:**
```bash
# Ver certificados
ssh admin@34.9.79.106 "sudo ls -la /home/admin/config/letsencrypt/certificates/"

# Verificar Traefik logs
ssh admin@34.9.79.106 "docker logs traefik | grep -i certificate"
```

**Soluções:**
```bash
# Forçar renovação (Traefik faz automático)
ssh admin@34.9.79.106 "docker restart traefik"

# Verificar se DNS está apontando correto
nslookup pangolin.keyanders.me

# Se necessário, limpar e reemitir
ssh admin@34.9.79.106 "sudo rm -rf /home/admin/config/letsencrypt/certificates/*"
ssh admin@34.9.79.106 "docker restart traefik"
```

---

### Problema 5: Database Locked

**Sintomas:**
```
Erros "database is locked" nos logs
```

**Diagnóstico:**
```bash
# Ver processos usando database
ssh admin@34.9.79.106 "docker exec pangolin fuser /app/config/db/sqlite.db"

# Ver logs específicos
ssh admin@34.9.79.106 "docker logs pangolin | grep -i 'database locked'"
```

**Soluções:**
```bash
# Restart Pangolin (última opção)
ssh admin@34.9.79.106 "docker restart pangolin"

# Se problema persistir, migrar para PostgreSQL
# (SQLite tem limitações em alta concorrência)
```

---

### Problema 6: High Memory Usage

**Sintomas:**
```
Container usando >1GB RAM
Sistema lento
```

**Diagnóstico:**
```bash
# Memória detalhada
ssh admin@34.9.79.106 "docker stats --no-stream pangolin"

# Processos internos
ssh admin@34.9.79.106 "docker exec pangolin ps aux"
```

**Soluções:**
```bash
# Limitar memória do container
# Editar docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 512M

# Restart com limite
ssh admin@34.9.79.106 "cd /home/admin && docker compose up -d --force-recreate"

# Upgrade VM se necessário (4GB → 8GB)
gcloud compute instances stop pangolin --zone=us-central1-c
gcloud compute instances set-machine-type pangolin --machine-type=e2-standard-2 --zone=us-central1-c
gcloud compute instances start pangolin --zone=us-central1-c
```

---

## 📚 RECURSOS ADICIONAIS

### Documentação Oficial

- **Docs:** https://docs.pangolin.net
- **GitHub:** https://github.com/fosrl/pangolin
- **Releases:** https://github.com/fosrl/pangolin/releases
- **Issues:** https://github.com/fosrl/pangolin/issues
- **Discussions:** https://github.com/fosrl/pangolin/discussions

### Comunidade

- **Discord:** (verificar no GitHub)
- **Reddit:** r/selfhosted (menções a Pangolin)
- **Blog Posts:**
  - https://noted.lol/pangolin/
  - https://leewc.com/articles/self-hosted-cloudflared-tailscale-alternative-pangolin/
  - https://eve.gd/2025/10/04/pangolin-newt-gerbil-and-custom-ports/

### Alternativas Comparadas

| Feature | Pangolin | Cloudflare Tunnel | Tailscale | ngrok |
|---------|----------|-------------------|-----------|-------|
| **Self-Hosted** | ✅ Sim | ❌ Não | ❌ Não | ❌ Não |
| **Open Source** | ✅ AGPL-3 | ❌ Proprietário | ❌ Proprietário | ❌ Proprietário |
| **Custom Domain** | ✅ Sim | ✅ Sim | ⚠️ Limitado | ⚠️ Limitado |
| **IAM Built-in** | ✅ Sim | ⚠️ Cloudflare Access | ❌ Não | ⚠️ Basic |
| **Load Balancing** | ✅ Sim | ✅ Sim | ❌ Não | ⚠️ Paid |
| **Geo-blocking** | ✅ Sim | ✅ Sim | ❌ Não | ❌ Não |
| **Audit Logging** | ✅ Sim | ✅ Sim | ❌ Não | ⚠️ Paid |
| **Cost** | 💰 Server only | 💰💰 Paid plans | 💰💰 Paid plans | 💰💰💰 Expensive |
| **Privacy** | ✅ Total | ⚠️ Cloudflare | ⚠️ Tailscale | ⚠️ ngrok |

---

## 🎓 PRÓXIMOS PASSOS DE APRENDIZADO

### Fase 1: Exploração Básica ✅
- [x] Entender arquitetura geral
- [x] Conhecer componentes (Pangolin, Gerbil, Traefik)
- [x] Acesso SSH ao servidor
- [x] Documentação inicial

### Fase 2: API e Integração 🔄
- [ ] Testar todos endpoints da API
- [ ] Criar scripts de automação
- [ ] Integrar com CI/CD
- [ ] Configurar webhooks

### Fase 3: Administração Avançada
- [ ] Blueprints avançados
- [ ] Migração para PostgreSQL
- [ ] Configurar backup automático
- [ ] Monitoring com Prometheus/Grafana
- [ ] Alertas via Slack/Discord

### Fase 4: Desenvolvimento
- [ ] Contribuir para o projeto
- [ ] Criar plugins/extensões
- [ ] Custom authentication providers
- [ ] Tema customizado do dashboard

---

## 📝 CHANGELOG DESTE DOCUMENTO

**2025-11-18:**
- ✅ Criação inicial do documento
- ✅ Documentação completa de arquitetura
- ✅ Mapeamento de API endpoints
- ✅ Comandos úteis e troubleshooting
- ✅ Recursos avançados (v1.12.2)

---

**Última Atualização:** 2025-11-18
**Mantido por:** Claude AI + Anderson
**Versão:** 1.0
**Status:** 🟢 Completo e Atualizado

---

🦎 **Pangolin Platform - Você agora é um especialista!** 🔥
