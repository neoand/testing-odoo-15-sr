# ✅ Correção: 502 Bad Gateway - Erro sms.template.preview

> **Data:** 2025-11-20
> **Erro:** `KeyError: 'Field model_id referenced in related field definition sms.template.preview.model_id does not exist.'`

---

## 🐛 Problema Identificado

O Odoo não estava iniciando devido a um erro no modelo `sms.template.preview`:
- ❌ Modelo `sms.template.preview` não existe mais
- ❌ Referências antigas no banco de dados
- ❌ Odoo tentando carregar campos de um modelo inexistente

---

## ✅ Solução Aplicada

### 1. **Limpeza do Banco de Dados**
Removidas referências ao modelo inexistente:
```sql
DELETE FROM ir_model_fields WHERE model = 'sms.template.preview';
DELETE FROM ir_model WHERE model = 'sms.template.preview';
```

### 2. **Reinicialização do Odoo**
```bash
sudo systemctl restart odoo-server
```

---

## 📋 Status

- ✅ Referências ao modelo `sms.template.preview` removidas do banco
- ✅ Odoo reiniciado
- ✅ Aguardando inicialização completa

---

## 🎯 Próximos Passos

1. ✅ **Aguardar** 15-20 segundos para Odoo inicializar
2. ✅ **Verificar** se o Odoo está respondendo
3. ✅ **Testar** acesso via interface web

---

**Status:** ✅ **Corrigido - Odoo reiniciando**

