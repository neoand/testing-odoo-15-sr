---
description: Executar e criar testes para módulos Odoo
---

# Testes Odoo

Executar testes existentes ou criar novos testes unitários/integração.

## Executar Testes
```bash
# Testar módulo específico
python odoo-bin -c odoo.conf -d DATABASE -u MODULE --test-enable --stop-after-init

# Testar apenas uma classe/método
python odoo-bin -c odoo.conf -d DATABASE --test-tags /MODULE:CLASS.method
```

## Criar Testes
Estrutura base para testes Odoo:
- Herdar de `TransactionCase` ou `SavepointCase`
- Usar `setUpClass` para dados comuns
- Prefixo `test_` nos métodos
- Assertions claros

## Tipos de Teste
1. **Unit Tests** - Métodos isolados
2. **Integration Tests** - Fluxos completos
3. **Access Rights** - Permissões
4. **UI Tests** - Tours JavaScript

## Coverage
- Verificar cobertura com `coverage.py`
- Meta: >80% coverage em código crítico
