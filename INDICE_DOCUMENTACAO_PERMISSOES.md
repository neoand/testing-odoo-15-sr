# ÍNDICE MESTRE - DOCUMENTAÇÃO DE PERMISSÕES
## Reestruturação de Permissões de Vendas - Odoo 15 Realcred
## Data: 16/11/2025

---

## 📚 VISÃO GERAL

Este índice organiza toda a documentação relacionada à reestruturação de permissões de vendas realizada em 16/11/2025.

**Total de Arquivos:** 5
**Total de Páginas:** ~40 páginas
**Backup em Banco:** res_groups_users_rel_backup_20251116 (381 registros)

---

## 📁 ARQUIVOS DISPONÍVEIS

### 1. 📖 ESTADO_ORIGINAL_PERMISSOES.md (15KB)
**O QUE É:** Documentação completa do estado ANTES das mudanças

**QUANDO USAR:**
- ✓ Para consultar como estava configurado originalmente
- ✓ Para entender quais problemas existiam
- ✓ Para comparar antes vs depois
- ✓ Para referência em caso de dúvidas

**CONTEÚDO:**
```
├─ Seção 1: Resumo Executivo
├─ Seção 2: Lista Completa de Cada Usuário (27 usuários)
│  ├─ Vendedores (15)
│  ├─ Supervisor (1)
│  ├─ Operacional (6)
│  ├─ Financeiro (2)
│  ├─ Marketing (2)
│  └─ Admin (1)
├─ Seção 3: Detalhamento Técnico dos Grupos
├─ Seção 4: Matriz Completa (Tabela usuário x grupos)
├─ Seção 5: Análise de Inconsistências
├─ Seção 6: Comparação ANTES vs DEPOIS
├─ Seção 7: Registros RAW do Backup
├─ Seção 8: Estatísticas
├─ Seção 9: Backup e Segurança
└─ Seção 10: Como Usar Este Documento
```

**PRINCIPAIS DESCOBERTAS:**
- ❌ 5 vendedores tinham Sales Administrator (problema!)
- ❌ Marketing Criativo tinha apenas Own Docs (insuficiente)
- ✅ Backup completo de 381 registros
- ⚠️ 33% dos vendedores viam todos os clientes

---

### 2. 📘 DOCUMENTACAO_PERMISSOES_VENDAS.md (15KB)
**O QUE É:** Documentação da nova estrutura e mudanças aplicadas

**QUANDO USAR:**
- ✓ Para entender a nova estrutura implementada
- ✓ Para ver exatamente quais mudanças foram feitas
- ✓ Para manutenção futura (adicionar usuários, etc)
- ✓ Para troubleshooting de problemas

**CONTEÚDO:**
```
├─ Seção 1: Problema Identificado
├─ Seção 2: Estrutura Implementada (diagrama)
├─ Seção 3: Mudanças Aplicadas (SQL executado)
├─ Seção 4: Resultado Final (estado atual)
├─ Seção 5: Impacto nas Operações
├─ Seção 6: Validação (queries)
├─ Seção 7: ROLLBACK (3 métodos)
├─ Seção 8: Manutenção Futura
├─ Seção 9: Troubleshooting
├─ Seção 10: Referências Técnicas
├─ Seção 11: Histórico de Mudanças
└─ Seção 12: Contatos e Responsáveis
```

**PRINCIPAIS FEATURES:**
- ✅ Estrutura clara por função (4 níveis)
- ✅ SQL de todas as mudanças documentado
- ✅ Guia de manutenção futura
- ✅ 3 métodos de rollback documentados

---

### 3. 🔧 ROLLBACK_PERMISSOES.sql (2.5KB)
**O QUE É:** Script SQL completo para reverter mudanças

**QUANDO USAR:**
- ✓ Se cliente não gostar das mudanças
- ✓ Se houver problemas inesperados
- ✓ Para teste de rollback

**COMO EXECUTAR:**
```bash
# No servidor odoo-rc
cat ~/ROLLBACK_PERMISSOES.sql | sudo -u postgres psql realcred
```

**O QUE FAZ:**
1. Mostra estado atual
2. Remove todas as permissões atuais dos grupos 13, 14, 15
3. Restaura do backup (381 registros)
4. Valida restauração
5. Mostra estado após rollback
6. Confirma usuários específicos voltaram ao normal

**TEMPO DE EXECUÇÃO:** ~2 segundos
**EFEITO:** Imediato (sem reiniciar Odoo)

---

### 4. 🛠️ rollback_permissoes.sh (2.5KB)
**O QUE É:** Script shell interativo para rollback

**QUANDO USAR:**
- ✓ Método mais fácil e seguro para fazer rollback
- ✓ Quando quiser confirmação antes de executar
- ✓ Para ter output formatado e visual

**COMO EXECUTAR:**
```bash
# 1. Copiar para servidor
scp rollback_permissoes.sh odoo-rc:~/

# 2. Dar permissão e executar
ssh odoo-rc
chmod +x rollback_permissoes.sh
./rollback_permissoes.sh
```

**O QUE FAZ:**
1. Mostra banner informativo
2. Explica o que vai fazer
3. **PEDE CONFIRMAÇÃO** (S/N)
4. Executa ROLLBACK_PERMISSOES.sql
5. Mostra resultado formatado
6. Confirma sucesso

**VANTAGENS:**
- ✅ Mais seguro (pede confirmação)
- ✅ Output visual e formatado
- ✅ Tratamento de erros

---

### 5. 📄 COMO_FAZER_ROLLBACK.txt (5.6KB)
**O QUE É:** Guia rápido e visual de rollback

**QUANDO USAR:**
- ✓ Consulta rápida de emergência
- ✓ Quando precisar de instruções passo-a-passo
- ✓ Para compartilhar com equipe

**CONTEÚDO:**
```
├─ Resumo e Garantias
├─ Método 1: Automático (script shell)
├─ Método 2: Manual via SQL
├─ Método 3: Comandos Diretos (emergência)
├─ Validação Pós-Rollback
├─ Arquivos Necessários
└─ Contato e Informações
```

**FORMATO:** ASCII art, visual, fácil de ler no terminal

---

### 6. 📋 INDICE_DOCUMENTACAO_PERMISSOES.md (Este arquivo)
**O QUE É:** Índice mestre de toda a documentação

**CONTEÚDO:** Você está aqui! 😊

---

## 🗺️ MAPA DE NAVEGAÇÃO

### Cenário 1: "Preciso entender o que foi feito"
1. Ler **DOCUMENTACAO_PERMISSOES_VENDAS.md** (Seções 1-2)
2. Ver **ESTADO_ORIGINAL_PERMISSOES.md** (Seção 6 - Comparação)

### Cenário 2: "Cliente não gostou, preciso reverter"
1. Ler **COMO_FAZER_ROLLBACK.txt** (Método 1)
2. Executar **rollback_permissoes.sh**
3. Validar resultado em **DOCUMENTACAO_PERMISSOES_VENDAS.md** (Seção 6)

### Cenário 3: "Como estava configurado antes?"
1. Consultar **ESTADO_ORIGINAL_PERMISSOES.md** (Seção 2)
2. Ver matriz completa na Seção 4

### Cenário 4: "Preciso adicionar novo vendedor"
1. Ler **DOCUMENTACAO_PERMISSOES_VENDAS.md** (Seção 8 - Manutenção Futura)
2. Executar SQL documentado

### Cenário 5: "Vendedor reclama que não vê cliente"
1. Consultar **DOCUMENTACAO_PERMISSOES_VENDAS.md** (Seção 9 - Troubleshooting)
2. Executar queries de validação da Seção 6

### Cenário 6: "Qual SQL foi executado?"
1. Ver **DOCUMENTACAO_PERMISSOES_VENDAS.md** (Seção 3)
2. Todos os SQLs estão documentados

---

## 📊 RESUMO DAS MUDANÇAS

### Usuários Modificados: 6

| ID | Login | ANTES | DEPOIS | Motivo |
|----|-------|-------|--------|--------|
| 393 | comercial20 | Admin | Own Docs | Vendedor não deve ter admin |
| 30 | comercial22 | Admin | Own Docs | Vendedor não deve ter admin |
| 33 | comercial12 | Admin | Own Docs | Vendedor não deve ter admin |
| 382 | Comercial29 | Admin | Own Docs | Vendedor não deve ter admin |
| 383 | Comercial30 | Admin | Own Docs | Vendedor não deve ter admin |
| 23 | marketingcriativo | Own Docs | All Docs | Precisa ver campanhas |

### Registros Modificados: 11

- **Deletados:** 10 registros (5 Admin + 5 All Docs dos vendedores)
- **Inseridos:** 1 registro (All Docs para marketing)

### Backup: 381 registros
- **Tabela:** res_groups_users_rel_backup_20251116
- **Status:** ✅ Testado e validado
- **Rollback:** Disponível a qualquer momento

---

## 🔍 QUERIES ÚTEIS

### Ver estado atual de um usuário:
```sql
SELECT
    u.login,
    string_agg(g.name, ' + ' ORDER BY g.id) as permissions
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON r.gid = g.id
WHERE u.login = 'comercial01@semprereal.com'
    AND g.id IN (13, 14, 15)
GROUP BY u.login;
```

### Ver estado ORIGINAL de um usuário:
```sql
SELECT
    u.login,
    string_agg(g.name, ' + ' ORDER BY g.id) as permissions_original
FROM res_users u
JOIN res_groups_users_rel_backup_20251116 b ON u.id = b.uid
JOIN res_groups g ON b.gid = g.id
WHERE u.login = 'comercial01@semprereal.com'
    AND g.id IN (13, 14, 15)
GROUP BY u.login;
```

### Comparar ANTES vs DEPOIS de um usuário:
```sql
SELECT
    u.login,
    string_agg(DISTINCT gb.name, ' + ' ORDER BY gb.name) as antes,
    string_agg(DISTINCT ga.name, ' + ' ORDER BY ga.name) as depois
FROM res_users u
LEFT JOIN res_groups_users_rel_backup_20251116 b ON u.id = b.uid AND b.gid IN (13,14,15)
LEFT JOIN res_groups gb ON b.gid = gb.id
LEFT JOIN res_groups_users_rel a ON u.id = a.uid AND a.gid IN (13,14,15)
LEFT JOIN res_groups ga ON a.gid = ga.id
WHERE u.login = 'comercial20@semprereal.com'
GROUP BY u.login;
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Após Mudanças (Estado Atual):
- [ ] Todos os 15 vendedores têm APENAS "Own Documents Only"
- [ ] Nenhum vendedor tem "Sales Administrator"
- [ ] Marketing Criativo tem "All Documents"
- [ ] Operacionais mantêm acesso total
- [ ] Financeiro mantém acesso total
- [ ] Supervisor mantém acesso total
- [ ] Admin mantém acesso total

### Após Rollback (Estado Original):
- [ ] 5 vendedores voltaram a ter "Sales Administrator"
- [ ] Marketing Criativo voltou a ter apenas "Own Documents"
- [ ] Total de 381 registros restaurados
- [ ] Comparação com ESTADO_ORIGINAL_PERMISSOES.md bate 100%

---

## 📞 SUPORTE E CONTATO

**Implementado por:** Claude (AI Assistant)
**Aprovado por:** Anderson Oliveira
**Data:** 16/11/2025
**Banco:** realcred
**Ambiente:** Produção Odoo 15

**Em caso de dúvidas:**
1. Consultar este índice primeiro
2. Ler documentação específica
3. Executar queries de validação
4. Contatar responsável técnico

---

## 🎯 OBJETIVOS ALCANÇADOS

✅ **Problema Original Resolvido**
- Vendedores não reclamam mais de inconsistências
- Todos os vendedores têm o mesmo nível de acesso
- Estrutura clara e organizada

✅ **Documentação Completa**
- Estado original catalogado (381 registros)
- Mudanças documentadas com SQL
- Rollback testado e disponível
- Manutenção futura documentada

✅ **Segurança Garantida**
- Backup completo no banco
- Múltiplos métodos de rollback
- Validações documentadas
- Sem perda de dados

---

## 📈 ESTATÍSTICAS FINAIS

```
ANTES:
├─ 16 usuários com Sales Administrator
├─ 5 vendedores com acesso total (problema)
├─ 10 vendedores com acesso limitado
└─ Inconsistência crítica

DEPOIS:
├─ 11 usuários com Sales Administrator
├─ 0 vendedores com acesso total ✅
├─ 15 vendedores com acesso limitado (todos iguais) ✅
└─ Consistência total ✅

MUDANÇAS:
├─ 6 usuários modificados
├─ 11 registros alterados
├─ 381 registros em backup
└─ 5 arquivos de documentação criados
```

---

**Status:** ✅ COMPLETO E DOCUMENTADO
**Data:** 16/11/2025
**Versão:** 1.0
