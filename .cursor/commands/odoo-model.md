---
description: Criar um novo modelo Odoo com campos, views e segurança
---

# Criar Modelo Odoo

Ajudar a criar um novo modelo (classe Python) no Odoo com toda estrutura necessária.

## Informações Necessárias
- Nome do modelo (ex: crm.lead, res.partner)
- Campos necessários
- Tipo de herança (_name ou _inherit)
- Views necessárias (tree, form, search, kanban)
- Regras de segurança

## Estrutura a Criar
1. Arquivo Python em models/
2. Registro no __init__.py
3. Views XML
4. Permissões no ir.model.access.csv
5. Record rules se necessário

## Validações
- Verificar se modelo já existe
- Validar nomes de campos
- Conferir dependências no manifest
