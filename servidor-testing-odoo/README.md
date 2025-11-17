# Servidor de Testing Odoo - Documentação Completa

## Visão Geral

Este documento contém toda a documentação necessária para acessar, gerenciar e trabalhar com o servidor de teste do Odoo hospedado no Google Cloud Platform.

**IMPORTANTE:** Esta documentação é escrita em formato "AI First" - estruturada para ser facilmente lida e compreendida por Large Language Models (LLMs) em novos contextos de chat.

## Estrutura da Documentação

### Documentos Principais
- **[RESUMO_EXECUTIVO.md](./RESUMO_EXECUTIVO.md)** - Resumo executivo e visão geral
- **[INDICE_RAPIDO.md](./INDICE_RAPIDO.md)** - Referência rápida e comandos essenciais

### Documentação Detalhada
1. **[CONEXAO_SSH.md](./CONEXAO_SSH.md)** - Como conectar ao servidor via SSH
2. **[DETALHES_TECNICOS.md](./DETALHES_TECNICOS.md)** - Especificações técnicas do servidor
3. **[ACESSOS_CREDENCIAIS.md](./ACESSOS_CREDENCIAIS.md)** - Informações de acesso e credenciais
4. **[CONFIGURACAO_GCP.md](./CONFIGURACAO_GCP.md)** - Configurações do Google Cloud Platform
5. **[COMANDOS_UTEIS.md](./COMANDOS_UTEIS.md)** - Comandos úteis para gerenciamento
6. **[ESTRUTURA_SISTEMA.md](./ESTRUTURA_SISTEMA.md)** - Estrutura de diretórios e serviços
7. **[ODOO_CONFIGURACAO.md](./ODOO_CONFIGURACAO.md)** - Configuração detalhada do Odoo
8. **[MODULOS_ODOO.md](./MODULOS_ODOO.md)** - Lista completa de módulos Odoo instalados

## Informações Rápidas

- **Nome da Instância:** `odoo-sr-tensting`
- **Projeto GCP:** `webserver-258516`
- **Zona:** `southamerica-east1-b`
- **IP Externo:** `35.199.92.1`
- **IP Interno:** `10.158.0.5`
- **Sistema Operacional:** Ubuntu 20.04 LTS
- **Usuário SSH:** `admin_iurd_mx`

## Conexão Rápida

```bash
# Via Google Cloud SDK (recomendado)
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b

# Ou usando o caminho completo
/opt/homebrew/bin/gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

## Última Atualização

- **Data:** 17 de Novembro de 2025
- **Status:** Servidor ativo e acessível
- **Versão da Documentação:** 1.0

