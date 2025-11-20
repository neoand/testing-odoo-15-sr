---
description: Refatorar código mantendo funcionalidade e melhorando qualidade
---

# Refatoração de Código

Melhorar a estrutura do código sem alterar seu comportamento externo, seguindo padrões e best practices.

## Objetivos da Refatoração

- **Melhorar legibilidade:** Código mais fácil de entender
- **Reduzir complexidade:** Simplificar lógica complexa
- **Eliminar duplicação:** Aplicar princípio DRY
- **Seguir padrões:** Conformidade com padrões da linguagem/framework
- **Facilitar manutenção:** Código mais fácil de modificar

## Processo de Refatoração

### 1. Análise Inicial
- **Entender o código:** O que ele faz? Por que existe?
- **Identificar code smells:** Padrões de código problemáticos
- **Mapear dependências:** O que depende deste código?
- **Avaliar testes:** Testes existentes são suficientes?

### 2. Planejamento
- **Priorizar mudanças:** Impacto vs. esforço
- **Definir escopo:** O que refatorar agora vs. depois
- **Preparar testes:** Garantir cobertura antes de mudar
- **Criar backup:** Poder voltar ao estado original

### 3. Execução Incremental
- **Mudanças pequenas:** Uma refatoração de cada vez
- **Testes constantes:** Após cada mudança
- **Commit frequente:** Mudanças testadas são commitadas
- **Validação funcional:** Comportamento permanece o mesmo

### 4. Validação Final
- **Testes completos:** Suite de testes passa
- **Performance:** Não degradou significativamente
- **Revisão:** Code review por colega
- **Documentação:** Atualizar se necessário

## Code Smells Comuns

### 1. Long Method
```python
# ❌ RUIM - Método muito longo
def process_order(self, order):
    # 100+ linhas de lógica
    validate_customer(order.customer)
    check_inventory(order.items)
    calculate_taxes(order)
    apply_discounts(order)
    process_payment(order)
    send_confirmation(order)
    update_inventory(order)
    create_invoice(order)

# ✅ BOM - Extraídos métodos
def process_order(self, order):
    self._validate_customer(order.customer)
    self._check_inventory(order.items)
    self._calculate_taxes(order)
    self._apply_discounts(order)
    self._process_payment(order)
    self._send_confirmation(order)
    self._update_inventory(order)
    self._create_invoice(order)
```

### 2. Duplicate Code
```python
# ❌ RUIM - Código duplicado
def calculate_discount_a(self, price, category):
    if category == "premium":
        return price * 0.9
    elif category == "gold":
        return price * 0.8
    return price

def calculate_discount_b(self, price, category):
    if category == "premium":
        return price * 0.9
    elif category == "gold":
        return price * 0.8
    return price

# ✅ BOM - Extraído método comum
def calculate_discount(self, price, category):
    discount_map = {
        "premium": 0.9,
        "gold": 0.8
    }
    return price * discount_map.get(category, 1.0)
```

### 3. Large Class
```python
# ❌ RUIM - Classe com muitas responsabilidades
class UserManager:
    def create_user(self, data): pass
    def update_user(self, id, data): pass
    def delete_user(self, id): pass
    def send_email(self, user, message): pass
    def validate_password(self, password): pass
    def hash_password(self, password): pass
    def generate_token(self, user): pass
    def log_activity(self, user, action): pass

# ✅ BOM - Responsabilidades separadas
class UserRepository:
    def create(self, data): pass
    def update(self, id, data): pass
    def delete(self, id): pass

class EmailService:
    def send(self, user, message): pass

class AuthService:
    def validate_password(self, password): pass
    def hash_password(self, password): pass
    def generate_token(self, user): pass

class ActivityLogger:
    def log(self, user, action): pass
```

### 4. Magic Numbers
```python
# ❌ RUIM - Números mágicos
def calculate_shipping_cost(self, weight):
    if weight < 5:
        return 10
    elif weight < 20:
        return 15
    else:
        return 25

# ✅ BOM - Constantes nomeadas
class ShippingConfig:
    LIGHT_WEIGHT_LIMIT = 5
    MEDIUM_WEIGHT_LIMIT = 20
    LIGHT_COST = 10
    MEDIUM_COST = 15
    HEAVY_COST = 25

def calculate_shipping_cost(self, weight):
    if weight < ShippingConfig.LIGHT_WEIGHT_LIMIT:
        return ShippingConfig.LIGHT_COST
    elif weight < ShippingConfig.MEDIUM_WEIGHT_LIMIT:
        return ShippingConfig.MEDIUM_COST
    else:
        return ShippingConfig.HEAVY_COST
```

## Técnicas de Refatoração

### 1. Extract Method
**Quando:** Método longo ou complexo
**Como:** Extrair parte do código para novo método com nome descritivo

```python
# Antes
def process_payment(self, order):
    # Validar cartão
    if len(order.card_number) != 16:
        raise ValueError("Invalid card number")
    if not self._validate_luhn(order.card_number):
        raise ValueError("Invalid card checksum")

    # Processar pagamento
    amount = order.total * 1.05  # + taxa
    response = self.gateway.charge(order.card_number, amount)

    # Registrar transação
    transaction = Transaction(
        order_id=order.id,
        amount=amount,
        status=response.status
    )
    transaction.save()

# Depois
def process_payment(self, order):
    self._validate_payment_method(order)
    amount = self._calculate_amount_with_fee(order)
    response = self._charge_card(order, amount)
    self._create_transaction(order, amount, response)

def _validate_payment_method(self, order):
    if len(order.card_number) != 16:
        raise ValueError("Invalid card number")
    if not self._validate_luhn(order.card_number):
        raise ValueError("Invalid card checksum")
```

### 2. Rename Variable
**Quando:** Nome não descritivo ou confuso
**Como:** Renomear para nome claro e significativo

```python
# Antes
def calc(self, d1, d2, x):
    r = d1 - d2
    if r > 0:
        return x * 0.1
    return 0

# Depois
def calculate_commission(self, deadline_date, delivery_date, amount):
    days_overdue = (deadline_date - delivery_date).days
    if days_overdue > 0:
        return amount * 0.1
    return 0
```

### 3. Replace Conditional with Polymorphism
**Quando:** Múltiplos if/else baseados em tipo
**Como:** Usar polimorfismo e herança

```python
# Antes
class NotificationService:
    def send(self, message, channel, recipient):
        if channel == "email":
            self._send_email(message, recipient)
        elif channel == "sms":
            self._send_sms(message, recipient)
        elif channel == "push":
            self._send_push(message, recipient)

# Depois
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    @abstractmethod
    def send(self, message, recipient):
        pass

class EmailChannel(NotificationChannel):
    def send(self, message, recipient):
        # Implementação email
        pass

class SMSChannel(NotificationChannel):
    def send(self, message, recipient):
        # Implementação SMS
        pass

class PushChannel(NotificationChannel):
    def send(self, message, recipient):
        # Implementação push
        pass

class NotificationService:
    def __init__(self):
        self.channels = {
            "email": EmailChannel(),
            "sms": SMSChannel(),
            "push": PushChannel()
        }

    def send(self, message, channel, recipient):
        sender = self.channels[channel]
        sender.send(message, recipient)
```

### 4. Extract Class
**Quando:** Classe com muitas responsabilidades
**Como:** Extrair responsabilidade para nova classe

```python
# Antes
class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock
        self.sales_history = []

    def add_sale(self, quantity, date):
        self.stock -= quantity
        self.sales_history.append({
            'quantity': quantity,
            'date': date,
            'price': self.price
        })

    def get_monthly_sales(self, month, year):
        return [s for s in self.sales_history
                if s['date'].month == month and s['date'].year == year]

# Depois
class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock
        self.sales_tracker = SalesTracker()

    def add_sale(self, quantity, date):
        self.stock -= quantity
        self.sales_tracker.record_sale(quantity, date, self.price)

    def get_monthly_sales(self, month, year):
        return self.sales_tracker.get_monthly_sales(month, year)

class SalesTracker:
    def __init__(self):
        self.sales_history = []

    def record_sale(self, quantity, date, price):
        self.sales_history.append({
            'quantity': quantity,
            'date': date,
            'price': price
        })

    def get_monthly_sales(self, month, year):
        return [s for s in self.sales_history
                if s['date'].month == month and s['date'].year == year]
```

## Segurança na Refatoração

### Antes de Começar
1. **Backup completo:** Código e dados
2. **Testes verdes:** Suite de testes passando
3. **Branch isolado:** Não refatorar em branch principal
4. **Tempo estimado:** Não subestimar complexidade

### Durante Refatoração
1. **Mudanças pequenas:** Uma técnica de cada vez
2. **Testes frequentes:** Após cada mudança
3. **Commits atômicos:** Mudanças testadas são commitadas
4. **Rollback fácil:** Poder voltar facilmente

### Após Refatoração
1. **Testes completos:** Suite inteira passando
2. **Performance:** Não degradou significativamente
3. **Code review:** Por outro desenvolvedor
4. **Documentação:** Atualizar documentação afetada

## Checklist de Refatoração

### Análise
- [ ] Código está claro e compreendido?
- [ ] Code smells identificados?
- [ ] Dependências mapeadas?
- [ ] Testes existem e cobrem o código?

### Planejamento
- [ ] Prioridades definidas?
- [ ] Escopo claro estabelecido?
- [ ] Testes preparados/criados?
- [ ] Backup feito?

### Execução
- [ ] Mudanças incrementais?
- [ ] Testes executados após cada mudança?
- [ ] Commits atômicos e descritivos?
- [ ] Funcionalidade mantida?

### Validação
- [ ] Todos os testes passam?
- [ ] Performance aceitável?
- [ ] Code review realizado?
- [ ] Documentação atualizada?

## Ferramentas Úteis

### Linters e Static Analysis
```bash
# Python
flake8 --max-line-length=120 .
black --line-length 120 .
isort .
pylint src/

# JavaScript
eslint src/
prettier --write src/
```

### IDE Features
- **Rename symbol:** Refatoração segura de variáveis/funções
- **Extract method:** Auto-extração de métodos
- **Find usages:** Verificar onde símbolo é usado
- **Safe delete:** Remover código não utilizado

### Test Coverage
```bash
# Python
coverage run -m pytest
coverage report
coverage html

# Verificar cobertura específica
coverage report --include=src/module/*
```

## Métricas de Qualidade

### Complexidade Ciclomática
- **Boa:** < 10 por método
- **Aceitável:** 10-20
- **Ruim:** > 20

### Tamanho de Método
- **Boa:** < 20 linhas
- **Aceitável:** 20-50
- **Ruim:** > 50

### Acoplamento
- **Baixo:** Classes independentes
- **Médio:** Algumas dependências
- **Alto:** Muitas dependências

### Coesão
- **Alta:** Métodos relacionados à classe
- **Média:** Alguns métodos não relacionados
- **Baixa:** Métodos não relacionados

## Padrões de Nomenclatura

### Python (PEP 8)
- **Classes:** PascalCase (`MyClass`)
- **Funções/Métodos:** snake_case (`my_function`)
- **Constantes:** UPPER_CASE (`MY_CONSTANT`)
- **Privado:** `_underscore_prefix`
- **Muito privado:** `__dunder__`

### JavaScript
- **Classes/Constructors:** PascalCase (`MyClass`)
- **Funções/Variáveis:** camelCase (`myFunction`)
- **Constantes:** UPPER_SNAKE_CASE (`MY_CONSTANT`)
- **Private:** `_underscorePrefix`

## Documentação de Refatoração

Para cada refatoração significativa, documentar:
```markdown
### Refatoração: [Data] - [Componente]

**Objetivo:** [Por que a refatoração foi necessária]
**Problemas:** [Code smells identificados]
**Solução:** [Técnicas aplicadas]
**Impacto:** [Mudanças no comportamento externo (nenhum)]
**Performance:** [Impacto na performance]
**Testes:** [Como foram afetados/criados]
```

## Melhores Práticas Finais

1. **Refatorar constantemente:** Não deixar acumular
2. **Testes primeiro:** Garantir cobertura antes de mudar
3. **Pequenos passos:** Mudanças incrementais
4. **Comunicação:** Documentar decisões e razões
5. **Revisão:** Sempre obter segunda opinião
6. **Métricas:** Medir qualidade antes e depois
