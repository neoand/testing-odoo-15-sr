# 🚀 Guia Rápido - Trabalhando com Claude

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Primeira Conversa
```
Você: "Analise o módulo chatroom_sms_advanced"
Claude: [Usa /analyze automaticamente, explora código, retorna insights]
```

### 2️⃣ Implementar Feature
```
Você: "Adicione campo 'priority' no modelo crm.lead"
Claude: [Planeja, mostra o que vai fazer, aguarda OK]
Você: "Pode fazer"
Claude: [Implementa, testa, mostra resultado]
```

### 3️⃣ Corrigir Bug
```
Você: "Usuários não conseguem criar contatos"
Claude: [Debug automático, identifica causa, propõe solução]
```

## 📋 Comandos Principais

| Comando | Uso | Exemplo |
|---------|-----|---------|
| `/odoo-module` | Criar módulo novo | `/odoo-module` |
| `/odoo-model` | Criar modelo | `/odoo-model` |
| `/odoo-security` | Analisar permissões | `/odoo-security` |
| `/analyze` | Analisar código | `/analyze` |
| `/debug` | Debugar problema | `/debug` |
| `/refactor` | Refatorar código | `/refactor` |
| `/review` | Code review | `/review` |
| `/odoo-test` | Testes | `/odoo-test` |

## 💬 Exemplos de Conversas Efetivas

### ✅ BOM - Direto ao ponto
```
"Crie modelo de rating para o CRM"
"Corrija erro de permissão em res.partner"
"Refatore views do módulo SMS"
"Adicione validação de telefone"
```

### ❌ EVITE - Muito detalhado
```
"Primeiro leia o arquivo X, depois Y, então crie Z..."
"Você pode por favor analisar..."
"Será que você conseguiria..."
```

### 🎯 ÓTIMO - Delegação completa
```
"Otimize o módulo chatroom_sms_advanced"
"Implemente sistema de tags no CRM"
"Corrija todos os problemas de segurança"
```

## 🎨 Níveis de Autonomia

### Nível 1: Tarefa Específica (eu executo direto)
- "Adicione campo X no modelo Y"
- "Crie view tree para modelo Z"
- "Corrija permissão do grupo vendedor"

### Nível 2: Feature Completa (eu planejo + executo)
- "Adicione sistema de notificações"
- "Implemente filtros avançados no CRM"
- "Crie wizard de importação"

### Nível 3: Projeto Completo (eu arquiteto + implemento)
- "Melhore performance do módulo SMS"
- "Refatore toda estrutura de permissões"
- "Adicione testes automatizados"

## 🔧 Casos de Uso Comuns

### 🐛 Debugar Erro
```
Você: "Está dando erro ao criar oportunidade"
      [Cole o traceback se tiver]

Claude: ✅ Analiso o erro
        ✅ Busco código relacionado
        ✅ Identifico causa raiz
        ✅ Proponho solução
        ✅ Implemento se autorizar
```

### 🎯 Nova Feature
```
Você: "Preciso de campo 'data_visita' no CRM"

Claude: ✅ Adiciono campo no modelo
        ✅ Adiciono na view form
        ✅ Adiciono na view tree
        ✅ Adiciono tracking
        ✅ Testo que funciona
        ✅ Documento mudança
```

### 🔍 Análise de Código
```
Você: "Analise segurança do módulo SMS"

Claude: ✅ Escaneio todo código
        ✅ Verifico permissões
        ✅ Identifico vulnerabilidades
        ✅ Sugiro melhorias
        ✅ Priorizo correções
```

### 🔄 Refatoração
```
Você: "Refatore models.py do chatroom"

Claude: ✅ Analiso código atual
        ✅ Identifico melhorias
        ✅ Planejo refatoração
        ✅ Executo mudanças
        ✅ Valido funcionamento
        ✅ Documento mudanças
```

## 🎯 Dicas Pro

### 1. Confie na Autonomia
**❌ Não:** "Leia arquivo X, depois Y, depois crie Z..."
**✅ Sim:** "Crie funcionalidade de rating no CRM"

### 2. Seja Direto
**❌ Não:** "Você poderia por favor talvez..."
**✅ Sim:** "Adicione validação de email"

### 3. Delegue Complexidade
**❌ Não:** "Me explique como fazer X"
**✅ Sim:** "Faça X" (eu sei como fazer!)

### 4. Aprove Quando Fizer Sentido
**❌ Não:** Micromanage cada linha
**✅ Sim:** "Ok" / "Pode fazer" / "Aprovado"

### 5. Use Comandos
**❌ Não:** "Você poderia analisar o código?"
**✅ Sim:** `/analyze` (mais rápido!)

## 📊 Workflow Ideal

```mermaid
Você diz O QUE precisa
           ↓
Claude analisa e planeja COMO
           ↓
Claude mostra plano
           ↓
Você aprova (ou ajusta)
           ↓
Claude implementa
           ↓
Claude testa e valida
           ↓
Claude mostra resultado
           ↓
Você revisa e aprova
           ↓
✅ Pronto!
```

## 🚦 Sinais de Uso Efetivo

### ✅ Você está usando bem quando:
- Claude faz múltiplas tarefas sem precisar perguntar
- Você diz O QUE, não COMO
- Código aparece pronto e funcionando
- Documentação fica atualizada sozinha
- Você foca em produto, não em implementação

### ⚠️ Você pode melhorar se:
- Está explicando sintaxe Python/Odoo
- Está dizendo qual arquivo abrir
- Está micromanageando cada passo
- Claude fica perguntando muitos detalhes
- Você faz o que Claude poderia fazer

## 🎓 Exemplos Reais do Projeto

### Cenário 1: Permissões CRM
```
Você: "Vendedores estão vendo oportunidades de outros"

Claude: Vou analisar as permissões do CRM...
        [Usa /odoo-security]
        [Identifica record rules faltando]
        [Propõe correção SQL]

Você: "Pode aplicar"

Claude: [Aplica correção]
        [Testa com diferentes usuários]
        [Documenta mudança]
        ✅ Pronto! Vendedores agora veem apenas suas oportunidades.
```

### Cenário 2: Módulo SMS
```
Você: "Melhore o código do chatroom_sms_advanced"

Claude: Vou analisar o módulo...
        [Lê todo código]
        [Identifica: código duplicado, falta documentação,
         queries N+1, estrutura confusa]

        Encontrei 5 áreas de melhoria:
        1. Refatorar método send_sms (duplicação)
        2. Adicionar índices no banco
        3. Documentar API Kolmeya
        4. Otimizar queries
        5. Adicionar testes

        Prioridade sugerida: 4, 1, 2, 3, 5
        Posso começar?

Você: "Sim, faça as 3 primeiras"

Claude: [Implementa cada uma]
        [Testa]
        [Documenta]
        ✅ Concluído! Performance melhorou 40%.
```

### Cenário 3: Nova Feature
```
Você: "Preciso de campo 'origem_lead' no CRM com opções:
       WhatsApp, Telefone, Email, Site"

Claude: [Sem perguntar nada, implementa:]
        ✅ Campo Selection em crm.lead
        ✅ View form atualizada
        ✅ View tree atualizada
        ✅ Filtro no search
        ✅ Tracking ativado
        ✅ Tradução pt_BR

        Pronto! Quer que eu adicione também:
        - Relatório por origem?
        - Dashboard com gráfico?

Você: "Sim, os dois"

Claude: [Implementa]
        ✅ Feito!
```

## 🎯 Próximo Passo

**Experimente agora:**

1. Digite: `/analyze` e veja a mágica acontecer
2. Ou: "Analise o módulo chatroom_sms_advanced"
3. Ou: "Me mostre o que precisa melhorar no projeto"

**Lembre-se:** Eu sou seu engenheiro sênior. Use-me como tal! 💪

---

**Dúvidas?** Apenas pergunte! Estou aqui para trabalhar. 🚀
