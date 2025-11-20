# 🔍 Teste de Conexão com API Kolmeya

> **Data:** 2025-11-20
> **API Key:** `5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY`

---

## 🧪 Testes Realizados

### **1. Teste com curl (verificação SSL)**
```bash
curl -v -X GET 'https://api.kolmeya.com/v1/status' \
  -H 'Authorization: Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY'
```

### **2. Teste com curl (sem verificação SSL)**
```bash
curl -k -X GET 'https://api.kolmeya.com/v1/status' \
  -H 'Authorization: Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY'
```

### **3. Teste com Python requests**
- Com verificação SSL (`verify=True`)
- Sem verificação SSL (`verify=False`)

### **4. Teste endpoint de balance**
```python
url = 'https://api.kolmeya.com/v1/balance'
headers = {
    'Authorization': 'Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY'
}
```

---

## 📋 Resultados

Os resultados dos testes serão documentados abaixo após execução.

---

## 💡 Próximos Passos

Baseado nos resultados:
1. Se funcionar sem verificação SSL → Implementar workaround temporário
2. Se não funcionar → Contatar suporte Kolmeya
3. Se funcionar → Atualizar código para usar a conexão que funcionou

---

**Status:** 🔄 **Testando conexão...**

