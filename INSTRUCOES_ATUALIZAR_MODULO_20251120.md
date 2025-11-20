# 📋 Instruções: Atualizar Módulo após Correções

> **Data:** 2025-11-20
> **Status:** ✅ **PRONTO PARA ATUALIZAR**

---

## ✅ **CORREÇÕES APLICADAS**

1. ✅ Método `action_check_status()` adicionado ao modelo `sms.message`
2. ✅ Erro de sintaxe corrigido
3. ✅ Cache Python limpo
4. ✅ Odoo reiniciado (HUP signal)

---

## 📝 **PASSO A PASSO PARA ATUALIZAR**

### **1. Acessar Odoo:**
- Abra o navegador
- Acesse a URL do Odoo
- Faça login

### **2. Ativar Modo Desenvolvedor (se necessário):**
- Menu: **Configurações** > **Ativar Modo Desenvolvedor**
- Ou adicione `?debug=1` na URL

### **3. Atualizar Módulo:**
1. Menu: **Apps**
2. Remova filtro "Apps" (mostrar todos)
3. Procure por: **SMS Core Unified**
4. Clique no módulo
5. Clique em **Upgrade**

### **4. Verificar:**
- Verifique se não há erros
- Acesse uma mensagem SMS
- Verifique se o botão "Check Status" aparece

---

## 🔄 **SE O ERRO PERSISTIR**

### **Opção 1: Reiniciar Odoo Completamente**
```bash
# No servidor
sudo pkill -9 -f 'odoo-bin'
# Aguardar alguns segundos
# Odoo deve reiniciar automaticamente (se houver supervisor/systemd)
```

### **Opção 2: Limpar Cache Manualmente**
```bash
# No servidor
sudo rm -rf /odoo/custom/addons_custom/sms_core_unified/models/__pycache__/*
sudo rm -rf /odoo/custom/addons_custom/sms_core_unified/__pycache__/*
```

### **Opção 3: Verificar Método no Código**
```bash
# No servidor
grep -n "def action_check_status" /odoo/custom/addons_custom/sms_core_unified/models/sms_message.py
```

---

## ✅ **VALIDAÇÃO**

O método `action_check_status` está presente no arquivo:
- ✅ Linha 124 do arquivo `sms_message.py`
- ✅ Sintaxe Python válida
- ✅ Cache limpo
- ✅ Odoo reiniciado

---

## 💡 **NOTA**

Se o erro persistir após atualizar o módulo, pode ser necessário:
1. Reiniciar completamente o servidor Odoo
2. Verificar se há outros processos Odoo rodando
3. Limpar todos os caches Python

---

**Status:** ✅ **Pronto para atualizar módulo no Odoo**

