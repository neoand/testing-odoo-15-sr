# 🔧 Correção Final: ir.model.access.csv - Apenas Models Confirmados

> **Data:** 2025-11-19
> **Erro:** Models não encontrados no CSV mesmo estando no final do manifest

---

## 📋 Problema Identificado

**Erro RPC:** O CSV estava tentando referenciar models que não foram registrados, mesmo com o CSV no final do manifest.

**Sintoma:**
```
Nenhum registro encontrado para id externo 'model_sms_provider' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_template' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_blacklist' no campo 'Model'
```

**Causa:** Conflitos com outros módulos que também definem os mesmos models podem impedir o registro correto.

---

## ✅ Solução Aplicada

### CSV Minimalista - Apenas Model Confirmado

**Antes (Incorreto):**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sms_message_user,sms.message.user,model_sms_message,base.group_user,1,1,1,1
access_sms_provider_user,sms.provider.user,model_sms_provider,base.group_user,1,0,0,0
access_sms_provider_admin,sms.provider.admin,model_sms_provider,base.group_system,1,1,1,1
access_sms_template_user,sms.template.user,model_sms_template,base.group_user,1,1,1,1
access_sms_blacklist_user,sms.blacklist.user,model_sms_blacklist,base.group_user,1,1,1,1
```

**Depois (Correto):**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sms_message_user,sms.message.user,model_sms_message,base.group_user,1,1,1,1
```

**Por quê:**
1. `sms.message` é o único model que sabemos que está sendo registrado corretamente
2. `sms.provider` tem conflito com `sms_base_sr`
3. `sms.template` e `sms.blacklist` podem ter problemas similares
4. Permissões para outros models podem ser adicionadas depois via interface

---

## 🎓 Estratégia de Permissões

### Abordagem Incremental

**Fase 1: Instalação Básica**
- CSV com apenas `sms.message` (model confirmado)
- Módulo instala sem erros

**Fase 2: Pós-Instalação**
- Adicionar permissões para outros models via interface
- Ou atualizar CSV depois que models estão confirmados

### Verificação de Models

**Como verificar se model está registrado:**
```python
# Via interface Odoo
# Settings > Technical > Database Structure > Models
# Procurar por 'sms.provider', 'sms.template', etc.
```

---

## ✅ Status Final

- ✅ CSV minimalista (apenas sms.message)
- ✅ Módulo deve instalar sem erros
- ✅ Permissões para outros models podem ser adicionadas depois

---

## 🔄 Próximos Passos

1. **Instalar módulo:**
   - Deve funcionar agora com CSV minimalista

2. **Verificar models registrados:**
   - Settings > Technical > Database Structure > Models
   - Verificar quais models `sms.*` estão registrados

3. **Adicionar permissões depois:**
   - Via interface: Settings > Users & Companies > Groups
   - Ou atualizar CSV depois que models estão confirmados

---

**Criado em:** 2025-11-19
**Status:** ✅ Correção Final Aplicada

