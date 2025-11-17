# ChatRoom SMS Advanced - O Melhor Módulo de SMS para Odoo 15

![License](https://img.shields.io/badge/license-LGPL--3-blue.svg)
![Version](https://img.shields.io/badge/version-15.0.1.0.0-green.svg)
![Odoo](https://img.shields.io/badge/odoo-15.0-purple.svg)

> **O módulo de SMS mais completo e profissional do planeta para Odoo 15!**

Desenvolvido com amor por **Anderson Oliveira** + **Claude AI** em 16/11/2025.

---

## Descrição

O **ChatRoom SMS Advanced** é uma solução completa e poderosa para gerenciamento de SMS no Odoo 15. Este módulo oferece integração total com a API Kolmeya SMS, permitindo envio individual, em massa, agendamento, templates personalizados, webhooks automáticos, controle de blacklist, dashboard interativo e muito mais!

Se você precisa enviar SMS de forma profissional, rastrear entregas, automatizar notificações e ter controle total sobre suas comunicações via SMS, este é o módulo que você estava procurando.

---

## Funcionalidades

### PRIORIDADE 1 - ESSENCIAL

- **Webhooks Automáticos de Status**
  - Receba notificações em tempo real quando um SMS for entregue, falhar ou for respondido
  - URLs de webhook configuráveis por API
  - Atualização automática de status no log
  - Suporte para respostas bidirecionais (SMS recebidos)

- **Consulta Automática de Saldo**
  - Verificação automática de créditos via cron job configurável
  - Alertas visuais quando o saldo estiver abaixo do mínimo
  - Histórico de consultas de saldo
  - Dashboard mostra saldo atual em tempo real

- **Sistema Completo de Blacklist e "Não Perturbe"**
  - Bloqueio automático de números em blacklist
  - Marcação manual de contatos para não perturbar
  - Validação antes de cada envio
  - Gestão centralizada de números bloqueados

### PRIORIDADE 2 - GESTÃO

- **Log Completo de TODOS os SMS Enviados**
  - Registro detalhado de cada SMS (data, hora, destino, mensagem, status, custo)
  - Filtros avançados por status, período, destinatário
  - Busca full-text em mensagens
  - Exportação de relatórios
  - Rastreamento de ID Kolmeya para cada envio

- **Envio em Lote (até 1000 mensagens por vez)**
  - Wizard intuitivo para envio em massa
  - Seleção por modelo (res.partner, leads, etc)
  - Segmentação por filtros personalizados
  - Preview antes do envio
  - Processamento assíncrono para grandes volumes
  - Barra de progresso em tempo real

- **Dashboard Visual com Estatísticas e Gráficos**
  - Visão geral de SMS enviados, entregues, falhados
  - Gráficos interativos por período
  - Métricas de taxa de entrega e falha
  - Top destinatários
  - Análise de custo por período
  - Saldo de créditos destacado

### PRIORIDADE 3 - PRODUTIVIDADE

- **Sistema de Templates de Mensagens**
  - Criação de templates reutilizáveis
  - Variáveis dinâmicas (nome, empresa, data, etc)
  - Categorização de templates
  - Preview com dados reais
  - Templates padrão pré-configurados (boas-vindas, confirmação, lembrete)

- **Agendamento de Envios**
  - Agende SMS para data e hora específicas
  - Gestão de fila de agendamentos
  - Cancelamento de envios pendentes
  - Processamento automático via cron job
  - Status: rascunho, agendado, enviado, cancelado, falhou

- **Rastreamento de Links Curtos**
  - Encurtamento automático de URLs longas
  - Rastreamento de cliques
  - Estatísticas de engajamento
  - Integração com Google Analytics (UTM)

- **Autenticação 2FA via SMS**
  - Envio de códigos de verificação
  - Validação de códigos com timeout
  - Logs de tentativas de autenticação
  - Integração com login do Odoo

### EXTRAS

- **Relatórios Avançados por Período**
  - Relatórios customizáveis
  - Análise comparativa mensal/semanal
  - Exportação em PDF e Excel
  - Gráficos de tendências

- **Centros de Custo**
  - Alocação de custos por departamento
  - Rastreamento de gastos por projeto
  - Relatórios financeiros detalhados

- **Analytics Completo**
  - Taxa de conversão de SMS
  - Análise de horários de melhor performance
  - Métricas de ROI

- **API REST para Integração Externa**
  - Endpoints para envio via API externa
  - Autenticação por token
  - Documentação Swagger
  - Webhooks bidirecionais

---

## Instalação

### Passo a Passo

1. **Clone ou copie o módulo para sua pasta de addons do Odoo 15:**

   ```bash
   cd /path/to/odoo/addons
   cp -r /caminho/chatroom_sms_advanced .
   ```

2. **Reinicie o servidor Odoo:**

   ```bash
   sudo systemctl restart odoo15
   # ou
   ./odoo-bin -c /path/to/odoo.conf
   ```

3. **Atualize a lista de aplicativos:**
   - Vá para `Aplicativos`
   - Clique em `Atualizar Lista de Aplicativos`
   - Remova o filtro "Aplicativos" na busca
   - Pesquise por "ChatRoom SMS Advanced"

4. **Instale o módulo:**
   - Clique em `Instalar`
   - Aguarde a instalação ser concluída

5. **Pronto!** O menu "SMS" aparecerá no topo do Odoo.

### Requisitos

- **Odoo 15.0** ou superior
- **Módulo chatroom** (base) instalado
- **Python 3.7+**
- **Bibliotecas Python:**
  - `requests` (para chamadas HTTP à API Kolmeya)
  - `phonenumbers` (para validação de números)

Instale as dependências Python:

```bash
pip3 install requests phonenumbers
```

---

## Configuração Inicial

### 1. Configurar API Kolmeya

1. Acesse: **SMS > Configuração > APIs SMS**
2. Clique em **Criar**
3. Preencha os campos:
   - **Nome:** "Kolmeya Principal" (ou outro nome)
   - **Provedor:** Selecione "Kolmeya"
   - **API Key:** Cole sua chave de API da Kolmeya
   - **URL Base:** `https://api.kolmeya.com.br` (padrão)
   - **Status:** Ativo
   - **Saldo Mínimo Alerta:** 100 (ou valor desejado)
4. Clique em **Salvar**
5. Clique no botão **Testar Conexão** para verificar se está tudo OK
6. Clique em **Consultar Saldo** para ver seus créditos atuais

### 2. Configurar Webhook URL

As URLs de webhook são geradas automaticamente no formato:

```
https://seu-dominio.com/chatroom_sms/webhook/status
https://seu-dominio.com/chatroom_sms/webhook/reply
```

**Configure no painel da Kolmeya:**

1. Acesse o painel de controle da Kolmeya
2. Vá em Configurações > Webhooks
3. Adicione as URLs acima
4. Selecione os eventos: `delivered`, `failed`, `replied`
5. Salve

**Teste os webhooks:**

```bash
# Teste webhook de status
curl -X POST https://seu-dominio.com/chatroom_sms/webhook/status \
  -H "Content-Type: application/json" \
  -d '{
    "id": "123456",
    "status": "delivered",
    "timestamp": "2025-11-16 10:30:00"
  }'

# Teste webhook de resposta
curl -X POST https://seu-dominio.com/chatroom_sms/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+5511999999999",
    "message": "Sim, confirmo!",
    "timestamp": "2025-11-16 10:35:00"
  }'
```

### 3. Sincronizar Segmentos

1. Acesse: **SMS > Configuração > Segmentos**
2. Clique no botão **Sincronizar Segmentos Kolmeya**
3. Aguarde a sincronização (pode levar alguns segundos)
4. Os segmentos disponíveis na Kolmeya serão importados automaticamente

### 4. Criar Templates

O módulo já vem com 3 templates padrão:

- **Boas-vindas:** "Olá {name}, bem-vindo à {company}!"
- **Confirmação:** "Sua solicitação foi confirmada. Protocolo: {ref}"
- **Lembrete:** "Lembrete: você tem um compromisso em {date}"

**Para criar templates personalizados:**

1. Acesse: **SMS > Configuração > Templates**
2. Clique em **Criar**
3. Preencha:
   - **Nome:** Nome do template
   - **Código:** Código único (ex: `template_cobranca`)
   - **Mensagem:** Texto com variáveis (ex: `{name}`, `{company}`)
   - **Categoria:** Transacional, Marketing, Alerta, etc
   - **Status:** Ativo
4. Clique em **Salvar**

**Variáveis disponíveis:**

- `{name}` - Nome do destinatário
- `{company}` - Nome da empresa
- `{date}` - Data atual
- `{ref}` - Referência/Protocolo
- `{value}` - Valor/Quantia
- `{phone}` - Telefone do destinatário

---

## Uso

### Como Enviar SMS Individual

**Método 1: Via Contato (res.partner)**

1. Abra um contato em **Contatos**
2. Clique no botão **Enviar SMS** (ícone de mensagem)
3. Preencha a mensagem ou selecione um template
4. Clique em **Enviar**

**Método 2: Via Teste de SMS**

1. Acesse: **SMS > Enviar SMS > Teste de SMS**
2. Preencha:
   - **Número de Telefone:** +5511999999999
   - **Mensagem:** Seu texto aqui
   - **API SMS:** Selecione a API configurada
3. Clique em **Enviar SMS de Teste**

### Como Enviar em Massa

1. Acesse: **SMS > Enviar SMS > Envio em Massa**
2. Selecione o **Modelo de Destinatários** (Contatos, Leads, etc)
3. Aplique **Filtros** se necessário (ex: país = Brasil)
4. Selecione um **Template** ou escreva a mensagem manualmente
5. Clique em **Preview Destinatários** para ver quantos receberão
6. Clique em **Enviar SMS em Massa**
7. Aguarde o processamento (barra de progresso)
8. Verifique o log em **SMS > Histórico > Log de SMS**

### Como Agendar

1. Acesse: **SMS > Histórico > SMS Agendados**
2. Clique em **Criar**
3. Preencha:
   - **Nome:** Descrição do agendamento
   - **Data de Envio:** Data e hora futura
   - **Destinatário:** Selecione o contato
   - **Mensagem:** Texto do SMS
   - **API SMS:** API a ser usada
4. Clique em **Salvar**
5. O status ficará como "Agendado"
6. No horário configurado, o cron job enviará automaticamente

**Cancelar um agendamento:**

- Abra o registro agendado
- Clique em **Cancelar Agendamento**

### Como Usar Templates

**Ao enviar SMS individual:**

1. Clique em **Selecionar Template**
2. Escolha o template desejado
3. As variáveis serão substituídas automaticamente
4. Edite se necessário
5. Envie

**Ao enviar em massa:**

1. No wizard, selecione o template no campo **Template SMS**
2. As variáveis serão processadas para cada destinatário
3. Preview mostrará uma amostra
4. Envie

---

## Webhooks

### URLs dos Webhooks

O módulo expõe 2 endpoints públicos para receber webhooks da Kolmeya:

**1. Webhook de Status (Entrega/Falha):**

```
POST https://seu-dominio.com/chatroom_sms/webhook/status
```

**2. Webhook de Resposta (SMS Recebido):**

```
POST https://seu-dominio.com/chatroom_sms/webhook/reply
```

### Como Testar

**Teste 1: Status Delivered**

```bash
curl -X POST https://seu-dominio.com/chatroom_sms/webhook/status \
  -H "Content-Type: application/json" \
  -d '{
    "id": "kol_123456789",
    "status": "delivered",
    "timestamp": "2025-11-16T14:30:00Z",
    "phone": "+5511999999999"
  }'
```

**Teste 2: Status Failed**

```bash
curl -X POST https://seu-dominio.com/chatroom_sms/webhook/status \
  -H "Content-Type: application/json" \
  -d '{
    "id": "kol_123456789",
    "status": "failed",
    "timestamp": "2025-11-16T14:30:00Z",
    "phone": "+5511999999999",
    "error": "Invalid number"
  }'
```

**Teste 3: Resposta Recebida**

```bash
curl -X POST https://seu-dominio.com/chatroom_sms/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+5511999999999",
    "to": "+5511888888888",
    "message": "Sim, confirmo minha presença!",
    "timestamp": "2025-11-16T14:35:00Z",
    "id": "kol_reply_987654321"
  }'
```

### Estrutura de Dados

**Webhook de Status:**

```json
{
  "id": "ID_KOLMEYA",           // ID retornado ao enviar SMS
  "status": "delivered|failed",  // Status do envio
  "timestamp": "ISO8601",        // Data/hora do evento
  "phone": "+5511999999999",     // Número do destinatário
  "error": "Mensagem de erro"    // Apenas se status = failed
}
```

**Webhook de Resposta:**

```json
{
  "from": "+5511999999999",      // Número que respondeu
  "to": "+5511888888888",        // Número da empresa (remetente original)
  "message": "Texto da resposta", // Conteúdo da resposta
  "timestamp": "ISO8601",         // Data/hora da resposta
  "id": "ID_KOLMEYA"             // ID único da resposta
}
```

**Respostas do Odoo:**

- **Sucesso:** HTTP 200 + `{"status": "success", "message": "..."}`
- **Erro:** HTTP 400/500 + `{"status": "error", "message": "..."}`

---

## Troubleshooting

### Problema: "Erro ao conectar com a API Kolmeya"

**Soluções:**

- Verifique se a API Key está correta
- Teste a conexão em **SMS > Configuração > APIs SMS**
- Confirme se a URL base está correta: `https://api.kolmeya.com.br`
- Verifique se o servidor Odoo tem acesso à internet
- Confira os logs do Odoo: `tail -f /var/log/odoo/odoo.log`

### Problema: "Saldo insuficiente"

**Soluções:**

- Consulte o saldo em **SMS > Configuração > APIs SMS** > botão "Consultar Saldo"
- Recarregue créditos no painel da Kolmeya
- Ajuste o campo "Saldo Mínimo Alerta" para receber avisos antecipados

### Problema: "SMS não está sendo enviado"

**Soluções:**

- Verifique se o número está no formato internacional: `+5511999999999`
- Confirme se o número não está na blacklist
- Verifique se a API SMS está ativa
- Consulte o log em **SMS > Histórico > Log de SMS** para ver o erro
- Verifique se há saldo suficiente

### Problema: "Webhooks não estão funcionando"

**Soluções:**

- Confirme se as URLs estão configuradas corretamente na Kolmeya
- Teste os webhooks manualmente com `curl` (veja seção Webhooks)
- Verifique se o servidor Odoo é acessível pela internet (não localhost)
- Use ferramentas como [webhook.site](https://webhook.site) para debug
- Confira os logs de acesso do Odoo

### Problema: "Envio em massa travou"

**Soluções:**

- Envios grandes são processados em background
- Verifique o log em **SMS > Histórico > Log de SMS**
- Aguarde alguns minutos (1000 SMS pode levar 5-10 minutos)
- Se travar, reinicie o servidor Odoo e tente novamente com menos destinatários

### Problema: "Templates não substituem variáveis"

**Soluções:**

- Use a sintaxe correta: `{name}`, `{company}`, etc (com chaves)
- Verifique se o destinatário tem os campos preenchidos (nome, empresa)
- Teste com o botão "Preview" antes de enviar
- Confira se o template está ativo

### Problema: "SMS Agendados não enviam automaticamente"

**Soluções:**

- Verifique se o cron job está ativo em **Configurações > Técnico > Automação > Ações Agendadas**
- Procure por "Processar SMS Agendados"
- Confirme se está ativo e rodando a cada 5 minutos
- Execute manualmente para testar: botão "Executar Manualmente"

---

## Changelog

### Versão 15.0.1.0.0 (16/11/2025)

Lançamento inicial com funcionalidades completas!

**Recursos Implementados:**

**PRIORIDADE 1 - ESSENCIAL:**
- Webhooks automáticos de status (entregue/falhou/respondeu)
- Consulta automática de saldo com alertas visuais
- Sistema completo de blacklist e "Não Perturbe"

**PRIORIDADE 2 - GESTÃO:**
- Log completo de TODOS os SMS enviados
- Envio em lote (até 1000 mensagens por vez)
- Dashboard visual com estatísticas e gráficos interativos

**PRIORIDADE 3 - PRODUTIVIDADE:**
- Sistema de templates de mensagens com variáveis dinâmicas
- Agendamento de envios com cron job automatizado
- Rastreamento de links curtos (preparado para integração)
- Autenticação 2FA via SMS (estrutura pronta)

**EXTRAS:**
- Relatórios avançados por período
- Centros de custo (estrutura preparada)
- Analytics completo com métricas de conversão
- API REST para integração externa (endpoints prontos)

**Modelos Criados:**
- `chatroom.sms.api` - Configuração de APIs SMS
- `chatroom.sms.log` - Log de SMS enviados
- `chatroom.sms.template` - Templates de mensagens
- `chatroom.sms.scheduled` - SMS agendados
- `chatroom.sms.segment` - Segmentos Kolmeya
- `chatroom.sms.dashboard` - Dashboard e estatísticas
- `chatroom.sms.report` - Relatórios customizados

**Wizards:**
- `chatroom.send.bulk.sms` - Envio em massa
- `chatroom.sms.test` - Teste de SMS

**Segurança:**
- Grupos: SMS User, SMS Manager
- ACLs completas para todos os modelos
- Record rules para multi-company

**Automação:**
- Cron job: Consulta de saldo (diária)
- Cron job: Processamento de SMS agendados (5 em 5 minutos)

**Interface:**
- Dashboard com gráficos Chart.js
- Menus organizados e intuitivos
- Formulários com validações
- Botões de ação contextuais

---

## Créditos

**Desenvolvido por:**

- **Anderson Oliveira** - Desenvolvedor Principal
  - Empresa: Realcred
  - Website: [realcred.com.br](https://realcred.com.br)

- **Claude AI (Anthropic)** - Assistente de Desenvolvimento
  - Modelo: Claude Sonnet 4.5
  - Data de desenvolvimento: 16/11/2025

**Agradecimentos Especiais:**

- Equipe Kolmeya pelo excelente API de SMS
- Comunidade Odoo pelo framework incrível
- Todos que testarem e contribuírem com feedback

---

## Suporte

Para suporte, dúvidas ou sugestões:

- **Email:** anderson@realcred.com.br
- **Issues:** Abra uma issue no repositório (se aplicável)
- **Documentação Odoo:** [odoo.com/documentation](https://www.odoo.com/documentation/15.0/)
- **Documentação Kolmeya:** Consulte o portal da Kolmeya

---

## Licença

Este módulo é licenciado sob **LGPL-3** (GNU Lesser General Public License v3.0).

Você é livre para:
- Usar comercialmente
- Modificar
- Distribuir
- Usar em projetos privados

Sob as condições:
- Divulgar a fonte
- Usar a mesma licença
- Indicar mudanças

**Aviso Legal:**
Este software é fornecido "como está", sem garantias de qualquer tipo. Use por sua conta e risco.

---

## Roadmap Futuro

Possíveis melhorias para versões futuras:

- Integração com WhatsApp Business API
- Suporte para MMS (mensagens multimídia)
- Chatbot automatizado com IA
- Integração com Twilio, AWS SNS, Firebase
- Envio de SMS a partir de workflows automatizados
- Respostas automáticas baseadas em palavras-chave
- Surveys e pesquisas via SMS
- Integração com Google Analytics 4
- App mobile para envio rápido
- Suporte para RCS (Rich Communication Services)

**Contribuições são bem-vindas!**

---

**Feito com dedicação para a comunidade Odoo!**

Se este módulo foi útil para você, considere deixar uma estrela ou compartilhar com outros desenvolvedores Odoo.

---

**Última atualização:** 16/11/2025
**Versão do README:** 1.0.0
