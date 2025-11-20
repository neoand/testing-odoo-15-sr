# 🔐 Explicação: Webhook Secret

> **Data:** 2025-11-20
> **Status:** 📋 **INFORMAÇÕES**

---

## 🔑 **O QUE É O WEBHOOK SECRET?**

O **Webhook Secret** é uma chave secreta usada para **validar** que os webhooks recebidos realmente vêm da API Kolmeya, garantindo segurança.

---

## 🎯 **PARA QUE SERVE?**

1. **Segurança:** Garante que apenas a Kolmeya pode enviar webhooks válidos
2. **Validação:** O código verifica a assinatura do webhook usando este secret
3. **Proteção:** Previne ataques de webhooks falsos

---

## ✅ **É OBRIGATÓRIO?**

**NÃO é obrigatório**, mas **altamente recomendado** para produção.

### **Sem Webhook Secret:**
- ✅ Webhooks ainda funcionam
- ⚠️ Sem validação de segurança
- ⚠️ Qualquer um pode enviar webhooks falsos

### **Com Webhook Secret:**
- ✅ Webhooks validados e seguros
- ✅ Apenas Kolmeya pode enviar webhooks válidos
- ✅ Proteção contra ataques

---

## 📝 **COMO OBTER O WEBHOOK SECRET?**

### **Opção 1: Gerar Você Mesmo (Recomendado)**

Você pode gerar uma string aleatória segura:

```python
import secrets
secret = secrets.token_urlsafe(32)
print(secret)
```

Ou usar um gerador online de tokens seguros.

### **Opção 2: Usar o Secret da Kolmeya**

Alguns provedores fornecem um secret quando você configura o webhook. Verifique:
- Dashboard da Kolmeya
- Documentação da API Kolmeya
- Suporte da Kolmeya

### **Opção 3: Deixar Vazio (Desenvolvimento)**

Para desenvolvimento/testes, você pode deixar vazio. O código ainda funcionará, mas sem validação.

---

## 🔧 **COMO CONFIGURAR?**

### **1. No Odoo:**
1. Acesse o provider Kolmeya
2. No campo **"Webhook Secret"**, cole o secret gerado
3. Salve

### **2. Na Kolmeya (se necessário):**
- Configure o mesmo secret no dashboard da Kolmeya
- Isso garante que ambos os lados usem a mesma chave

---

## 💻 **COMO O CÓDIGO USA?**

O código usa o secret para validar a assinatura do webhook:

```python
def _verify_kolmeya_signature(self, payload, signature):
    webhook_secret = provider.kolmeya_webhook_secret
    # Gera assinatura esperada
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    # Compara com assinatura recebida
    return hmac.compare_digest(expected_signature, signature)
```

---

## 📋 **RESUMO**

| Item | Status |
|------|--------|
| **Obrigatório?** | ❌ Não (mas recomendado) |
| **Temos essa info?** | ⚠️ Precisa gerar/configurar |
| **Como obter?** | Gerar você mesmo ou usar da Kolmeya |
| **Onde configurar?** | Campo "Webhook Secret" no provider |

---

## 💡 **RECOMENDAÇÃO**

1. **Para Desenvolvimento/Testes:**
   - Pode deixar vazio por enquanto
   - Webhooks ainda funcionarão

2. **Para Produção:**
   - Gere um secret seguro
   - Configure no Odoo
   - Configure na Kolmeya (se necessário)

---

**Status:** 📋 **Webhook Secret é opcional mas recomendado para segurança**

