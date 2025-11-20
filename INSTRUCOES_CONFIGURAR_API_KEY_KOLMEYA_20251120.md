# 📋 Instruções: Como Configurar API Key Kolmeya

> **Data:** 2025-11-20
> **Status:** ✅ **INSTRUÇÕES**

---

## 🔑 **COMO CONFIGURAR A API KEY**

### **Sua API Key:**
```
Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
```

### **⚠️ IMPORTANTE:**
O código **JÁ ADICIONA** o prefixo "Bearer" automaticamente.

### **✅ O QUE VOCÊ DEVE COLOCAR:**

**Apenas a chave, SEM o "Bearer":**
```
5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
```

---

## 📝 **PASSO A PASSO**

### **1. Acessar Provider:**
1. Vá em **SMS** > **Providers** (ou **SMS Providers**)
2. Abra o provider **Kolmeya**

### **2. Configurar API Key:**
1. No campo **"Kolmeya API Key"**, cole apenas:
   ```
   5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
   ```
2. **NÃO** coloque "Bearer" antes
3. **NÃO** coloque espaços extras

### **3. Verificar URL:**
- Certifique-se que o campo **"Kolmeya API URL"** está como:
  ```
  https://kolmeya.com.br/api/v1
  ```

### **4. Salvar:**
- Clique em **Salvar**

### **5. Testar:**
- Clique no botão **"Testar Conexão"**
- Deve aparecer mensagem de sucesso

---

## 🔍 **COMO O CÓDIGO USA A API KEY**

O código automaticamente adiciona "Bearer" quando faz as requisições:

```python
headers={
    'Authorization': f'Bearer {self.kolmeya_api_key}',
    ...
}
```

Por isso você deve colocar **apenas a chave**, sem o "Bearer".

---

## ✅ **EXEMPLO CORRETO**

**Campo "Kolmeya API Key":**
```
5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
```

**O código vai usar como:**
```
Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
```

---

## ❌ **EXEMPLO ERRADO**

**NÃO faça isso:**
```
Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
```

Isso resultaria em:
```
Bearer Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
```
(duplo "Bearer" - ERRADO!)

---

## 💡 **RESUMO**

1. ✅ Cole apenas: `5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY`
2. ❌ **NÃO** coloque "Bearer" antes
3. ✅ Salve e teste a conexão

---

**Status:** ✅ **Instruções completas - Configure apenas a chave sem "Bearer"**

