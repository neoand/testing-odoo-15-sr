# 🚀 Como Usar CC-10x no Cursor/Claude Code

## ✅ Configuração Atual

Você já tem **duas configurações** prontas:

1. **`.vscode/settings.json`** - Configuração do projeto (já configurada!)
2. **`~/.ccm_config`** - Configuração do CC-10x (já configurada!)

## 📖 Formas de Usar

### OPÇÃO 1: Configuração Automática (Recomendada) ⭐

**As configurações em `.vscode/settings.json` já estão prontas!**

1. **Reinicie o Cursor** para carregar as novas configurações
2. **Abra o Claude Code** normalmente (Cmd+Shift+P → "Claude Code")
3. **Pronto!** O Claude Code usará automaticamente:
   - Base URL: `https://api.z.ai/api/anthropic`
   - Token: Configurado
   - Modelos: `glm-4.6` (Sonnet/Opus), `glm-4.5-air` (Haiku)

**Vantagem:** Funciona automaticamente, sem comandos adicionais!

---

### OPÇÃO 2: Via Terminal do Cursor (Alternativa)

Se a Opção 1 não funcionar, use o terminal:

1. **Abra o terminal no Cursor:**
   - `Ctrl + \`` (backtick) ou
   - Menu: `Terminal > New Terminal`
   - **IMPORTANTE:** Use terminal **zsh** ou **bash**, não PowerShell!

2. **Execute o comando:**
   ```bash
   ccm glm
   ```

3. **Abra o Claude Code:**
   - `Cmd+Shift+P` → "Claude Code"
   - Ou use o ícone do Claude Code na barra lateral

**Vantagem:** Permite alternar entre modelos facilmente!

---

### OPÇÃO 3: Comando Único (Mais Rápido)

Use `ccc` para alternar modelo E iniciar Claude Code:

1. **Terminal do Cursor (zsh/bash):**
   ```bash
   ccc glm
   ```

2. **Pronto!** O Claude Code abre automaticamente com GLM configurado.

---

## 🔍 Verificar se Está Funcionando

### No Terminal (zsh/bash):
```bash
# Ver configuração atual
ccm status

# Deve mostrar:
# BASE_URL: https://api.z.ai/api/anthropic
# MODEL: glm-4.6
```

### No Claude Code:
- Abra o Claude Code
- Verifique se está usando os modelos GLM
- As respostas devem vir da API z.ai

---

## 🎯 Alternar Entre Modelos

Se quiser usar outros modelos:

```bash
# No terminal do Cursor (zsh/bash):
ccm deepseek    # DeepSeek
ccm kimi        # KIMI
ccm qwen        # Qwen
ccm claude      # Claude Sonnet (oficial)
ccm opus        # Claude Opus (oficial)

# Depois abra Claude Code normalmente
```

---

## ⚙️ Configurações Atuais

### Variáveis Configuradas:
- `ANTHROPIC_BASE_URL`: `https://api.z.ai/api/anthropic`
- `ANTHROPIC_AUTH_TOKEN`: `bb42e0b593324786be8fb989ce839b2c.eHkqUUIiaVj3K9IV`
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`: `glm-4.5-air`
- `ANTHROPIC_DEFAULT_SONNET_MODEL`: `glm-4.6`
- `ANTHROPIC_DEFAULT_OPUS_MODEL`: `glm-4.6`

### Arquivos de Configuração:
- **Projeto:** `.vscode/settings.json`
- **CC-10x:** `~/.ccm_config`

---

## 🐛 Troubleshooting

### Problema: Claude Code não está usando z.ai

**Solução 1:** Reinicie o Cursor completamente

**Solução 2:** Use o terminal (zsh/bash):
```bash
ccm glm
# Depois abra Claude Code
```

**Solução 3:** Verifique as configurações:
```bash
ccm status
```

### Problema: Comando `ccm` não encontrado

**Solução:**
```bash
source ~/.zshrc
# Ou abra um novo terminal zsh/bash
```

### Problema: Terminal está em PowerShell

**Solução:** No Cursor, configure o terminal padrão para zsh:
1. `Cmd+,` (Settings)
2. Busque: "terminal integrated shell"
3. Configure para: `/bin/zsh`

---

## 📝 Notas Importantes

1. **Configuração do Projeto** (`.vscode/settings.json`):
   - Carregada automaticamente quando você abre o projeto
   - Funciona para toda a sessão do Cursor

2. **CC-10x** (`ccm`/`ccc`):
   - Permite alternar modelos facilmente
   - Útil quando você quer testar diferentes modelos
   - **Funciona apenas em zsh/bash**, não PowerShell!

3. **Ambos funcionam juntos:**
   - As configurações do projeto têm prioridade
   - CC-10x permite override via terminal

---

## ✨ Resumo Rápido

**Para usar GLM no Cursor:**

1. **Mais simples:** Apenas reinicie o Cursor (configuração já está pronta!)
2. **Alternativa:** Terminal (zsh/bash) → `ccm glm` → Abrir Claude Code
3. **Mais rápido:** Terminal (zsh/bash) → `ccc glm` (faz tudo de uma vez)

**Pronto!** 🎉




