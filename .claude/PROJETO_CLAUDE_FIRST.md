# 🤖 Projeto Claude First - Odoo 15 Testing

## Visão Geral

Este projeto está configurado para **desenvolvimento colaborativo com Claude Code**, onde você (humano) atua como **Product Owner/Arquiteto** e eu (Claude) como seu **Engenheiro de Software Senior** e executor.

## 🎯 Filosofia Claude First

### Princípios
1. **Claude como Executor** - Você define "O QUE", eu implemento "COMO"
2. **Autonomia com Supervisão** - Eu trabalho de forma independente, você aprova
3. **Transparência Total** - Tudo que faço é visível e rastreável
4. **Documentação Viva** - Código e docs sempre sincronizados
5. **Qualidade por Padrão** - Best practices em cada linha

### Como Funciona
```
VOCÊ (Product Owner)          EU (Claude)
━━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━
"Precisamos de X"      →      Analiso requisitos
                             Planejo implementação
                             Mostro plano para você
                       ←      "Vou fazer assim: ..."

"Parece bom"          →      Implemento
                             Testo
                             Documento
                             Commito
                       ←      "Pronto! Review?"

"Aprovado"            →      Próxima tarefa!
```

## 🛠️ Comandos Disponíveis

Use `/` para ver todos os comandos ou digite diretamente:

### Comandos Odoo
- `/odoo-module` - Criar novo módulo completo
- `/odoo-model` - Criar modelo (classe Python)
- `/odoo-security` - Analisar permissões e segurança
- `/odoo-test` - Executar/criar testes

### Comandos Gerais
- `/analyze` - Analisar código e arquitetura
- `/debug` - Debugar problemas
- `/refactor` - Refatorar código
- `/review` - Code review detalhado

## 📁 Estrutura Claude

```
.claude/
├── commands/          # Comandos slash personalizados
├── prompts/          # Prompts reutilizáveis
├── templates/        # Templates de código
└── hooks/           # Automações (futuro)

.clauderc            # Configuração do projeto
```

## 🚀 Workflows Típicos

### 1. Nova Feature
```
Você: "Preciso adicionar funcionalidade X"
Eu: Uso /analyze para entender contexto
    Crio plano detalhado
    Mostro para você
Você: "Aprovado"
Eu: Uso TodoWrite para organizar tarefas
    Implemento passo a passo
    Testo
    Documento
    Mostro resultado
```

### 2. Bug Fix
```
Você: "Está dando erro Y"
Eu: Uso /debug
    Investigo causa raiz
    Proponho solução
Você: "Ok, pode corrigir"
Eu: Implemento fix
    Testo que funciona
    Documento o que causou
```

### 3. Refatoração
```
Você: "Esse código está confuso"
Eu: Uso /analyze para entender
    Uso /refactor para melhorar
    Mantenho funcionalidade
    Mostro antes/depois
```

## 💡 Dicas de Uso

### Para Máxima Produtividade

**❌ Evite:**
- "Leia o arquivo X" (eu faço isso automaticamente)
- Micromanagement de cada passo
- Explicar sintaxe Python/Odoo (eu já sei)

**✅ Prefira:**
- "Adicione feature X que faz Y"
- "Analise o módulo Z e sugira melhorias"
- "Corrija o bug que está causando erro W"
- "Implemente conforme documento especificacao.md"

### Delegação Efetiva

**Nível 1 - Tarefa Clara:**
```
Você: "Crie um modelo crm.custom_field com campos name e description"
Eu: [Implemento direto, sem perguntar detalhes]
```

**Nível 2 - Feature Complexa:**
```
Você: "Adicione sistema de notificações SMS no CRM"
Eu: [Analiso, planejo, mostro opções arquiteturais]
```

**Nível 3 - Autonomia Total:**
```
Você: "Refatore o módulo chatroom_sms_advanced para melhor manutenibilidade"
Eu: [Analiso, decido melhorias, implemento, documento tudo]
```

## 🎓 Capacidades Avançadas

### Exploração de Codebase
Posso navegar e entender toda a estrutura:
- Buscar arquivos por padrão
- Grep em todo código
- Analisar dependências
- Mapear arquitetura

### Desenvolvimento Full-Stack
- **Backend:** Models, controllers, business logic
- **Frontend:** Views XML, JavaScript, QWeb
- **Database:** SQL, migrations, data
- **DevOps:** Scripts, configs, deploy

### Análise e Qualidade
- Code review automático
- Detecção de vulnerabilidades
- Otimização de performance
- Sugestões de refatoração

## 📊 Gestão de Tarefas

Uso **TodoWrite** para:
- Quebrar tarefas grandes em pequenas
- Mostrar progresso em tempo real
- Garantir que nada seja esquecido
- Você acompanhar o andamento

Exemplo:
```
✅ Analisar requisitos
🔄 Criar modelo Python (em progresso)
⏳ Criar views XML
⏳ Adicionar permissões
⏳ Testar funcionalidade
⏳ Documentar
```

## 🔒 Segurança e Controle

### Você Sempre Tem Controle
- Eu **NUNCA** commito sem sua autorização
- Eu **SEMPRE** mostro o que vou fazer antes
- Você pode **PARAR** a qualquer momento
- Todo código é **REVISÁVEL**

### Práticas de Segurança
- Validação de inputs
- Sanitização de dados
- Permissões corretas
- Sem hard-coded secrets
- SQL injection prevention

## 🎯 Próximos Passos

1. **Me conte sobre o projeto:**
   - Qual funcionalidade está trabalhando?
   - Quais são as prioridades?
   - Há algo para corrigir urgente?

2. **Experimente comandos:**
   - `/analyze` no módulo principal
   - `/odoo-security` para revisar permissões
   - `/review` em código recente

3. **Defina workflows:**
   - Como prefere aprovar mudanças?
   - Quer ver plano sempre antes?
   - Nível de autonomia desejado?

## 📞 Como Pedir Ajuda

- **Dúvida técnica:** "Como funciona X no Odoo?"
- **Implementação:** "Implemente Y"
- **Análise:** "Analise Z e diga o que acha"
- **Sugestão:** "O que você melhoraria em W?"

---

**Lembre-se:** Eu sou seu engenheiro, não um assistente passivo.
Use-me para **FAZER** coisas, não apenas explicar! 🚀

**Pronto para começar?** Me diga no que está trabalhando!
