# ADR-012: Completão SMS Core Unified - Processo e Decisões

> **Data:** 2025-11-19
> **Status:** ✅ Aceito e Implementado
> **Tipo:** Process Decision / Implementation Pattern

---

## Contexto

O módulo `sms_core_unified` foi criado durante refatoração mas ficou incompleto (~30% implementado). Arquivos unificados estavam na raiz do projeto ao invés de estarem no módulo. Era necessário completar o módulo deixando-o 100% funcional.

---

## Decisão

Completar o módulo `sms_core_unified` movendo todos os arquivos da raiz para o módulo, criando arquivos faltantes e organizando tudo seguindo padrões Odoo.

---

## Decisões Técnicas

### DT-1: Estrutura de Arquivos

**Decisão:** Manter estrutura padrão Odoo:
```
sms_core_unified/
├── models/
├── security/
├── views/
└── data/
```

**Alternativas consideradas:**
- Manter arquivos na raiz (rejeitado - não segue padrão)
- Criar subpastas adicionais (rejeitado - desnecessário)

**Justificativa:** Seguir padrão Odoo facilita manutenção e upgrades futuros.

---

### DT-2: Processo de Cópia

**Decisão:** Usar processo em 2 etapas:
1. Copiar para `/tmp` no servidor
2. Mover para local correto com `sudo`

**Alternativas consideradas:**
- Copiar diretamente (rejeitado - problemas de permissão)
- Usar rsync (rejeitado - mais complexo)

**Justificativa:** Processo simples, confiável e fácil de debugar.

---

### DT-3: Permissões de Arquivos

**Decisão:** Sempre usar `chown odoo:odoo` e `chmod 644`

**Justificativa:** Padrão Odoo garante que o servidor possa ler os arquivos.

---

### DT-4: ir.model.access.csv

**Decisão:** Criar CSV com permissões básicas:
- Usuários: leitura/escrita em models principais
- Admin: acesso total a providers

**Justificativa:** CSV é padrão Odoo e mais fácil de manter que XML.

---

### DT-5: Ordem no Manifest

**Decisão:** Seguir ordem:
1. Security (CSV primeiro)
2. Views
3. Menus
4. Data

**Justificativa:** Odoo carrega na ordem listada. Security deve vir antes.

---

## Consequências

### Positivas
- ✅ Módulo 100% funcional
- ✅ Estrutura organizada
- ✅ Segue padrões Odoo
- ✅ Fácil manutenção futura
- ✅ Processo documentado e reutilizável

### Negativas
- ⚠️ Requer reinstalação do módulo (se já estava instalado)
- ⚠️ Pode precisar migração de dados (se houver)

### Neutras
- Arquivos da raiz podem ser removidos (não são mais necessários)

---

## Alternativas Rejeitadas

### AR-1: Manter Arquivos na Raiz
**Rejeitado porque:** Não segue padrão Odoo, dificulta manutenção.

### AR-2: Criar Script de Migração Automática
**Rejeitado porque:** Processo manual é mais seguro e permite validação em cada etapa.

### AR-3: Usar Symlinks
**Rejeitado porque:** Pode causar problemas em diferentes ambientes.

---

## Validação

### Critérios de Sucesso
- [x] Todos os models implementados
- [x] Security completo
- [x] Views completas
- [x] Manifest atualizado
- [x] Estrutura validada
- [x] Módulo pode ser instalado

### Métricas
- **Antes:** ~30% completo
- **Depois:** 100% completo ✅
- **Tempo:** ~25 minutos
- **Arquivos movidos:** 7
- **Arquivos criados:** 2
- **Arquivos atualizados:** 3

---

## Aprendizados

1. **Sempre verificar estrutura antes de começar**
2. **Processo em etapas é mais seguro que tudo de uma vez**
3. **Validação após cada etapa evita problemas acumulados**
4. **Documentação durante o processo é essencial**

---

## Referências

- `.cursor/memory/learnings/SMS-CORE-UNIFIED-COMPLETION-AI-FIRST.md`
- `PLANO-MIGRACAO-SMS-UNIFIED.md`
- `SMS-CORE-UNIFIED-PROGRESSO.md`

---

**Status:** ✅ Implementado
**Próxima revisão:** Quando necessário completar outro módulo

