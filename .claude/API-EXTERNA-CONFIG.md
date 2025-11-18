# 🔧 Configuração de API Externa no Cursor

## 📋 Situação Atual

Você configurou uma API externa (de outra empresa) porque seu limite no Claude acabou, mas a opção de seleção ainda não aparece no Cursor.

## 🔍 Verificação Realizada

✅ **Arquivos verificados:**
- `.claude/settings.json` - Apenas hooks configurados
- `.claude/hooks.yaml` - Apenas hooks de automação
- Nenhum arquivo de configuração de API encontrado na pasta `.claude/`

## 🎯 Como Configurar API Externa no Cursor

### Método 1: Interface do Cursor (Recomendado)

1. **Abrir Configurações:**
   - Pressione `Cmd + ,` (Mac) ou `Ctrl + ,` (Windows/Linux)
   - Ou: `Cursor` → `Settings` → `Settings`

2. **Buscar por "API" ou "Claude":**
   - Na barra de busca, digite: `claude api` ou `anthropic`
   - Procure por opções como:
     - `Claude API Key`
     - `Anthropic API Key`
     - `Custom API Provider`
     - `Model Provider`

3. **Configurar API Externa:**
   - Se houver opção "Custom API" ou "External Provider":
     - Adicione a URL base da API
     - Adicione a API Key fornecida pela empresa
     - Configure o modelo (ex: `claude-3-5-sonnet-20241022`)

### Método 2: Arquivo de Configuração Manual

O Cursor pode usar configurações em:

**macOS:**
```
~/Library/Application Support/Cursor/User/settings.json
```

**Windows:**
```
%APPDATA%\Cursor\User\settings.json
```

**Linux:**
```
~/.config/Cursor/User/settings.json
```

#### Exemplo de configuração:

```json
{
  "claude.apiKey": "sua-api-key-aqui",
  "claude.apiUrl": "https://api.exemplo.com/v1",
  "claude.model": "claude-3-5-sonnet-20241022",
  "claude.provider": "custom"
}
```

### Método 3: Variáveis de Ambiente

Você pode configurar via variáveis de ambiente:

```bash
export ANTHROPIC_API_KEY="sua-api-key-aqui"
export ANTHROPIC_API_URL="https://api.exemplo.com/v1"
```

## 🚨 Problemas Comuns

### 1. Opção não aparece no menu

**Possíveis causas:**
- Versão do Cursor desatualizada
- API externa não suporta o formato esperado pelo Cursor
- Configuração precisa ser feita via arquivo JSON

**Solução:**
- Atualize o Cursor para a versão mais recente
- Verifique se a API externa é compatível com a API do Anthropic
- Configure manualmente via `settings.json`

### 2. API Key não funciona

**Verificar:**
- A API Key está correta?
- A API Key tem permissões adequadas?
- O endpoint da API está acessível?
- A API externa suporta os mesmos modelos do Claude?

### 3. Erro de autenticação

**Verificar:**
- Formato do header de autenticação
- Se a API usa `Authorization: Bearer <key>` ou outro formato
- Se há rate limits ou quotas

## 📝 Checklist de Configuração

- [ ] Obter API Key da empresa externa
- [ ] Obter URL base da API
- [ ] Verificar modelo disponível (ex: `claude-3-5-sonnet`)
- [ ] Verificar formato de autenticação
- [ ] Testar conexão com a API
- [ ] Configurar no Cursor (via UI ou arquivo)
- [ ] Verificar se aparece no seletor de modelo
- [ ] Testar uma conversa para validar

## 🔗 Informações Necessárias da Empresa Externa

Para configurar corretamente, você precisa:

1. **API Key:** A chave de autenticação
2. **Base URL:** URL base da API (ex: `https://api.exemplo.com/v1`)
3. **Modelo:** Nome do modelo (ex: `claude-3-5-sonnet-20241022`)
4. **Formato de Auth:** Como enviar a autenticação (Bearer token, etc.)
5. **Endpoints:** Endpoints disponíveis (chat, completions, etc.)

## 🛠️ Próximos Passos

1. **Verificar versão do Cursor:**
   ```bash
   # No Cursor, vá em: Help → About
   ```

2. **Contatar a empresa externa:**
   - Solicitar documentação da API
   - Verificar compatibilidade com Anthropic API
   - Obter exemplos de configuração

3. **Testar API manualmente:**
   ```bash
   curl -X POST https://api.exemplo.com/v1/messages \
     -H "Authorization: Bearer sua-api-key" \
     -H "Content-Type: application/json" \
     -d '{"model": "claude-3-5-sonnet", "messages": [...]}'
   ```

4. **Configurar no Cursor:**
   - Via interface (se disponível)
   - Ou via arquivo `settings.json`

## 📚 Referências

- [Cursor Settings Documentation](https://cursor.sh/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference)

---

**Última atualização:** 2025-11-18
**Status:** Aguardando informações da API externa para configuração completa

