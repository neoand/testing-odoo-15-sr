# 📦 Instalação de Dependências - FASE 1

> **Data:** 2025-11-20
> **Status:** ⚠️ **AÇÃO NECESSÁRIA**

---

## 🔧 **DEPENDÊNCIA NECESSÁRIA**

### **Package Python: cryptography**

A funcionalidade de criptografia requer o package `cryptography`.

---

## 📋 **INSTALAÇÃO**

### **No Servidor Odoo:**

```bash
# Instalar cryptography
sudo pip3 install cryptography

# OU se usar virtualenv
source /path/to/venv/bin/activate
pip install cryptography

# Verificar instalação
python3 -c "import cryptography; print('✅ cryptography instalado')"
```

---

## ⚠️ **IMPORTANTE**

Se `cryptography` não estiver instalado, a funcionalidade de criptografia não funcionará e pode causar erros ao criar/atualizar providers.

---

## ✅ **VERIFICAÇÃO**

Após instalar, verificar:
```bash
python3 -c "from cryptography.fernet import Fernet; print('✅ OK')"
```

---

**Status:** ⚠️ **Aguardando instalação de cryptography**

