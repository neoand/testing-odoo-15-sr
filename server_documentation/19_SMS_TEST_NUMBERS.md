# SMS Test Numbers - SempreReal

**Data**: 2025-11-15
**Módulo**: sms_base_sr + sms_kolmeya
**Provider**: Kolmeya (https://kolmeya.com.br/)

## Números de Teste Cadastrados

Sempre que realizar testes de SMS, enviar para TODOS estes números:

| Nome | Telefone | DDI+DDD+Número | Status |
|------|----------|----------------|--------|
| Ana Carla | 48 99191-0234 | 5548991910234 | ⚠️ Precisa autorização |
| Tata | 48 99122-1131 | 5548991221131 | ⚠️ Precisa autorização |
| Usuário | 48 99637-5050 | 5548996375050 | ⚠️ Precisa autorização |

## ⚠️ IMPORTANTE: Autorização de Números

A plataforma Kolmeya retornou erro **403 - Invalid** para todos os números de teste, indicando que:

1. **Números precisam ser autorizados na plataforma Kolmeya primeiro**
2. Possível restrição de horário ("Não Perturbe")
3. Possível rate limiting (muitos envios em pouco tempo)

### Como Autorizar Números na Plataforma Kolmeya

Para enviar SMS de teste, é necessário:

1. Acessar https://kolmeya.com.br/
2. Login: SUPERVISAO@REALCREDEMPRESTIMO.COM.BR
3. Senha: Anca741@
4. Ir em configurações de números autorizados/whitelist
5. Adicionar os 3 números de teste acima
6. Ou verificar se há restrições de horário

## Histórico de Testes

### Teste #1 - Sucesso (2025-11-15 22:25)
- **Número**: 5548991910234 (Ana Carla)
- **Status**: ✅ Entregue
- **Message ID**: e3e8dea1-aadb-41ef-8a34-143d2827eb32
- **Job ID**: 69b3884b-5154-4adb-a2f1-12d09df6475b
- **Tempo de entrega**: ~39 segundos

### Teste #2 - Individual (2025-11-15 22:26)
- **Número**: 5548991910234 (Ana Carla)
- **Status**: ✅ Enviado
- **Message ID**: d38f0fc6-6f48-4b27-84ca-c606e6507b9d
- **Job ID**: 012d7091-0dd4-4362-9bdd-657191910312

### Teste #3 - Batch (2025-11-15 22:27)
- **Todos os 3 números**: ❌ Retornaram como inválidos (403)
- **Possível causa**: Números precisam ser autorizados na plataforma

## Formato de Número Correto

```python
# ✅ CORRETO
{
    'phone': '5548991910234',  # DDI (55) + DDD (48) + Número (991910234)
    'message': 'Texto da mensagem',
    'reference': 'identificador_unico'
}

# ❌ ERRADO
'phone': '+5548991910234'  # Não usar +
'phone': '48991910234'     # Falta DDI 55
'phone': '554899191 0234'  # Não usar espaços
```

## Código Python para Teste em Lote

```python
import requests

url = 'https://kolmeya.com.br/api/v1/sms/store'
headers = {
    'Authorization': 'Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY',
    'Content-Type': 'application/json'
}

# Batch com todos os números de teste
payload = {
    'messages': [
        {
            'phone': '5548991910234',
            'message': 'Teste Ana Carla - SempreReal SMS',
            'reference': 'test_ana'
        },
        {
            'phone': '5548991221131',
            'message': 'Teste Tata - SempreReal SMS',
            'reference': 'test_tata'
        },
        {
            'phone': '5548996375050',
            'message': 'Teste Usuário - SempreReal SMS',
            'reference': 'test_user'
        }
    ]
}

response = requests.post(url, json=payload, headers=headers, timeout=30)
print(response.json())
```

## Próximos Passos

1. ✅ Autorizar os 3 números de teste na plataforma Kolmeya
2. 🔄 Re-testar envio em lote após autorização
3. 🔄 Implementar webhook para captura de respostas
4. 🔄 Integrar com contacts.realcred.campaign

## Saldo Atual

- **Saldo**: R$ 9.397,15
- **Última verificação**: 2025-11-15 22:25
- **Endpoint**: POST https://kolmeya.com.br/api/v1/sms/balance

## Referências

- [Documentação Kolmeya API](https://kolmeya.com.br/docs/api/)
- [Módulo sms_base_sr](/odoo/custom/addons_custom/sms_base_sr)
- [Módulo sms_kolmeya](/odoo/custom/addons_custom/sms_kolmeya)
- [Implementação completa](./18_SMS_IMPLEMENTATION_SUCCESS.md)
