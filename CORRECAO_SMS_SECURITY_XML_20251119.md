# 🔧 Correção: sms_security.xml - Referências a Models não encontrados

> **Data:** 2025-11-19
> **Erro:** `ValueError: External ID not found in the system: sms_core_unified.model_sms_provider`

---

## 📋 Problema Identificado

**Erro RPC:** O arquivo `sms_security.xml` estava tentando criar registros de `ir.model.access` que referenciam models ainda não registrados.

**Sintoma:**
```
ValueError: External ID not found in the system: sms_core_unified.model_sms_provider
```

**Localização do erro:**
```xml
<record id="access_sms_provider_manager" model="ir.model.access">
    <field name="model_id" ref="model_sms_provider"/>  <!-- ← Erro aqui -->
    ...
</record>
```

---

## 🔍 Causa Raiz

### Duplicação de Definições

**Problema:** O `sms_security.xml` estava definindo `ir.model.access` que também estão no CSV:

1. **XML** define `ir.model.access` com `ref="model_sms_provider"`
2. **CSV** também define as mesmas permissões
3. XML é carregado **antes** dos models serem registrados
4. Erro: `model_sms_provider` não existe ainda

**Conflito:**
- XML tenta criar permissões antes dos models existirem
- CSV já tem todas as permissões necessárias
- Duplicação desnecessária

---

## ✅ Solução Aplicada

### Remover ir.model.access do XML

**Decisão:** Remover todas as definições de `ir.model.access` do XML e manter apenas os grupos (`res.groups`).

**Antes (Incorreto):**
```xml
<odoo>
    <data>
        <!-- Grupos -->
        <record id="group_sms_user" model="res.groups">...</record>
        <record id="group_sms_manager" model="res.groups">...</record>
        
        <!-- Permissões (PROBLEMA!) -->
        <record id="access_sms_provider_manager" model="ir.model.access">
            <field name="model_id" ref="model_sms_provider"/>  <!-- ← Erro -->
            ...
        </record>
        ...
    </data>
</odoo>
```

**Depois (Correto):**
```xml
<odoo>
    <data>
        <!-- Grupos -->
        <record id="group_sms_user" model="res.groups">...</record>
        <record id="group_sms_manager" model="res.groups">...</record>
        
        <!-- NOTA: Permissões movidas para ir.model.access.csv -->
    </data>
</odoo>
```

**Por quê:**
1. **Grupos** (`res.groups`) não precisam dos models
2. **Permissões** (`ir.model.access`) já estão no CSV
3. CSV é carregado **depois** dos models serem registrados
4. Evita duplicação e problemas de ordem

---

## 🎓 Regra Importante

### Separação de Responsabilidades

**XML (`sms_security.xml`):**
- ✅ Definir grupos (`res.groups`)
- ✅ Definir regras de acesso (`ir.rule`) se necessário
- ❌ **NÃO** definir `ir.model.access` (usar CSV)

**CSV (`ir.model.access.csv`):**
- ✅ Definir todas as permissões de acesso
- ✅ Carregado por último (após models registrados)

**Benefícios:**
- Evita problemas de ordem de carregamento
- CSV é mais fácil de editar
- Separação clara de responsabilidades

---

## 📊 Comparação

### Antes
- XML: Grupos + Permissões (duplicado)
- CSV: Permissões (duplicado)
- **Problema:** XML carregado antes dos models

### Depois
- XML: Apenas Grupos ✅
- CSV: Apenas Permissões ✅
- **Solução:** CSV carregado depois dos models

---

## ✅ Status

- ✅ XML atualizado (apenas grupos)
- ✅ CSV mantido (todas as permissões)
- ✅ Duplicação removida
- ✅ Ordem correta no manifest
- ✅ Pronto para atualizar módulo

---

## 🔄 Próximos Passos

1. **Tentar atualizar o módulo novamente:**
   - XML agora só tem grupos (não precisa de models)
   - CSV tem todas as permissões (carregado depois)

2. **Se ainda houver erro:**
   - Verificar se CSV está correto
   - Verificar se models estão sendo importados

---

## 📝 Comandos para Testar

```bash
# Verificar XML atualizado
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b \
  --command="cat /odoo/custom/addons_custom/sms_core_unified/security/sms_security.xml"

# Verificar CSV
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b \
  --command="cat /odoo/custom/addons_custom/sms_core_unified/security/ir.model.access.csv"
```

---

**Criado em:** 2025-11-19
**Status:** ✅ Correção aplicada

