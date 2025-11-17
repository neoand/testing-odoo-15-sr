---
description: Analisar e corrigir problemas de segurança e permissões do Odoo
---

# Análise de Segurança Odoo

Analisar permissões, grupos de acesso e security rules do projeto.

## Análises a Realizar
1. Verificar ir.model.access.csv de todos os módulos
2. Listar record rules ativas
3. Mapear grupos e suas permissões
4. Identificar inconsistências
5. Sugerir correções

## Foco Especial
- Permissões de res.partner
- Grupos CRM (Manager, User, Salesperson)
- Módulos personalizados (chatroom_sms_advanced)
- Conflitos entre módulos

## Output
- Relatório de inconsistências
- SQL de correção (se necessário)
- Recomendações de melhorias
