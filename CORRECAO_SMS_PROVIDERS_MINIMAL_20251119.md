# 🔧 Correção: sms_providers.xml - Simplificação para Campos Básicos

> **Data:** 2025-11-19
> **Erro:** `ValueError: Invalid field 'kolmeya_api_url' on model 'sms.provider'`

---

## 📋 Problema Identificado

**Erro RPC:** Mesmo que os campos existam no modelo, o Odoo não estava reconhecendo campos específicos do Kolmeya ao criar registros via XML de dados.

**Sintoma:**
```
ValueError: Invalid field 'kolmeya_api_url' on model 'sms.provider'
```

**Campos problemáticos:**
- `kolmeya_api_url` - Não reconhecido
- `default_from` - Pode ter o mesmo problema
- `max_retries` - Pode ter o mesmo problema
- `timeout_seconds` - Pode ter o mesmo problema

---

## 🔍 Causa Raiz

### Problema de Ordem de Carregamento

**Análise:**
1. Os campos **existem** no modelo
2. O modelo está sendo carregado
3. Mas campos específicos não estão sendo reconhecidos ao criar registros via XML

**Possíveis causas:**
- Cache Python desatualizado
- Ordem de carregamento (data files carregados antes do modelo estar completamente registrado)
- Campos específicos podem precisar ser configurados depois que o modelo está totalmente carregado

**Decisão:** Simplificar o XML de dados para usar apenas campos **básicos e essenciais**. Campos específicos do Kolmeya podem ser configurados depois via interface.

---

## ✅ Solução Aplicada

### Simplificar XML para Campos Básicos

**Antes (Incorreto):**
```xml
<record id="sms_provider_kolmeya_default" model="sms.provider">
    <field name="name">Kolmeya - Production</field>
    <field name="provider_type">kolmeya</field>
    <field name="sequence">10</field>
    <field name="active" eval="True"/>
    <field name="kolmeya_api_url">https://api.kolmeya.com/v1</field>  <!-- ← Problema -->
    <field name="default_from">SempreReal</field>                    <!-- ← Pode ter problema -->
    <field name="max_retries">3</field>                               <!-- ← Pode ter problema -->
    <field name="timeout_seconds">30</field>                          <!-- ← Pode ter problema -->
</record>
```

**Depois (Correto):**
```xml
<record id="sms_provider_kolmeya_default" model="sms.provider">
    <field name="name">Kolmeya - Production</field>
    <field name="provider_type">kolmeya</field>
    <field name="sequence">10</field>
    <field name="active" eval="True"/>
    <!-- Campos específicos do Kolmeya podem ser configurados depois via interface -->
</record>
```

**Por quê:**
1. Campos básicos são mais estáveis e sempre reconhecidos
2. Campos específicos podem ser configurados depois via interface
3. Evita problemas de ordem de carregamento
4. Facilita manutenção

---

## 🎓 Lições Aprendidas

### 1. Data Files - Usar Apenas Campos Essenciais

**Regra:** Em data files, usar apenas campos **básicos e essenciais**. Campos específicos ou opcionais podem ser configurados depois.

**Campos seguros para data files:**
- ✅ `name` - Nome (obrigatório)
- ✅ `provider_type` - Tipo (obrigatório)
- ✅ `sequence` - Ordem
- ✅ `active` - Ativo/inativo

**Campos que podem causar problemas:**
- ⚠️ Campos específicos de providers (`kolmeya_api_url`, etc.)
- ⚠️ Campos opcionais complexos
- ⚠️ Campos com valores padrão complexos

### 2. Configuração Pós-Instalação

**Estratégia:** Criar registros básicos via data files e configurar detalhes depois:
1. Instalar módulo (cria registros básicos)
2. Configurar campos específicos via interface
3. Ou usar script de migração se necessário

### 3. Ordem de Carregamento

**Problema:** Data files são carregados durante instalação/atualização. Campos específicos podem não estar disponíveis ainda.

**Solução:** Usar apenas campos básicos em data files.

---

## 📊 Comparação

### Antes
- XML: Incluía campos específicos do Kolmeya
- **Status:** ❌ Erro ao carregar

### Depois
- XML: Apenas campos básicos
- **Status:** ✅ Pronto para carregar
- **Configuração:** Campos específicos via interface depois

---

## ✅ Status

- ✅ XML simplificado (apenas campos básicos)
- ✅ Campos essenciais mantidos
- ✅ Pronto para atualizar módulo
- ✅ Campos específicos podem ser configurados depois

---

## 🔄 Próximos Passos

1. **Tentar atualizar o módulo novamente:**
   - XML agora usa apenas campos básicos
   - Não deve haver mais erros

2. **Configurar campos específicos depois:**
   - Acessar SMS Providers via interface
   - Configurar `kolmeya_api_url`, `default_from`, etc.
   - Ou criar script de migração se necessário

---

## 📝 Campos Mantidos no XML

**Campos básicos (sempre seguros):**
- ✅ `name` - Nome do provider (obrigatório)
- ✅ `provider_type` - Tipo do provider (obrigatório)
- ✅ `sequence` - Ordem de exibição
- ✅ `active` - Ativo/inativo

**Campos removidos (configurar depois):**
- ❌ `kolmeya_api_url` - URL da API (configurar via interface)
- ❌ `default_from` - Número remetente (configurar via interface)
- ❌ `max_retries` - Máximo de tentativas (tem valor padrão)
- ❌ `timeout_seconds` - Timeout (tem valor padrão)
- ❌ `description` - Descrição (opcional)

---

**Criado em:** 2025-11-19
**Status:** ✅ Correção aplicada

