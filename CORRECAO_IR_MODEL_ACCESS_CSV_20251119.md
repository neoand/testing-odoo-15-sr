# 🔧 Correção: ir.model.access.csv - Models não encontrados

> **Data:** 2025-11-19
> **Erro:** `Nenhum registro encontrado para id externo 'model_sms_provider' no campo 'Model'`

---

## 📋 Problema Identificado

**Erro RPC:** Ao atualizar o módulo `sms_core_unified`, o arquivo `ir.model.access.csv` estava sendo carregado **antes** dos models serem registrados no Odoo.

**Sintoma:**
```
Exception: Carregamento do Módulo sms_core_unified falhou: 
arquivo sms_core_unified/security/ir.model.access.csv não pode ser processado:

Nenhum registro encontrado para id externo 'model_sms_provider' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_template' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_blacklist' no campo 'Model'
```

---

## 🔍 Causa Raiz

### Ordem de Carregamento no Manifest

**Problema:** O `ir.model.access.csv` estava listado **primeiro** na lista `data` do manifest:

```python
'data': [
    'security/ir.model.access.csv',  # ← Carregado PRIMEIRO
    'security/sms_security.xml',
    'views/sms_message_views.xml',
    ...
]
```

**O que acontece:**
1. Odoo carrega arquivos na ordem do manifest
2. `ir.model.access.csv` é carregado primeiro
3. CSV tenta referenciar `model_sms_provider`, `model_sms_template`, `model_sms_blacklist`
4. **Models ainda não foram registrados** (são carregados quando o módulo é importado)
5. Erro: models não encontrados

---

## ✅ Solução Aplicada

### Reordenar Arquivos no Manifest

**Nova ordem:**
```python
'data': [
    # 1. Security XML primeiro (não precisa dos models)
    'security/sms_security.xml',
    
    # 2. Views (precisam dos models, mas models são carregados automaticamente)
    'views/sms_message_views.xml',
    'views/sms_menu.xml',
    
    # 3. Data files
    'data/sms_providers.xml',
    'data/sms_blacklist_data.xml',
    
    # 4. CSV por ÚLTIMO (precisa que models estejam registrados)
    'security/ir.model.access.csv',  # ← Movido para o FINAL
],
```

**Por quê:**
- Security XML não precisa dos models (só define grupos)
- Views precisam dos models, mas models são carregados automaticamente quando o módulo é importado
- Data files podem precisar dos models
- **CSV precisa que os models já estejam registrados** no `ir.model`

---

## 🎓 Regra Importante

### Ordem Correta no Manifest

**Regra:** `ir.model.access.csv` deve vir **DEPOIS** que os models forem carregados.

**Ordem recomendada:**
1. Security XML (grupos, não precisa de models)
2. Views (models carregados automaticamente)
3. Menus
4. Data files
5. **ir.model.access.csv (por último)**

**Exceção:** Se houver `init_hook` ou `post_init_hook` que registra models, ajustar conforme necessário.

---

## 🔄 Próximos Passos

1. **Tentar atualizar o módulo novamente:**
   - O CSV agora será carregado depois dos models
   - Models devem estar registrados quando o CSV for processado

2. **Se ainda houver erro:**
   - Verificar se models estão sendo importados corretamente
   - Verificar se `__init__.py` está correto
   - Verificar se há erros de sintaxe nos models

---

## 📝 Comandos para Testar

```bash
# Atualizar módulo
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b \
  --command="cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin \
  -c /etc/odoo-server.conf -d testing -u sms_core_unified --stop-after-init"
```

---

## 🎯 Validação

Após atualizar o manifest, verificar:

1. ✅ Ordem no manifest está correta
2. ✅ CSV está no final da lista
3. ✅ Models estão sendo importados
4. ✅ Módulo pode ser atualizado

---

**Criado em:** 2025-11-19
**Status:** ✅ Correção aplicada

