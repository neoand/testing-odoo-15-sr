# ✅ Instruções: Como Adicionar Variáveis Customizadas

> **Data:** 2025-11-20
> **Feature:** Adicionar campos customizados como variáveis no template SMS

---

## 🎯 Objetivo

Permitir que o usuário adicione variáveis personalizadas além das pré-definidas, para usar campos específicos do seu negócio.

---

## 📋 Como Adicionar Variáveis Customizadas

### Passo a Passo:

1. **Acesse o Template**
   - Vá em **SMS → Templates**
   - Crie um novo template ou edite um existente

2. **Vá para a Aba "Variables"**
   - No formulário do template, clique na aba **"Variables"** (ao lado de "Message Content")

3. **Adicione uma Nova Variável**
   - Clique em **"Adicionar uma linha"**
   - Preencha os campos:
     - **Nome da Variável:** Ex: `contract_number`, `installment_value`, `bank_name`
       - ⚠️ **Importante:** Use apenas letras, números e underscores (_)
       - ❌ Não use: espaços, caracteres especiais, chaves `{{}}`
       - ✅ Exemplos válidos: `contract_number`, `valor_parcela`, `data_vencimento`
     - **Valor Padrão:** (opcional) Valor usado se não fornecido ao enviar
     - **Obrigatória:** Marque se a variável é obrigatória
     - **Descrição:** Explique o que a variável representa

4. **Use no Template**
   - Volte para a aba **"Message Content"**
   - Use a variável com o formato: `{{nome_da_variavel}}`
   - Exemplo: `{{contract_number}}`, `{{installment_value}}`

---

## 📝 Exemplos de Variáveis Customizadas

### Exemplo 1: Contrato
```
Nome: contract_number
Valor Padrão: (deixe vazio)
Obrigatória: ✓ Sim
Descrição: Número do contrato do cliente
```

**Uso no template:**
```
Olá {{name}}, seu contrato {{contract_number}} tem uma parcela vencendo.
```

### Exemplo 2: Valor da Parcela
```
Nome: installment_value
Valor Padrão: R$ 0,00
Obrigatória: ✓ Sim
Descrição: Valor da parcela a ser paga
```

**Uso no template:**
```
Sua parcela de {{installment_value}} vence em {{due_date}}.
```

### Exemplo 3: Nome do Banco
```
Nome: bank_name
Valor Padrão: Banco Padrão
Obrigatória: ✗ Não
Descrição: Nome do banco onde será feito o débito
```

**Uso no template:**
```
O débito será realizado no {{bank_name}}.
```

---

## 🔧 Regras e Validações

### ✅ Nome da Variável:
- Deve conter apenas: **letras, números e underscores (_)**
- Não pode conter: espaços, caracteres especiais, chaves `{{}}`
- Exemplos válidos:
  - ✅ `contract_number`
  - ✅ `valor_parcela`
  - ✅ `data_vencimento`
  - ✅ `account_123`
- Exemplos inválidos:
  - ❌ `contract number` (espaço)
  - ❌ `contract-number` (hífen)
  - ❌ `{{contract_number}}` (chaves)
  - ❌ `contract@number` (caractere especial)

### 📋 Valor Padrão:
- **Opcional:** Pode ser deixado em branco
- Será usado se o valor não for fornecido ao enviar o SMS
- Útil para valores que raramente mudam

### ⚠️ Obrigatória:
- Se marcada, o sistema garantirá que o valor seja fornecido
- Se não marcada, usará o valor padrão ou deixará vazio

---

## 💡 Dicas de Uso

1. **Nomes Descritivos:**
   - Use nomes claros: `contract_number` ao invés de `cn`
   - Facilita a manutenção e entendimento

2. **Documentação:**
   - Sempre preencha a **Descrição** para documentar o que a variável representa
   - Facilita para outros usuários entenderem

3. **Valores Padrão:**
   - Use valores padrão para variáveis que raramente mudam
   - Ex: `bank_name` = "Banco Padrão"

4. **Teste o Template:**
   - Use o botão **"Preview"** para testar o template
   - Verifique se todas as variáveis estão sendo substituídas corretamente

---

## 🎨 Interface Melhorada

A interface agora inclui:

- ✅ **Instruções visuais** na aba "Message Content"
- ✅ **Guia passo a passo** na aba "Variables"
- ✅ **Exemplos práticos** de variáveis customizadas
- ✅ **Alertas informativos** sobre regras e validações
- ✅ **Placeholders** nos campos para orientar o preenchimento

---

## 📸 O que o usuário verá:

### Aba "Message Content":
- Lista de variáveis pré-definidas
- Instruções sobre como adicionar variáveis customizadas
- Exemplo de template com variáveis customizadas

### Aba "Variables":
- Alert informativo com instruções passo a passo
- Exemplos de variáveis customizadas
- Tabela para gerenciar variáveis
- Formulário detalhado para cada variável

---

**Status:** ✅ **Interface melhorada e documentada**

