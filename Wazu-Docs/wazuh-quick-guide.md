# 📋 WAZUH - GUIA RÁPIDO DE FONTES PARA CLAUDE CODE & RAG

## ✅ ARQUIVOS GERADOS

| Arquivo | Descrição | Tamanho |
|---------|-----------|--------|
| `wazuh-rag-complete.md` | Documentação completa (12 seções) | ~15KB |
| `wazuh_sources_consolidated.json` | Base de dados JSON estruturada | Pronto |

---

## 🔗 REPOSITÓRIOS OFICIAIS (GitHub)

### Core & Management
```
https://github.com/wazuh/wazuh
├─ Manager (Central processing)
├─ Agent (Endpoint collection)
├─ Core em C/C++
└─ Issues: https://github.com/wazuh/wazuh/issues
```

### API & Integration
```
https://github.com/wazuh/wazuh-api
├─ RESTful API
├─ JWT Authentication
├─ Node.js backend
└─ Exemplos: Python, PowerShell, cURL
```

### Dashboard & UI
```
https://github.com/wazuh/wazuh-dashboard-plugins
├─ React components
├─ Kibana integration
└─ Visualizações customizadas
```

### Container Orchestration
```
https://github.com/wazuh/wazuh-kubernetes
├─ Helm Charts (oficial)
├─ StatefulSets, DaemonSets
├─ ConfigMaps & Secrets
└─ Production-ready configs
```

```
https://github.com/kajov/wazuh-kubernetes-helmchart
├─ Helm Chart (comunidade)
├─ Helm 2.16.12 compatible
└─ Planejamento Helm 3
```

---

## 📚 DOCUMENTAÇÃO OFICIAL

### Homepage Principal
```
https://documentation.wazuh.com
```

### Documentação por Módulo

#### File Integrity Monitoring (FIM)
```
Portal: https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/
├─ Capabilities: File monitoring, checksums, real-time alerts
├─ PoC Guide: Hands-on example
├─ Use Cases: Compliance scenarios
├─ Compliance: PCI DSS, HIPAA, NIST 800-53, GDPR
└─ Integração: CDB lists + threat intelligence
```

#### RESTful API
```
Portal: https://documentation.wazuh.com/current/api/index.html
├─ Getting Started: https://documentation.wazuh.com/current/user-manual/api/getting-started.html
├─ Authentication: JWT Bearer Token
├─ Endpoints: /agents, /manager, /groups, /rules, /lists
├─ Métodos: GET, POST, PUT, DELETE
└─ Exemplos: Python, PowerShell, cURL
```

#### Security Configuration Assessment (SCA)
```
Portal: https://documentation.wazuh.com/current/user-manual/capabilities/configuration-assessment/
├─ Capabilities: Policy-based scanning
├─ Benchmarks: CIS, PCI DSS, HIPAA, NIST, Custom
├─ Format: YAML policies
├─ Location: /var/ossec/ruleset/sca/
└─ Compliance: Multi-regulatory support
```

#### Vulnerability Detection
```
Portal: https://documentation.wazuh.com/current/user-manual/capabilities/vulnerability-detection/
├─ Integration: Syscollector
├─ Databases: NVD, Ubuntu, Debian, Red Hat, Windows
├─ CVE: CVSS scoring, patch recommendations
└─ Compliance: Automated updates tracking
```

#### CDB Lists & Threat Intelligence
```
Portal: https://documentation.wazuh.com/current/user-manual/ruleset/cdb-list.html
├─ Format: Key-value pairs
├─ Uses: Malware hashes, IP lists, domains, allow/deny
├─ Integration: FIM + CDB lists for malware detection
└─ Sources: AlienVault OTX, VirusTotal, Custom
```

#### Kubernetes & Helm
```
Portal: https://documentation.wazuh.com/current/deployment-options/docker/kubernetes/
├─ Helm Deployment: https://documentation.wazuh.com/current/deployment-options/docker/kubernetes/wazuh-helm-chart.html
├─ Components: Manager, Elasticsearch, Dashboard, Agent
├─ Storage: PersistentVolumes
└─ Services: LoadBalancer, ClusterIP
```

### Troubleshooting & Support
```
Troubleshooting: https://documentation.wazuh.com/current/user-manual/manager/troubleshooting.html
Release Notes: https://github.com/wazuh/wazuh/releases
Security Advisories: https://github.com/wazuh/wazuh/security/advisories
Community Forum: https://wazuh.com/community/
```

---

## 🛠️ STACK TECNOLÓGICO

### Backend
- **Core**: C/C++
- **Scripting**: Python, Shell/Bash
- **API**: Node.js

### Search & Indexing
- **Elasticsearch**: 7.10+
- **OpenSearch**: 1.0+ (alternativa)
- **Wazuh Indexer**: 4.3+ (proprietário)

### Frontend & UI
- **React**: 16.8+
- **Kibana**: 7.10+ (legacy integration)
- **Wazuh Dashboard**: 2.0+ (modern UI)

### Data Processing
- **Filebeat**: 7.10+
- **Logstash**: 7.10+ (opcional)

### Container & Orchestration
- **Docker**: 20.0+
- **Kubernetes**: 1.14+
- **Helm**: 2.16.12+ (Helm 3 planned)

### Communication
- **Protocols**: HTTPS/TLS, REST API, Syslog
- **Ports**: TCP/1514 (Agent-Manager), UDP/514 (Syslog)
- **Authentication**: JWT Bearer, SSL/TLS

---

## ⚠️ ISSUES CONHECIDAS & SOLUÇÕES

### 1. Elasticsearch Sharding
**GitHub Issue**: https://github.com/wazuh/wazuh-kibana-app/issues/1016
- **Problema**: Red/Yellow status em índices
- **Causa**: Shards não alocados
- **Solução**: Rebalancear e reiniciar serviço

### 2. GitHub Integration 404
**GitHub Issue**: https://github.com/wazuh/wazuh/issues/14964
- **Problema**: Erro 404 ao coletar dados GitHub
- **Causa**: Requer GitHub Enterprise Cloud + escopos específicos
- **Solução**: PAT com `admin:org` e `read:audit_log`

### 3. Agent Connection
- **Problema**: Agent não conecta no Manager
- **Causas**: Firewall, DNS, permissões, certificados
- **Debug**: telnet, nslookup, restart agent

### 4. API Token Issues
- **Problema**: JWT token expirado
- **Solução**: Regenerar via `/security/user/authenticate`

### 5. Memory Issues
- **Problema**: Manager/ES usando muita memória
- **Soluções**: Aumentar heap, index rotation, disable modules

### 6. Kubernetes CrashLoop
- **Problema**: Pods não iniciam
- **Debug**: `kubectl logs`, `describe pod`, PVC check

---

## 📦 INSTALAÇÃO AGENTS

### Linux (Ubuntu/Debian)
```bash
# Repository
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -
echo "deb https://packages.wazuh.com/4.x/apt/ stable main" > /etc/apt/sources.list.d/wazuh.list
apt-get update && apt-get install -y wazuh-agent

# Start
systemctl enable wazuh-agent && systemctl start wazuh-agent
```

### Windows (PowerShell)
```powershell
# Download
$uri = "https://packages.wazuh.com/4.7.4/windows/wazuh-agent-4.7.4-1.msi"
Invoke-WebRequest -Uri $uri -OutFile wazuh-agent.msi

# Install
msiexec.exe /i wazuh-agent.msi /q WAZUH_MANAGER="192.168.1.100"

# Start
Start-Service WazuhSvc
```

### macOS (Homebrew)
```bash
brew install wazuh-agent
sudo defaults write /Library/Preferences/com.wazuh.agent MANAGER_IP 192.168.1.100
sudo launchctl start com.wazuh.agent
```

### Docker
```bash
docker run -d --name wazuh-agent \
  -e WAZUH_MANAGER="192.168.1.100" \
  -e WAZUH_AGENT_NAME="docker-agent" \
  wazuh/wazuh-agent:latest
```

---

## 🔍 CONFIGURAÇÃO PRINCIPAL

### FIM Configuration (XML)
```xml
<syscheck>
  <disabled>no</disabled>
  <directories check_all="yes" realtime="yes">/etc</directories>
  <directories check_all="yes" realtime="yes">/home</directories>
  <ignore>/etc/mtab</ignore>
</syscheck>
```

### SCA Configuration
```xml
<sca>
  <enabled>yes</enabled>
  <scan_on_start>yes</scan_on_start>
  <interval>24h</interval>
  <policy path="/var/ossec/ruleset/sca/cis_ubuntu_linux_22.04_l1.yml" />
</sca>
```

### Vulnerability Detection
```xml
<vulnerability-detection>
  <enabled>yes</enabled>
  <index-status>yes</index-status>
  <feed-update-interval>60m</feed-update-interval>
</vulnerability-detection>
```

---

## 🔌 API ENDPOINTS PRINCIPAIS

### Autenticação
```bash
POST /security/user/authenticate
Header: Authorization: Basic <base64>
Response: { "data": { "token": "eyJ..." } }
```

### Agentes
```
GET    /agents
GET    /agents/summary/status
GET    /agents/{id}/stats/hourly
POST   /agents
DELETE /agents/{id}
```

### Manager
```
GET /manager/info
GET /manager/logs
GET /manager/logs/summary
```

### Grupos
```
GET  /groups
POST /groups
PUT  /groups/{id}
```

### Regras
```
GET /rules
GET /decoders
```

### CDB Lists
```
GET  /lists/files
POST /lists/files
```

---

## 📊 COMPLIANCE FRAMEWORKS SUPORTADOS

| Framework | FIM | SCA | Vulnerability | Link |
|-----------|-----|-----|----------------|------|
| **PCI DSS** | ✅ | ✅ | ✅ | https://documentation.wazuh.com/current/compliance/pci_dss/ |
| **HIPAA** | ✅ | ✅ | ✅ | https://documentation.wazuh.com/current/compliance/hipaa/ |
| **NIST 800-53** | ✅ | ✅ | ✅ | https://documentation.wazuh.com/current/compliance/nist_800_53/ |
| **GDPR** | ✅ | ✅ | ✅ | https://documentation.wazuh.com/current/compliance/gdpr/ |
| **CIS Benchmarks** | - | ✅ | - | https://documentation.wazuh.com/current/user-manual/capabilities/configuration-assessment/ |
| **SOC 2** | ✅ | ✅ | ✅ | - |
| **ISO 27001** | ✅ | ✅ | ✅ | - |

---

## 🚀 PRÓXIMOS PASSOS - CLAUDE CODE

### 1. Import Documentation
```bash
# Copiar arquivos
- wazuh-rag-complete.md (documentação)
- wazuh_sources_consolidated.json (base de dados)
```

### 2. Create Knowledge Base
```python
# Estrutura sugerida
/knowledge_base
├── /docs
│   ├── wazuh-rag-complete.md
│   ├── api-reference.md
│   ├── modules/
│   │   ├── fim.md
│   │   ├── sca.md
│   │   ├── vulnerability-detection.md
│   │   └── kubernetes.md
│   └── troubleshooting.md
└── /data
    └── wazuh_sources_consolidated.json
```

### 3. RAG Configuration
```python
# Embeddings para busca semântica
- Criar embeddings dos documentos
- Indexar em vector DB (Pinecone, Weaviate, etc)
- Configurar retrieval com similarity search
```

### 4. Agent Training
```python
# Fine-tuning com contexto Wazuh
- Usar documentação como context window
- Exemplos de respostas esperadas
- Padrões de troubleshooting
- Best practices
```

---

## 📌 ÍNDICE DE LINKS RÁPIDOS

### Oficial
- Docs: https://documentation.wazuh.com
- GitHub: https://github.com/wazuh/wazuh
- Community: https://wazuh.com/community/

### Módulos
- FIM: https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/
- API: https://documentation.wazuh.com/current/api/index.html
- SCA: https://documentation.wazuh.com/current/user-manual/capabilities/configuration-assessment/
- Kubernetes: https://documentation.wazuh.com/current/deployment-options/docker/kubernetes/

### Issues & Referências
- Elasticsearch Sharding: https://github.com/wazuh/wazuh-kibana-app/issues/1016
- GitHub Integration: https://github.com/wazuh/wazuh/issues/14964
- Troubleshooting: https://documentation.wazuh.com/current/user-manual/manager/troubleshooting.html

---

## ✅ CHECKLIST PARA RAG

- [ ] Baixar wazuh-rag-complete.md
- [ ] Importar wazuh_sources_consolidated.json
- [ ] Criar embeddings da documentação
- [ ] Testar retrieval com queries comuns
- [ ] Treinar agent com exemplos
- [ ] Validar respostas contra documentação
- [ ] Implementar feedback loop
- [ ] Documentar padrões de uso

---

**Última atualização**: 2025-11-18
**Versão documentada**: Wazuh 4.7.4
**Status**: ✅ Pronto para RAG

