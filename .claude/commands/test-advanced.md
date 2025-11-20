# test-advanced - Testar Recursos Avançados do Claude Code

## Descrição

Testa e valida todas as funcionalidades avançadas implementadas no ambiente .claude:

- MCP server Odoo (PostgreSQL)
- Hooks de segurança e validação
- Hierarchical RAG System
- Settings avançado
- Performance e caching

## Uso

```
/test-advanced
```

## Implementação

Quando executado, Claude deverá:

### 1. Testar MCP Server Odoo
```bash
# Listar modelos do Odoo
echo '{"method":"odoo.list_models","params":{}}' | python3.11 .claude/scripts/python/odoo_mcp_server.py

# Buscar campos do modelo res.partner
echo '{"method":"odoo.model_fields","params":{"model":"res.partner"}}' | python3.11 .claude/scripts/python/odoo_mcp_server.py

# Listar módulos instalados
echo '{"method":"odoo.list_modules","params":{}}' | python3.11 .claude/scripts/python/odoo_mcp_server.py
```

### 2. Testar Hierarchical RAG
```bash
python3.11 .claude/scripts/python/hierarchical_rag.py
```

### 3. Testar Hooks
```bash
# Testar hook de segurança
.claude/hooks/security-check.sh "Bash" "rm -rf /tmp/test"

# Testar hook pré-tool
.claude/hooks/pre-tool-use.sh "Bash" "ls -la"

# Testar hook pós-resposta
.claude/hooks/post-response.sh
```

### 4. Verificar Configurações
```bash
# Validar settings.json
cat .claude/settings.json | python3.11 -m json.tool

# Validar MCP configuration
cat .mcp.json | python3.11 -m json.tool
```

### 5. Testar Performance
```bash
# Testar tempo de resposta do MCP server
time echo '{"method":"odoo.list_models","params":{}}' | python3.11 .claude/scripts/python/odoo_mcp_server.py > /dev/null

# Testar cache do RAG
python3.11 -c "
from hierarchical_rag import HierarchicalRAG
rag = HierarchicalRAG()
results1 = rag.search('test query')
results2 = rag.search('test query')  # Deve usar cache
print(f'Cache funcionando: {len(rag.query_cache)} queries em cache')
"
```

## Resultados Esperados

### ✅ MCP Server Odoo
- Conexão PostgreSQL bem-sucedida
- Listagem de modelos funcionando
- Campos de modelos retornados corretamente
- Módulos listados com informações

### ✅ Hierarchical RAG
- Coleções criadas/carregadas
- Busca retornando resultados relevantes
- Reranking funcionando
- Cache de queries operacional

### ✅ Hooks
- Validações de segurança aplicadas
- Logs de uso de ferramentas
- Sugestões pós-resposta geradas

### ✅ Configurações
- Settings.json válido e completo
- MCP servers configurados
- Permissões definidas

## Troubleshooting

### MCP Server não conecta
1. Verificar configuração do PostgreSQL
2. Validar credenciais no .mcp.json
3. Verificar se database está acessível

### RAG não funciona
1. Verificar se ChromaDB está instalado
2. Validar caminho do vector DB
3. Verificar permissões dos arquivos

### Hooks não executam
1. Verificar permissões dos scripts (.sh)
2. Validar caminho no settings.json
3. Verificar logs em .claude/logs/

## Performance Metrics

- **MCP Response Time**: < 500ms para queries simples
- **RAG Search Time**: < 1s para busca completa
- **Hook Execution**: < 100ms para validações
- **Cache Hit Rate**: > 80% para queries repetidas