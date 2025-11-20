# ✅ Adicionado: Instruções de Uso de Variáveis no Template SMS

> **Data:** 2025-11-20
> **URL:** https://sempreneo.univsys.net/web#menu_id=945&action=1192&model=sms.template&view_type=form&id=1

---

## 🎯 Objetivo

Adicionar informações visuais no formulário de `sms.template` explicando como utilizar variáveis dinâmicas nas mensagens SMS.

---

## ✅ Solução Implementada

Criado arquivo `sms_template_views.xml` com:

### 1. **Instruções Visuais no Formulário**

Adicionado um **alert informativo** na aba "Message Content" com:

- 📝 **Formato de uso:** `{{nome_da_variavel}}`
- 📋 **Lista de variáveis disponíveis:**
  - `{{name}}` - Nome do contato/parceiro
  - `{{phone}}` - Telefone do contato
  - `{{mobile}}` - Celular do contato
  - `{{email}}` - Email do contato
  - `{{cpf}}` - CPF (se disponível)
  - `{{cnpj}}` - CNPJ (se disponível)
  - `{{value}}` - Valor (para oportunidades/pagamentos)
  - `{{amount}}` - Valor formatado
  - `{{date}}` - Data atual
  - `{{due_date}}` - Data de vencimento
  - `{{partner_name}}` - Nome completo do parceiro
  - `{{company_name}}` - Nome da empresa

- 💡 **Exemplo prático:**
  ```
  Olá {{name}}, seu pagamento de R$ {{value}} vence em {{due_date}}. 
  Entre em contato: {{phone}}
  ```

### 2. **Estrutura da View**

- ✅ **Tree View:** Lista de templates com informações básicas
- ✅ **Form View:** Formulário completo com:
  - Header com botão "Preview"
  - Campo de conteúdo com placeholder
  - **Alert informativo com instruções**
  - Aba "Variables" para gerenciar variáveis customizadas
- ✅ **Search View:** Filtros para buscar templates

---

## 📋 Arquivos Modificados

1. ✅ **Criado:** `sms_core_unified/views/sms_template_views.xml`
2. ✅ **Atualizado:** `sms_core_unified/__manifest__.py` (adicionado ao `data`)

---

## 🎨 Características da Interface

### Alert Informativo:
- 🎨 Estilo Bootstrap (`alert alert-info`)
- 📝 Título destacado
- 📋 Lista de variáveis com código formatado
- 💡 Exemplo prático em box destacado
- ⚠️ Dica final sobre substituição automática

### Layout:
- ✅ Organizado em abas (notebook)
- ✅ Campo de conteúdo com widget `text` (multilinha)
- ✅ Placeholder com exemplo de uso
- ✅ Gerenciamento de variáveis customizadas

---

## 🚀 Próximos Passos

1. ✅ **Atualizar o módulo** `sms_core_unified` via interface web
2. ✅ **Acessar** SMS → Templates → Criar/Editar Template
3. ✅ **Verificar** se as instruções aparecem corretamente

---

## 📸 O que o usuário verá:

Quando acessar o formulário de template, verá:

```
┌─────────────────────────────────────────────────┐
│ 📝 Como Usar Variáveis no Template              │
├─────────────────────────────────────────────────┤
│ Formato: Use {{nome_da_variavel}} para...      │
│                                                 │
│ Variáveis Disponíveis:                         │
│ • {{name}} - Nome do contato                   │
│ • {{phone}} - Telefone do contato             │
│ • {{value}} - Valor                            │
│ ...                                            │
│                                                 │
│ Exemplo de Template:                           │
│ ┌─────────────────────────────────────────┐   │
│ │ Olá {{name}}, seu pagamento de R$      │   │
│ │ {{value}} vence em {{due_date}}.       │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ 💡 Dica: As variáveis serão automaticamente   │
│ substituídas pelos valores reais...           │
└─────────────────────────────────────────────────┘
```

---

**Status:** ✅ **Implementado e pronto para uso**

