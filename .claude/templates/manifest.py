# -*- coding: utf-8 -*-
# Template para __manifest__.py

{
    'name': 'Nome do Módulo',
    'version': '15.0.1.0.0',
    'category': 'Categoria',  # Sales, CRM, Custom, Tools, etc
    'summary': 'Resumo curto do módulo',
    'description': """
        Descrição Longa do Módulo
        ==========================

        Este módulo adiciona funcionalidades de...

        Funcionalidades Principais:
        ---------------------------
        * Feature 1
        * Feature 2
        * Feature 3

        Dependências:
        ------------
        * base
        * crm (se aplicável)

        Notas Técnicas:
        --------------
        - Informações importantes
        - Configurações necessárias
    """,

    # Metadados
    'author': 'Seu Nome / Empresa',
    'website': 'https://www.exemplo.com',
    'license': 'LGPL-3',

    # Versão e dependências
    'version': '15.0.1.0.0',
    'depends': [
        'base',
        'mail',  # Se usar chatter
        # Adicione outras dependências
    ],

    # Arquivos de dados
    'data': [
        # Security
        'security/security_groups.xml',  # Grupos de acesso
        'security/ir.model.access.csv',  # Permissões de modelo
        'security/record_rules.xml',     # Regras de registro

        # Data
        'data/data.xml',                 # Dados iniciais

        # Views
        'views/menu.xml',                # Menus
        'views/model_views.xml',         # Views principais

        # Wizards (se houver)
        'wizard/wizard_views.xml',

        # Reports (se houver)
        'report/report_templates.xml',
    ],

    # Arquivos de demonstração (opcional)
    'demo': [
        'demo/demo_data.xml',
    ],

    # Assets (JS, CSS, SCSS)
    'assets': {
        'web.assets_backend': [
            'module_name/static/src/js/**/*',
            'module_name/static/src/scss/**/*',
        ],
        'web.assets_qweb': [
            'module_name/static/src/xml/**/*',
        ],
    },

    # Configurações
    'installable': True,
    'application': False,  # True se for um módulo principal
    'auto_install': False,  # True para instalar automaticamente

    # Imagens
    'images': ['static/description/banner.png'],

    # Preço (Odoo Apps)
    # 'price': 0.00,
    # 'currency': 'EUR',

    # External dependencies
    'external_dependencies': {
        'python': [
            # 'requests',
            # 'pandas',
        ],
        'bin': [
            # 'wkhtmltopdf',
        ],
    },

    # Post init hook (se necessário)
    # 'post_init_hook': 'post_init_hook',

    # Uninstall hook (se necessário)
    # 'uninstall_hook': 'uninstall_hook',
}
