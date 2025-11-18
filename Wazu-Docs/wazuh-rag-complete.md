# WAZUH OPEN SOURCE - DOCUMENTAÇÃO COMPLETA PARA RAG
**Consolidação total: Fontes, Módulos, Issues, Technologies, APIs**

---

## 📑 ÍNDICE RÁPIDO

1. [Repositórios Oficiais](#repositórios-oficiais)
2. [Documentação Principal](#documentação-principal)
3. [Módulo FIM (File Integrity Monitoring)](#módulo-fim-file-integrity-monitoring)
4. [Módulo API (RESTful)](#módulo-api-restful)
5. [Módulo Kubernetes & Helm](#módulo-kubernetes--helm)
6. [Módulo SCA (Security Configuration Assessment)](#módulo-sca-security-configuration-assessment)
7. [Módulo Vulnerability Detection](#módulo-vulnerability-detection)
8. [CDB Lists & Threat Intelligence](#cdb-lists--threat-intelligence)
9. [Stack Tecnológico](#stack-tecnológico)
10. [Issues Conhecidas & Soluções](#issues-conhecidas--soluções)
11. [Instalação de Agents](#instalação-de-agents)
12. [Troubleshooting](#troubleshooting)

---

## 🔗 REPOSITÓRIOS OFICIAIS

### Core & Principal
- **Wazuh Principal (Manager + Agent)**: https://github.com/wazuh/wazuh
  - Core do sistema em C/C++
  - Agent para coleta de dados
  - Documentação técnica completa

### APIs & Integração
- **Wazuh API (RESTful)**: https://github.com/wazuh/wazuh-api
  - Autenticação JWT
  - Endpoints REST completos
  - Exemplos Python, PowerShell, cURL

### Dashboard & UI
- **Wazuh Dashboard Plugins**: https://github.com/wazuh/wazuh-dashboard-plugins
  - Visualizações customizadas
  - Integração com Kibana
  - Componentes React

### Container & Orquestração
- **Wazuh Kubernetes**: https://github.com/wazuh/wazuh-kubernetes
  - Helm Charts para deployment
  - StatefulSets, DaemonSets
  - ConfigMaps e Secrets

- **Wazuh Deployment Guide**: https://github.com/wazuh/wazuh-deployment-guide
  - Step-by-step deployment
  - Production-ready configs
  - Troubleshooting

### Comunidade (Helm Chart Alternativo)
- **Helm Chart Comunitário**: https://github.com/kajov/wazuh-kubernetes-helmchart
  - Alternativa mantida pela comunidade
  - Suporte a Helm 2 (v2.16.12)
  - Planejamento para Helm 3

---

## 📚 DOCUMENTAÇÃO PRINCIPAL

### Portal Oficial
| Recurso | URL | Descrição |
|---------|-----|-----------|
| **Homepage Docs** | https://documentation.wazuh.com | Entrada principal |
| **Quickstart** | https://documentation.wazuh.com/current/quickstart.html | Guia de 5 minutos |
| **Installation Guide** | https://documentation.wazuh.com/current/installation-guide/index.html | Setup completo |
| **Troubleshooting** | https://documentation.wazuh.com/current/user-manual/manager/troubleshooting.html | Debugging |
| **Release Notes** | https://github.com/wazuh/wazuh/releases | Changelog oficial |

### Comunidade & Suporte
- **Wazuh Community**: https://wazuh.com/community/
- **GitHub Issues**: https://github.com/wazuh/wazuh/issues
- **Security Advisories**: https://github.com/wazuh/wazuh/security/advisories
- **Reddit Discussions**: https://reddit.com/r/Wazuh

---

## 🔍 MÓDULO FIM (FILE INTEGRITY MONITORING)

### Documentação Oficial
- **FIM Capabilities**: https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html
- **FIM Proof of Concept**: https://documentation.wazuh.com/current/proof-of-concept-guide/poc-file-integrity-monitoring.html
- **FIM Use Cases**: https://documentation.wazuh.com/current/use-cases/file-integrity-monitoring.html
- **FIM + HIPAA Compliance**: https://documentation.wazuh.com/current/compliance/hipaa/index.html
- **FIM + NIST 800-53 Compliance**: https://documentation.wazuh.com/current/compliance/nist_800_53/index.html

### Como Funciona FIM

#### Funcionamento Básico
1. **Baseline Scan**: Cria snapshot criptográfico dos arquivos monitorados
2. **Monitoramento**: Real-time e scheduled scans
3. **Comparação**: Compara checksum e atributos contra baseline
4. **Alertas**: Detecta criação, modificação e exclusão de arquivos

#### Atributos Monitorados
- Checksum MD5/SHA256
- Permissions (mode)
- Owner & Group
- File size
- Last modification date
- Inode
- Registry keys (Windows)

### Configuração FIM

#### Linux Configuration (agent)
```xml
<ossec_config>
  <syscheck>
    <disabled>no</disabled>
    
    <!-- Real-time monitoring -->
    <directories check_all="yes" realtime="yes">/etc</directories>
    <directories check_all="yes" realtime="yes">/home</directories>
    <directories check_all="yes" realtime="yes">/opt</directories>
    
    <!-- Scheduled scans -->
    <directories check_all="yes">/var/www</directories>
    
    <!-- Exclude patterns -->
    <ignore>/etc/mtab</ignore>
    <ignore>/etc/hosts.allow</ignore>
  </syscheck>
</ossec_config>
```

#### Windows Configuration
- Registry keys monitoramento
- File system monitoramento
- Real-time e scheduled options

### Integração FIM com CDB Lists
```xml
<group name="malware,">
  <rule id="110002" level="13">
    <if_sid>554, 550</if_sid>
    <list field="md5" lookup="match_key">etc/lists/malware-hashes</list>
    <description>File with known malware hash detected: $(file)</description>
  </rule>
</group>
```

### Dashboard FIM
- **Inventory**: Lista de todos os arquivos indexados
- **Alerts**: Eventos gerados por mudanças
- **Statistics**: Overview de modificações

### Compliance com FIM
- **PCI DSS**: Monitoramento de arquivos críticos
- **HIPAA**: Protected Health Information (PHI) protection
- **NIST 800-53**: CM-6 Configuration Settings
- **GDPR**: Data integrity monitoring

---

## 🔌 MÓDULO API (RESTful)

### Documentação Oficial
- **API Getting Started**: https://documentation.wazuh.com/current/user-manual/api/getting-started.html
- **API Reference**: https://documentation.wazuh.com/current/api/index.html
- **API Endpoints**: https://documentation.wazuh.com/current/user-manual/api/reference.html

### Estrutura da API

#### Autenticação
```bash
# Obter JWT Token
curl -k -X POST "https://localhost:55000/security/user/authenticate" \
  -H "Authorization: Basic $(echo -n 'wazuh:wazuh' | base64)" \
  -H "Content-Type: application/json"

# Resposta
{
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

#### Headers Necessários
```
Authorization: Bearer <TOKEN>
Content-Type: application/json
```

#### Resposta Padrão
```json
{
  "error": 0,
  "data": {
    "affected_items": [...],
    "total_affected_items": 10,
    "total_items": 100
  }
}
```

### Principais Endpoints

#### Agentes
- `GET /agents` - Listar agentes
- `GET /agents/summary/status` - Status resumido
- `POST /agents` - Adicionar agente
- `DELETE /agents/{agent_id}` - Deletar agente
- `GET /agents/{agent_id}/stats/hourly` - Estatísticas

#### Manager
- `GET /manager/info` - Informações do manager
- `GET /manager/logs` - Logs do manager
- `GET /manager/logs/summary` - Resumo de logs

#### Groups
- `GET /groups` - Listar grupos
- `POST /groups` - Criar grupo
- `PUT /groups/{group_id}` - Atualizar grupo

#### Rules & Decoders
- `GET /rules` - Listar rules
- `GET /decoders` - Listar decoders

#### CDB Lists
- `GET /lists/files` - Listar CDB lists
- `POST /lists/files` - Upload lista

### Exemplos de Uso

#### Python
```python
import requests
import json
from base64 import b64encode

host = "localhost"
port = 55000
user = "wazuh"
password = "wazuh"

# Autenticação
auth = f"{user}:{password}".encode()
headers = {
    'Authorization': f'Basic {b64encode(auth).decode()}',
    'Content-Type': 'application/json'
}

login_url = f"https://{host}:{port}/security/user/authenticate"
response = requests.post(login_url, headers=headers, verify=False)
token = response.json()["data"]["token"]

# Usar token
headers['Authorization'] = f'Bearer {token}'

# Listar agentes
agents_url = f"https://{host}:{port}/agents?pretty=true"
response = requests.get(agents_url, headers=headers, verify=False)
print(json.dumps(response.json(), indent=4))
```

#### PowerShell
```powershell
$host = "localhost"
$port = 55000
$user = "wazuh"
$password = "wazuh"

$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${password}"))
$headers = @{
    'Authorization' = "Basic $base64AuthInfo"
    'Content-Type' = 'application/json'
}

$loginUrl = "https://${host}:${port}/security/user/authenticate"
$response = Invoke-RestMethod -Uri $loginUrl -Headers $headers -SkipCertificateCheck

$headers['Authorization'] = "Bearer " + $response.data.token

# Usar token
$agentsUrl = "https://${host}:${port}/agents"
$agents = Invoke-RestMethod -Uri $agentsUrl -Headers $headers -SkipCertificateCheck
$agents.data | ConvertTo-Json
```

#### cURL
```bash
# Autenticar
TOKEN=$(curl -s -k -X POST "https://localhost:55000/security/user/authenticate" \
  -H "Authorization: Basic $(echo -n 'wazuh:wazuh' | base64)" \
  -H "Content-Type: application/json" | jq -r '.data.token')

# Usar token
curl -k -X GET "https://localhost:55000/agents/summary/status?pretty=true" \
  -H "Authorization: Bearer $TOKEN"
```

### Parâmetros Comuns
- `pretty=true` - Formata JSON
- `select` - Seleciona campos específicos
- `limit` - Pagina resultados
- `offset` - Deslocamento
- `sort` - Ordena resultados
- `search` - Busca texto

---

## 🐳 MÓDULO KUBERNETES & HELM

### Documentação Oficial
- **Kubernetes Deployment**: https://documentation.wazuh.com/current/deployment-options/docker/kubernetes/index.html
- **Helm Deployment**: https://documentation.wazuh.com/current/deployment-options/docker/kubernetes/wazuh-helm-chart.html
- **Helm Chart (Oficial)**: https://github.com/wazuh/wazuh-kubernetes
- **Helm Chart (Comunidade)**: https://github.com/kajov/wazuh-kubernetes-helmchart

### Opções de Deployment

#### 1. Helm Chart Oficial
```bash
# Adicionar repo
helm repo add wazuh https://wazuh.github.io/wazuh-helm-chart

# Instalar
helm install wazuh wazuh/wazuh

# Atualizar
helm upgrade wazuh wazuh/wazuh
```

#### 2. Helm Chart Comunitário (kajov)
```bash
# Clone repository
git clone https://github.com/kajov/wazuh-kubernetes-helmchart.git
cd wazuh-kubernetes-helmchart/wazuh-kubernetes

# Test
./scripts/test.sh

# Deploy
./scripts/deploy.sh

# Remove
./scripts/remove.sh
```

### Estrutura de Componentes Kubernetes

#### Deployments
- **Kibana**: UI Dashboard
- **Wazuh Dashboard**: UI alternativa

#### StatefulSets
- **Elasticsearch**: Indexação (3 réplicas)
- **Wazuh Manager Master**: Manager principal
- **Wazuh Manager Workers**: Managers adicionais

#### DaemonSets
- **Wazuh Agent**: Agent em cada nó

#### ConfigMaps
- `elasticsearch.yml` - Config Elasticsearch
- `wazuh-master.yaml` - Config Manager Master
- `wazuh-workers.yaml` - Config Manager Workers
- `wazuh-agent.yaml` - Config Agent

#### Secrets
- `elastic-cred` - Credenciais Elasticsearch
- `kibana-certs` - Certificados Kibana
- `odfe-ssl-certs` - SSL certificates
- `wazuh-api-cred` - Credenciais API
- `wazuh-authd-pass` - Password agent auth
- `wazuh-cluster-key` - Cluster key

### Services
- **Elasticsearch**: ClusterIP + LoadBalancer
- **Kibana**: LoadBalancer
- **Wazuh Manager**: ClusterIP para agents
- **Wazuh Cluster**: Inter-manager communication

### Storage
- PersistentVolumes para Elasticsearch
- PersistentVolumes para Manager data
- ConfigMaps para configurações

### Exemplo values.yaml
```yaml
elasticsearch:
  replicas: 3
  storage: 30Gi
  
kibana:
  replicas: 1
  
wazuh:
  manager:
    replicas: 1
    storage: 10Gi
  agent:
    enabled: true
  
image:
  repository: wazuh.azurecr.io/wazuh
  tag: 4.7.0
```

### Troubleshooting Kubernetes
- Verificar pods: `kubectl get pods -n wazuh`
- Logs: `kubectl logs -n wazuh <pod-name>`
- Describe pod: `kubectl describe pod -n wazuh <pod-name>`
- Port forward: `kubectl port-forward -n wazuh svc/kibana 5601:5601`

---

## ⚙️ MÓDULO SCA (SECURITY CONFIGURATION ASSESSMENT)

### Documentação Oficial
- **SCA Capabilities**: https://documentation.wazuh.com/current/user-manual/capabilities/configuration-assessment/index.html
- **SCA Configuration**: https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/sca.html
- **SCA Use Cases**: https://documentation.wazuh.com/current/use-cases/configuration-assessment.html

### Como Funciona SCA

#### Processo
1. **Policy Definition**: Arquivos YAML com rules de verificação
2. **Scanning**: Scans periódicos ou sob demanda
3. **Policy Evaluation**: Verifica contra regras
4. **Reporting**: Gera relatórios detalhados

#### Benchmarks Disponíveis
- **CIS Benchmarks**: Industry standard
- **PCI DSS**: Payment Card Industry
- **HIPAA**: Health Insurance Portability
- **NIST 800-53**: Federal security standards
- **Custom**: Policies customizadas

### Arquivos de Política SCA

#### Localização
- Linux/Mac: `/var/ossec/ruleset/sca/`
- Windows: `C:\Program Files (x86)\ossec-agent\ruleset\sca\`

#### Exemplos
- `cis_ubuntu_linux_22.04_l1.yml`
- `cis_debian_linux_12_l1.yml`
- `cis_rhel_linux_9_l1.yml`
- `cis_windows_11_enterprise_l1.yml`

### Estrutura YAML Policy
```yaml
policy:
  id: "cis_ubuntu_linux_22.04"
  file: "cis_ubuntu_linux_22.04_l1.yml"
  name: "CIS Ubuntu Linux 22.04 L1"
  description: "CIS Benchmarks"
  
checks:
  - id: 6700
    title: "Ensure permissions on /etc/ssh/sshd_config are configured"
    compliance:
      - cis_level1
      - pci_dss_2_2_4
    type: file
    file: /etc/ssh/sshd_config
    file_type: regular
    mode:
      value: "0600"
    
  - id: 6701
    title: "Ensure SSH PermitRootLogin is disabled"
    type: file
    file: /etc/ssh/sshd_config
    regex: "^PermitRootLogin"
    not_regex_match_output: "^PermitRootLogin\\s+no$"
```

### Configuração SCA no Agent
```xml
<sca>
  <enabled>yes</enabled>
  <scan_on_start>yes</scan_on_start>
  <interval>24h</interval>
  <skip_nfs>yes</skip_nfs>
  <policy path="/var/ossec/ruleset/sca/cis_ubuntu_linux_22.04_l1.yml" />
</sca>
```

### Dashboard SCA
- **Compliance Overview**: Visão geral de compliance
- **Policy Details**: Detalhes de cada política
- **Failed Checks**: Verificações falhadas
- **Remediation**: Instruções de correção

### Conformidade Regulatória
- PCI DSS: Compliance validation
- HIPAA: Healthcare standards
- NIST 800-53: Federal requirements
- SOC 2: Service organization controls
- ISO 27001: Information security

---

## 🔓 MÓDULO VULNERABILITY DETECTION

### Documentação Oficial
- **Vulnerability Detection**: https://documentation.wazuh.com/current/user-manual/capabilities/vulnerability-detection/index.html
- **Configuration**: https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/vulnerability-detection.html

### Como Funciona

#### Integração com Syscollector
1. Syscollector coleta software inventário
2. Compara contra base de vulnerabilidades
3. Gera alertas para software vulnerável

#### Bancos de Vulnerabilidades
- NVD (National Vulnerability Database)
- Ubuntu Security Notices
- Debian Security
- Red Hat Advisories
- Windows Update

### Configuração
```xml
<vulnerability-detection>
  <enabled>yes</enabled>
  <index-status>yes</index-status>
  <feed-update-interval>60m</feed-update-interval>
</vulnerability-detection>
```

### Dashboard
- **Vulnerable Packages**: Pacotes vulneráveis
- **CVSS Scores**: Severidade das vulnerabilidades
- **Remediation**: Patches disponíveis

### Compliance Mapping
- CVE References
- CVSS Scoring
- Patch availability
- Update recommendations

---

## 🎯 CDB LISTS & THREAT INTELLIGENCE

### Documentação Oficial
- **CDB Lists Documentation**: https://documentation.wazuh.com/current/user-manual/ruleset/cdb-list.html
- **Threat Intelligence**: https://documentation.wazuh.com/current/user-manual/capabilities/malware-detection/cdb-lists.html

### O que são CDB Lists

#### Funcionalidade
- Key-value pairs store
- Rapid lookups
- File hashes, IPs, domains
- Malware signatures
- Allow/deny lists

### Formato CDB List

#### Exemplo: Malware Hashes
```
3a7ea5d39ef1dd2551f1c7f9aeaf54e9:malware
7b2e8f4a9c6d1b3e5f2a8c4d7e9b1f3a:trojan
...
```

#### Exemplo: IP Blocklist
```
192.168.1.100:malicious_ip
10.0.0.50:botnet_ip
...
```

### Criar CDB List

#### 1. Arquivo de texto
```bash
cat > /var/ossec/etc/lists/malware-hashes << EOF
3a7ea5d39ef1dd2551f1c7f9aeaf54e9:malware
7b2e8f4a9c6d1b3e5f2a8c4d7e9b1f3a:trojan
EOF
```

#### 2. Compilar em formato CDB
```bash
/var/ossec/bin/wazuh-cdb-maker.py -i /var/ossec/etc/lists/malware-hashes \
  -o /var/ossec/etc/lists/malware-hashes.cdb
```

#### 3. Registrar em ossec.conf
```xml
<ruleset>
  <cdb_list>/var/ossec/etc/lists/malware-hashes</cdb_list>
  <cdb_list>/var/ossec/etc/lists/ip-blocklist</cdb_list>
</ruleset>
```

### Usar em Rules
```xml
<group name="malware,">
  <rule id="110002" level="13">
    <if_sid>554, 550</if_sid>
    <list field="md5" lookup="match_key">etc/lists/malware-hashes</list>
    <description>File with known malware hash detected: $(file)</description>
  </rule>
</group>
```

### Integração FIM + CDB Lists

Workflow:
1. FIM detecta nova/modificada file
2. Calcula MD5/SHA256
3. Compara contra CDB list
4. Match = Alert em nível 13

### Fontes de Threat Intelligence
- AlienVault OTX
- VirusTotal
- Abuse.ch
- Phishtank
- Custom feeds

---

## 🏗️ STACK TECNOLÓGICO

### Backend & Core
| Componente | Tecnologia | Função |
|-----------|-----------|--------|
| **Manager Core** | C/C++ | Processamento central |
| **Agent Core** | C/C++ | Coleta em endpoints |
| **Scripting** | Python, Shell/Bash | Automação e scripts |
| **API Backend** | Node.js | RESTful API |

### Indexação & Busca
| Componente | Versão | Função |
|-----------|--------|--------|
| **Elasticsearch** | 7.10+ | Indexação de logs (padrão) |
| **OpenSearch** | 1.0+ | Alternativa ao Elasticsearch |
| **Wazuh Indexer** | 4.3+ | Indexer proprietário |

### Visualização & Dashboard
| Componente | Versão | Função |
|-----------|--------|--------|
| **Kibana** | 7.10+ | Visualizações (integração legada) |
| **Wazuh Dashboard** | 2.0+ | UI proprietária moderna |
| **React** | 16.8+ | Framework UI |

### Processamento de Logs
| Componente | Versão | Função |
|-----------|--------|--------|
| **Filebeat** | 7.10+ | Log shipper |
| **Logstash** | 7.10+ | Log processing (opcional) |

### Container & Orquestração
| Componente | Versão | Função |
|-----------|--------|--------|
| **Docker** | 20.0+ | Containerização |
| **Docker Compose** | 1.29+ | Multi-container |
| **Kubernetes** | 1.14+ | Orquestração |
| **Helm** | 2.16+ / 3.0+ | Package manager K8s |

### Protocolos & Comunicação
| Protocolo | Uso |
|----------|-----|
| **HTTPS/TLS** | Segurança |
| **TCP/1514** | Agent-Manager |
| **UDP/514** | Syslog (opcional) |
| **REST API** | Management |
| **WebSocket** | Dashboard |

---

## ⚠️ ISSUES CONHECIDAS & SOLUÇÕES

### 1. Problemas de Indexação Elasticsearch

#### Problema: Red/Yellow Status
```
Problem: Elasticsearch indices showing red status
Symptoms: Data not indexed, searches failing
```

**Causa**: Shards não alocados, problemas de quorum

**Solução**:
```bash
# Verificar status
curl -X GET "localhost:9200/_cluster/health?pretty"

# Rebalancear shards
curl -X PUT "localhost:9200/_settings" -H 'Content-Type: application/json' \
  -d '{"index.unassigned.node_allocation.enabled": "all"}'

# Reiniciar Elasticsearch
systemctl restart elasticsearch
```

**Referência**: https://github.com/wazuh/wazuh-kibana-app/issues/1016

### 2. GitHub Integration Issues

#### Problema: GitHub Integration retorna erro 404
```
Problem: Não consegue coletar dados do GitHub
Error: 404 Not Found
```

**Causa**: 
- Requer GitHub Enterprise Cloud
- Escopos incorretos (precisa `audit_log` e `admin:org`)
- Token sem permissões adequadas

**Solução**:
1. Usar GitHub Enterprise Cloud (não Free tier)
2. Criar PAT com escopos:
   - `admin:org` - Organization read
   - `read:audit_log` - Audit log read
3. Testar token: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`

**Referência**: https://github.com/wazuh/wazuh/issues/14964

### 3. Agent Connection Issues

#### Problema: Agent não conecta no Manager
```
Problem: Agent stuck in "Never connected" status
```

**Causa**: Firewall, DNS, permissões, certificados

**Solução**:
```bash
# Testar conectividade
telnet wazuh-manager 1514

# Verificar DNS
nslookup wazuh-manager

# Reiniciar agent
systemctl restart wazuh-agent

# Verificar logs agent
tail -f /var/ossec/logs/active-responses.log
```

### 4. API Authentication Failures

#### Problema: JWT Token expirado ou inválido
```
Error: Invalid token or expired
```

**Solução**:
```bash
# Gerar novo token
curl -k -X POST "https://localhost:55000/security/user/authenticate" \
  -H "Authorization: Basic $(echo -n 'wazuh:wazuh' | base64)" \
  -H "Content-Type: application/json"

# Usar token recém-gerado
export TOKEN="<novo_token>"
```

### 5. Performance & Memory Issues

#### Problema: Manager/Elasticsearch usando muita memória
```
Symptom: OOMKilled pods, sluggish performance
```

**Solução**:
1. **Elasticsearch heap**: Aumentar `ES_JAVA_OPTS="-Xms2g -Xmx2g"`
2. **Index rotation**: Configurar daily/weekly rollover
3. **Rebalance shards**: Distribuir entre nodes
4. **Disable unnecessary modules**: Desabilitar módulos não usados

```xml
<disabled-module name="vulnerability-detection"/>
<disabled-module name="aws-cloudtrail"/>
```

### 6. Kubernetes Deployment Issues

#### Problema: Pods não iniciam
```
Status: CrashLoopBackOff ou Pending
```

**Debug**:
```bash
# Ver logs
kubectl logs -f wazuh-manager-0 -n wazuh

# Ver eventos
kubectl describe pod wazuh-manager-0 -n wazuh

# Verificar recursos
kubectl top pod -n wazuh

# Verificar PVC
kubectl get pvc -n wazuh
```

### 7. Certificate Issues

#### Problema: SSL certificate errors
```
Error: self signed certificate in certificate chain
```

**Solução**:
```bash
# Regenerar certificados
/var/ossec/bin/wazuh-certs-tool.sh -a

# Copiar para agentes
scp /var/ossec/etc/ssl/certs/* agent:/var/ossec/etc/ssl/certs/

# Reiniciar serviços
systemctl restart wazuh-manager
systemctl restart wazuh-agent
```

### 8. Syslog Ingestion Issues

#### Problema: Eventos Syslog não aparecem
```
Problem: Syslog data not indexed
```

**Verificar**:
1. Port 514 aberta
2. Firewall rules
3. Syslog remoto configurado em ossec.conf
4. Logs em `/var/ossec/logs/alerts.log`

---

## 📦 INSTALAÇÃO DE AGENTS

### Linux - Ubuntu/Debian

#### Via Repository
```bash
# Adicionar repository
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -
echo "deb https://packages.wazuh.com/4.x/apt/ stable main" > /etc/apt/sources.list.d/wazuh.list

# Instalar
apt-get update
apt-get install -y wazuh-agent

# Iniciar
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent
```

#### Via Script Manual
```bash
# Download
wget https://packages.wazuh.com/4.7.4/wazuh-agent-4.7.4-1.linux.x86_64.tar.gz

# Extract
tar -xzf wazuh-agent-4.7.4-1.linux.x86_64.tar.gz

# Install
cd wazuh-agent-4.7.4
./install.sh

# Register
/var/ossec/bin/wazuh-control start
```

### Windows - PowerShell

#### Via MSI Installer
```powershell
# Download
$uri = "https://packages.wazuh.com/4.7.4/windows/wazuh-agent-4.7.4-1.msi"
Invoke-WebRequest -Uri $uri -OutFile wazuh-agent.msi

# Install com Manager configurado
msiexec.exe /i wazuh-agent.msi /q WAZUH_MANAGER="192.168.1.100" WAZUH_REGISTRATION_SERVER="192.168.1.100"

# Start service
Start-Service WazuhSvc
```

#### Via CMD
```cmd
wazuh-agent-4.7.4-1.msi /q WAZUH_MANAGER="192.168.1.100"
NET START WazuhSvc
```

### macOS - Homebrew

```bash
# Install
brew install wazuh-agent

# Configure
sudo defaults write /Library/Preferences/com.wazuh.agent MANAGER_IP 192.168.1.100

# Start
sudo launchctl start com.wazuh.agent
```

### Docker

```bash
# Pull image
docker pull wazuh/wazuh-agent:latest

# Run
docker run -d \
  --name wazuh-agent \
  -e WAZUH_MANAGER="192.168.1.100" \
  -e WAZUH_AGENT_NAME="docker-agent" \
  wazuh/wazuh-agent:latest
```

### Ansible Playbook

```yaml
---
- hosts: wazuh-agents
  become: yes
  roles:
    - role: wazuh-ansible/roles/wazuh-agent
  vars:
    wazuh_managers:
      - address: 192.168.1.100
        port: 1514
        protocol: tcp
        api_port: 55000
        api_proto: https
        api_user: wazuh
```

### Configuração Agent Avançada

```xml
<agent_config>
  <!-- FIM -->
  <syscheck>
    <disabled>no</disabled>
    <directories check_all="yes" realtime="yes">/etc</directories>
  </syscheck>
  
  <!-- SCA -->
  <sca>
    <enabled>yes</enabled>
    <scan_on_start>yes</scan_on_start>
  </sca>
  
  <!-- Log collection -->
  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/auth.log</location>
  </localfile>
  
  <!-- Command monitoring -->
  <command>
    <frequency>3600</frequency>
    <run_on_start>yes</run_on_start>
    <bin_name>netstat</bin_name>
    <arg>-tulpn</arg>
  </command>
</agent_config>
```

---

## 🔧 TROUBLESHOOTING

### Manager Issues

#### Manager não inicia
```bash
# Verificar logs
tail -f /var/ossec/logs/ossec.log

# Verificar configuração
/var/ossec/bin/wazuh-control validate-config

# Reiniciar
/var/ossec/bin/wazuh-control restart
```

#### Cluster issues
```bash
# Verificar status cluster
curl -s http://localhost:55000/cluster/status?pretty=true \
  -H "Authorization: Bearer $TOKEN"

# Ver nós
curl -s http://localhost:55000/cluster/nodes?pretty=true \
  -H "Authorization: Bearer $TOKEN"
```

### Agent Issues

#### Agent não reporta dados
```bash
# Verificar status
/var/ossec/bin/wazuh-control status

# Verificar conexão
netstat -tulpn | grep ossec

# Verificar logs
tail -f /var/ossec/logs/active-responses.log
```

#### Duplicate agent ID
```bash
# Remover agent duplicado via API
curl -X DELETE "https://localhost:55000/agents/12345" \
  -H "Authorization: Bearer $TOKEN"

# Ou via agent registration
/var/ossec/bin/agent-auth -m 192.168.1.100
```

### Dashboard Issues

#### Kibana/Dashboard não acessível
```bash
# Verificar status
curl -s http://localhost:5601/api/status | jq '.status.overall.state'

# Limpar cache
curl -X DELETE http://localhost:5601/api/opensearch_dashboards/management/saved_objects/index-pattern/*

# Reiniciar
systemctl restart wazuh-dashboard
```

#### Índices não aparecem
```bash
# Criar índice manualmente
curl -X POST "localhost:9200/.wazuh-4.x-alerts-*/_doc" \
  -H 'Content-Type: application/json' -d '{}'

# Refresh índice
curl -X POST "localhost:9200/.wazuh-4.x-alerts-*/_refresh"
```

---

## 📊 RESUMO DE FONTES PARA RAG

### URLs Consolidadas
```json
{
  "official_docs": "https://documentation.wazuh.com",
  "github_main": "https://github.com/wazuh/wazuh",
  "github_api": "https://github.com/wazuh/wazuh-api",
  "github_kubernetes": "https://github.com/wazuh/wazuh-kubernetes",
  "api_docs": "https://documentation.wazuh.com/current/api/index.html",
  "fim_docs": "https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html",
  "sca_docs": "https://documentation.wazuh.com/current/user-manual/capabilities/configuration-assessment/index.html",
  "community": "https://wazuh.com/community/"
}
```

### Tecnologias Core
- **Backend**: C/C++ (core), Python, Node.js
- **Search**: Elasticsearch/OpenSearch
- **UI**: React, Kibana
- **Container**: Docker, Kubernetes, Helm
- **Protocols**: REST API, HTTPS, Syslog

### Módulos Principais
1. **FIM** - File Integrity Monitoring
2. **API** - RESTful Management
3. **SCA** - Security Configuration Assessment
4. **Vulnerability Detection** - CVE Detection
5. **CDB Lists** - Threat Intelligence
6. **Kubernetes** - Container Orchestration

### Compliance Support
- PCI DSS, HIPAA, NIST 800-53, GDPR, ISO 27001

---

**Última atualização**: 2025-11-18
**Versão Wazuh documentada**: 4.7.4
**Status**: Completo e pronto para RAG

