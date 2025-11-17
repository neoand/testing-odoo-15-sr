# -*- coding: utf-8 -*-
{
    'name': 'RealCred - Permissões Customizadas',
    'version': '15.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Configurações de permissões e grupos customizados para RealCred',
    'description': """
RealCred - Permissões Customizadas
===================================

Este módulo implementa as regras de negócio de permissões da RealCred:

1. **res.partner (Contatos):** CRUD completo para TODOS os usuários internos
2. **Grupo Operacional:** Acesso total CRM (CRUD) + Vendas sem delete (CRU)
3. **Financeiro:** Acesso completo + leitura de CRM
4. **RH:** Acesso restrito apenas para equipe RH + Administradores

Autor: Anderson Oliveira + Claude AI
Data: 17/11/2025
Versão Odoo: 15.0
    """,
    'author': 'RealCred - TI',
    'website': 'https://www.realcred.com.br',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'sale',
        'account',
        'hr',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
