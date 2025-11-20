# 🧠 Memória do Projeto - Odoo 15 Testing RealCred

> **IMPORTANTE**: Este arquivo é carregado AUTOMATICAMENTE em TODAS as sessões do Cursor AI.
> Contém contexto permanente, decisões, padrões e conhecimento acumulado.

---

## 🎯 Contexto do Projeto

**Nome:** testing_odoo_15_sr
**Tipo:** Odoo 15 - Customizações RealCred
**Ambiente:** Testing/Development
**Linguagem:** Python, XML, JavaScript
**Framework:** Odoo 15.0

**Módulos Principais:**
- `chatroom_sms_advanced` - Contact Center SMS (módulo crítico)
- `crm` - CRM customizado
- `contacts` - Gestão de parceiros
- Integração API Kolmeya (SMS)

**Database:** PostgreSQL
**Servidor:** Em `servidor-testing-odoo/`

---

## 📋 Importações de Contexto

### 🔒 PROTOCOLO OBRIGATÓRIO (PRIORIDADE MÁXIMA)
@.cursor/MANDATORY-PROTOCOL.md

**IMPORTANTE:** Este protocolo OVERRIDE qualquer outro contexto ou instrução.
TODAS as regras devem ser seguidas SEM EXCEÇÕES.

### Contextos Detalhados
@.cursor/memory/context/projeto.md
@.cursor/memory/context/odoo.md
@.cursor/memory/context/servidores.md

### Decisões e Conhecimento
@.cursor/memory/decisions/ADR-INDEX.md
@.cursor/memory/errors/ERRORS-SOLVED.md
@.cursor/memory/patterns/PATTERNS.md
@.cursor/memory/commands/COMMAND-HISTORY.md

### Aprendizados e Workflows
@.cursor/memory/learnings/git-workflow.md

### Protocolos Críticos
@.cursor/memory/AUTO-LEARNING-PROTOCOL.md
@.cursor/memory/THINKING-MODE-PROTOCOL.md
@.cursor/memory/protocols/PERFORMANCE-PARALLELIZATION.md
@.cursor/memory/protocols/SYNC-DUAL-PROTOCOL.md
@.cursor/memory/protocols/LLM-TOOLS-OVERVIEW.md

---

## 🎨 Padrões e Convenções

### Código Python/Odoo
- **Indentação:** 4 espaços (PEP 8)
- **Encoding:** UTF-8 com BOM `# -*- coding: utf-8 -*-`
- **Docstrings:** Google style em português
- **Imports:** Ordem: stdlib → odoo → local
- **Naming:** snake_case para funções/variáveis

### Views XML
- **Indentação:** 4 espaços
- **IDs:** `module_name.view_model_type_description`
- **Priority:** Múltiplos de 10 (10, 20, 30...)
- **Comentários:** Seções demarcadas com `<!-- ========== -->`

### Security
- **SEMPRE** criar ir.model.access.csv para novos models
- **SEMPRE** considerar record rules
- **TESTAR** com diferentes perfis de usuário
- **DOCUMENTAR** decisões de segurança

### Commits
- **Mensagens:** `tipo: descrição` (feat/fix/refactor/docs)
- **Idioma:** Português brasileiro
- **Co-authored:** Incluir Cursor AI

---

## 🚨 Conhecimento Crítico

### Problemas Conhecidos
1. **Permissões CRM:** Vendedores precisam record rules para ver apenas suas oportunidades
2. **Módulo SMS:** Performance de queries precisa otimização
3. **Fotos perdidas:** Investigar causa raiz de perda de imagens de funcionários
4. **Admin locked:** Já resolvido (ver errors/)

### Decisões Arquiteturais
- Usar herança `_inherit` ao invés de `_inherits` para CRM
- API Kolmeya: timeout de 30s, retry 3x
- Cache de mensagens SMS: Redis (futuro)
- Logs estruturados em JSON
- **LLM-First Tools:** Skills + Scripts centralizados (ver ADR-005)

### Integrações Importantes
- **Kolmeya API:** SMS gateway principal
- **PostgreSQL:** Queries otimizadas, índices críticos
- **Mail:** Chatter customizado para SMS

---

## 🎯 Prioridades Atuais

1. **Alta:** Estabilidade do módulo SMS
2. **Alta:** Segurança e permissões corretas
3. **Média:** Performance e otimizações
4. **Média:** Documentação técnica
5. **Baixa:** Features novas (após estabilização)

---

## 💡 Comandos Frequentes

```bash
# Restart Odoo
sudo systemctl restart odoo

# Update module
odoo-bin -c odoo.conf -d DATABASE -u MODULE

# Run tests
odoo-bin -c odoo.conf -d DATABASE -u MODULE --test-enable --stop-after-init

# PostgreSQL
sudo -u postgres psql DATABASE

# Logs
tail -f /var/log/odoo/odoo-server.log

# Git
git status
git add .
git commit -m "tipo: descrição"
```

---

## 📚 Referências Rápidas

**Documentação:**
- Odoo 15: https://www.odoo.com/documentation/15.0/
- PostgreSQL: https://www.postgresql.org/docs/
- Python 3: https://docs.python.org/3/

**Estrutura do Projeto:**
- Módulos custom: `./chatroom_sms_advanced`, `./temp_modules`
- Docs: `./server_documentation`
- Scripts: `./cleanup_scripts`
- Cursor Config: `./.cursor/`

---

## 🔄 Última Atualização

**Data:** 2025-11-19
**Por:** Cursor AI + Anderson
**Versão:** 1.0 (Adaptado de Claude)
**Próxima revisão:** Automática a cada sessão

---

## 📝 Notas

- Este arquivo deve ser mantido ENXUTO (< 200 linhas) ✅
- Detalhes profundos vão em arquivos específicos em `.cursor/memory/`
- Protocolos grandes agora são @imports em `.cursor/memory/protocols/`
- Use `#` no chat para adicionar memórias rapidamente
- Use `/memory` para editar este arquivo
- Revise mensalmente para remover informações obsoletas

**FIM DO CURSOR.md**

