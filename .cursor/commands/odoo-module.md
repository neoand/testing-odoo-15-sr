---
description: Criar estrutura completa de um novo módulo Odoo
---

# Criar Módulo Odoo

Você deve ajudar a criar um novo módulo Odoo completo seguindo as melhores práticas.

## Contexto
- Versão Odoo: 15
- Ambiente: testing_odoo_15_sr
- Padrão: Estrutura modular com security, views, models

## Tarefas
1. Perguntar ao usuário: nome do módulo, descrição, dependências
2. Criar estrutura de diretórios:
   - models/
   - views/
   - security/
   - data/
   - static/
   - wizard/ (se necessário)
3. Criar arquivos base:
   - __manifest__.py
   - __init__.py
   - security/ir.model.access.csv
4. Validar estrutura criada
5. Mostrar próximos passos

## Padrões de Qualidade
- Seguir OCA guidelines
- Documentação inline
- Comentários em português
- Segurança por padrão
