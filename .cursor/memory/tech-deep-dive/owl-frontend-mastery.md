# 🦉 OWL Frontend Framework - Mastery Guide

> **OWL (Odoo Web Library)** - Framework JavaScript reativo usado no Odoo 17+
>
> **Última atualização:** 2025-11-17
> **Versão coberta:** OWL 2.0 (Odoo 17/18)
> **Status:** ✅ Conhecimento Consolidado

---

## 📚 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura de Componentes](#arquitetura-de-componentes)
3. [Sistema de Reatividade](#sistema-de-reatividade)
4. [Lifecycle Hooks](#lifecycle-hooks)
5. [Template Engine (QWeb)](#template-engine-qweb)
6. [Props e Communication](#props-e-communication)
7. [Performance e Otimizações](#performance-e-otimizações)
8. [Integração com Odoo](#integração-com-odoo)
9. [Padrões e Best Practices](#padrões-e-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

### O Que é OWL?

OWL (Odoo Web Library) é um framework JavaScript moderno e reativo desenvolvido pela Odoo para substituir o sistema legado baseado em widgets.

**Características principais:**
- ✅ **Reativo:** Sistema de estado baseado em Proxies
- ✅ **Baseado em Classes:** Componentes como classes ES6
- ✅ **Virtual DOM:** Rendering eficiente com patches mínimos
- ✅ **QWeb Templates:** Motor de templates do Odoo
- ✅ **Hooks:** API similar ao React Hooks
- ✅ **TypeScript Ready:** Suporte completo a tipos

### Versões e Compatibilidade

| Odoo Version | OWL Version | Status |
|--------------|-------------|--------|
| Odoo 14 | OWL 1.x | Legacy |
| Odoo 15 | OWL 1.x | Legacy |
| Odoo 16 | OWL 1.x | Legacy |
| Odoo 17 | OWL 2.0 | ✅ Current |
| Odoo 18 | OWL 2.0 | ✅ Latest |

**⚠️ IMPORTANTE:** Odoo 15 (nosso projeto atual) ainda usa sistema de Widgets legado, NÃO OWL!

### Quando Usar OWL vs Widgets

**Use OWL quando:**
- ✅ Odoo 17+ (disponível nativamente)
- ✅ Componentes reativos complexos
- ✅ Estado compartilhado entre componentes
- ✅ UI altamente interativa

**Use Widgets quando:**
- ✅ Odoo 15 ou anterior (padrão)
- ✅ Manutenção de código legado
- ✅ Simplicidade suficiente

---

## 🏗️ Arquitetura de Componentes

### Estrutura Básica de um Componente

```javascript
import { Component, useState, onWillStart, onMounted } from "@odoo/owl";

class MyComponent extends Component {
    static template = "my_module.MyTemplate";

    static props = {
        title: String,
        count: { type: Number, optional: true },
    };

    setup() {
        // Estado reativo
        this.state = useState({
            items: [],
            loading: false
        });

        // Hooks de lifecycle
        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            console.log("Component mounted!");
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const data = await this.rpc('/my/endpoint');
            this.state.items = data.items;
        } finally {
            this.state.loading = false;
        }
    }

    onItemClick(item) {
        // Lógica de click
        console.log("Clicked:", item);
    }
}
```

### Anatomia de um Componente

```
Component
├── Static Properties
│   ├── template (obrigatório)
│   ├── props (validação de props)
│   └── components (subcomponentes)
│
├── setup() - Inicialização
│   ├── Estado (useState)
│   ├── Hooks (onWillStart, onMounted, etc)
│   └── Bindings de métodos
│
├── Methods
│   ├── Event handlers
│   ├── Business logic
│   └── Helper functions
│
└── Lifecycle
    ├── willStart → mounted → willUpdateProps → willPatch → patched → willUnmount
```

---

## ⚡ Sistema de Reatividade

### useState Hook

O coração da reatividade em OWL 2.0:

```javascript
import { Component, useState } from "@odoo/owl";

class Counter extends Component {
    static template = "my_module.Counter";

    setup() {
        // Estado reativo usando Proxy
        this.state = useState({
            count: 0,
            history: []
        });
    }

    increment() {
        // Modificação direta do estado
        this.state.count++;
        this.state.history.push(this.state.count);
        // Component re-renderiza automaticamente!
    }

    reset() {
        this.state.count = 0;
        this.state.history = [];
    }
}
```

**Como funciona:**
1. `useState()` cria um **Proxy** em torno do objeto
2. Quando uma propriedade muda, o Proxy detecta
3. Component é marcado para re-render
4. Virtual DOM calcula diferenças (diff)
5. Apenas mudanças são aplicadas ao DOM real

### Reatividade Profunda vs Não-Profunda

```javascript
// ❌ ATENÇÃO: Reatividade NÃO é profunda por padrão!
this.state = useState({
    user: {
        profile: {
            name: "John"  // Mudanças aqui NÃO triggam re-render!
        }
    }
});

// Solução 1: Reatribuir objeto inteiro
this.state.user = {
    ...this.state.user,
    profile: { ...this.state.user.profile, name: "Jane" }
};

// Solução 2: Usar useState para cada nível
this.state = useState({
    user: useState({
        profile: useState({
            name: "John"  // Agora SIM é reativo!
        })
    })
});

// ✅ Solução 3: Usar reactive() para reatividade profunda
import { reactive } from "@odoo/owl";

this.state = reactive({
    user: {
        profile: {
            name: "John"  // Mudanças em qualquer nível triggam re-render
        }
    }
});
```

### Computed Properties

```javascript
class ProductList extends Component {
    setup() {
        this.state = useState({
            products: [],
            filter: 'all'
        });
    }

    // Getter como computed property
    get filteredProducts() {
        if (this.state.filter === 'all') {
            return this.state.products;
        }
        return this.state.products.filter(p => p.category === this.state.filter);
    }

    get totalPrice() {
        return this.filteredProducts.reduce((sum, p) => sum + p.price, 0);
    }
}
```

**Template:**
```xml
<t t-foreach="filteredProducts" t-as="product" t-key="product.id">
    <div t-esc="product.name"/>
</t>
<div>Total: <t t-esc="totalPrice"/></div>
```

---

## 🔄 Lifecycle Hooks

### Hooks Disponíveis

```javascript
import {
    Component,
    onWillStart,    // Antes do primeiro render
    onMounted,      // Após montar no DOM
    onWillUpdateProps,  // Antes de receber novas props
    onWillPatch,    // Antes de aplicar patches ao DOM
    onPatched,      // Após aplicar patches
    onWillUnmount,  // Antes de desmontar
    onWillDestroy,  // Antes de destruir
    onError         // Captura de erros
} from "@odoo/owl";

class FullLifecycleComponent extends Component {
    setup() {
        // 1. ANTES do primeiro render
        onWillStart(async () => {
            console.log("1. onWillStart - carregando dados...");
            this.data = await this.loadInitialData();
        });

        // 2. APÓS montar no DOM (similar ao componentDidMount)
        onMounted(() => {
            console.log("2. onMounted - DOM está pronto!");
            this.setupEventListeners();
            this.focusFirstInput();
        });

        // 3. ANTES de receber novas props
        onWillUpdateProps((nextProps) => {
            console.log("3. onWillUpdateProps", nextProps);
            // Comparar props e ajustar estado se necessário
        });

        // 4. ANTES de aplicar mudanças ao DOM
        onWillPatch(() => {
            console.log("4. onWillPatch - guardando scroll position...");
            this.scrollPosition = window.scrollY;
        });

        // 5. APÓS aplicar mudanças ao DOM
        onPatched(() => {
            console.log("5. onPatched - restaurando scroll...");
            window.scrollTo(0, this.scrollPosition);
        });

        // 6. ANTES de desmontar
        onWillUnmount(() => {
            console.log("6. onWillUnmount - cleanup...");
            this.removeEventListeners();
        });

        // 7. ANTES de destruir
        onWillDestroy(() => {
            console.log("7. onWillDestroy - final cleanup...");
        });

        // 8. Captura de erros
        onError((error) => {
            console.error("Error capturado:", error);
            this.showErrorMessage(error);
        });
    }
}
```

### Ordem de Execução Completa

```
Component criado
    ↓
setup() executado
    ↓
onWillStart() → await async operations
    ↓
Primeiro render (Virtual DOM criado)
    ↓
onMounted() → DOM está pronto
    ↓
[Component ativo - recebendo eventos, mudanças de estado]
    ↓
Props mudaram? → onWillUpdateProps(nextProps)
    ↓
Estado mudou? → onWillPatch()
    ↓
Virtual DOM re-renderizado
    ↓
Patches aplicados ao DOM
    ↓
onPatched()
    ↓
[Ciclo continua...]
    ↓
Component sendo removido → onWillUnmount()
    ↓
onWillDestroy()
    ↓
Component destruído
```

### Casos de Uso Práticos

**1. Carregamento de Dados Assíncrono:**
```javascript
setup() {
    this.state = useState({ data: [], loading: true });

    onWillStart(async () => {
        this.state.data = await this.rpc('/my/data');
        this.state.loading = false;
    });
}
```

**2. Event Listeners:**
```javascript
setup() {
    this.handleResize = this.handleResize.bind(this);

    onMounted(() => {
        window.addEventListener('resize', this.handleResize);
    });

    onWillUnmount(() => {
        window.removeEventListener('resize', this.handleResize);
    });
}
```

**3. Focus Management:**
```javascript
setup() {
    onMounted(() => {
        this.el.querySelector('input').focus();
    });
}
```

**4. Scroll Restoration:**
```javascript
setup() {
    let scrollPos = 0;

    onWillPatch(() => {
        scrollPos = this.el.scrollTop;
    });

    onPatched(() => {
        this.el.scrollTop = scrollPos;
    });
}
```

---

## 📝 Template Engine (QWeb)

### QWeb Basics

```xml
<templates>
    <t t-name="my_module.MyTemplate">
        <div class="my-component">
            <!-- Interpolação de variáveis -->
            <h1 t-esc="props.title"/>

            <!-- HTML não escapado (CUIDADO: XSS risk!) -->
            <div t-raw="props.htmlContent"/>

            <!-- Atributos dinâmicos -->
            <div t-att-class="state.isActive ? 'active' : 'inactive'">
                <span t-att-style="{'color': state.color}">Texto</span>
            </div>

            <!-- Condicionais -->
            <div t-if="state.loading">
                Carregando...
            </div>
            <div t-elif="state.error">
                Erro: <t t-esc="state.error"/>
            </div>
            <div t-else="">
                <t t-esc="state.data.length"/> itens carregados
            </div>

            <!-- Loops -->
            <ul>
                <li t-foreach="state.items" t-as="item" t-key="item.id">
                    <span t-esc="item.name"/> - <span t-esc="item.price"/>
                </li>
            </ul>

            <!-- Event handlers -->
            <button t-on-click="increment">
                Cliques: <t t-esc="state.count"/>
            </button>

            <!-- Subcomponentes -->
            <t t-component="SubComponent"
               t-props="subComponentProps"/>
        </div>
    </t>
</templates>
```

### Diretivas QWeb Essenciais

#### 1. Interpolação

```xml
<!-- t-esc: Escapa HTML (SEGURO) -->
<div t-esc="state.userInput"/>  <!-- &lt;script&gt; vira texto -->

<!-- t-raw: HTML não escapado (RISCO XSS!) -->
<div t-raw="state.trustedHtml"/>  <!-- <b>Bold</b> renderiza HTML -->

<!-- t-out: Alias para t-esc (Odoo 17+) -->
<div t-out="state.value"/>
```

**⚠️ SEGURANÇA:** SEMPRE use `t-esc` para conteúdo de usuário! Use `t-raw` APENAS para HTML confiável.

#### 2. Condicionais

```xml
<!-- t-if / t-elif / t-else -->
<div t-if="state.status === 'loading'">
    Carregando...
</div>
<div t-elif="state.status === 'error'">
    Erro ao carregar
</div>
<div t-else="">
    Dados carregados!
</div>

<!-- Condicionais em atributos -->
<button t-att-disabled="state.isSubmitting ? 'disabled' : undefined">
    Enviar
</button>
```

#### 3. Loops

```xml
<!-- t-foreach básico -->
<ul>
    <li t-foreach="state.products" t-as="product" t-key="product.id">
        <t t-esc="product.name"/>
    </li>
</ul>

<!-- Acesso a índice -->
<ul>
    <li t-foreach="state.items" t-as="item" t-key="item_index">
        #<t t-esc="item_index"/> - <t t-esc="item.name"/>
    </li>
</ul>

<!-- Valores disponíveis no loop -->
<!-- item: elemento atual -->
<!-- item_index: índice (0, 1, 2...) -->
<!-- item_value: mesmo que item -->
<!-- item_first: true se primeiro -->
<!-- item_last: true se último -->

<ul>
    <li t-foreach="state.users" t-as="user" t-key="user.id">
        <span t-if="user_first">👑</span>
        <t t-esc="user.name"/>
        <span t-if="user_last">🏁</span>
    </li>
</ul>
```

**⚠️ PERFORMANCE:** SEMPRE use `t-key` em loops para otimizar Virtual DOM!

#### 4. Event Handlers

```xml
<!-- Click events -->
<button t-on-click="handleClick">Click me</button>

<!-- Com parâmetros -->
<button t-on-click="() => this.deleteItem(item.id)">Delete</button>

<!-- Modificadores de eventos -->
<button t-on-click.prevent="handleSubmit">Submit</button>
<button t-on-click.stop="handleClick">Stop propagation</button>

<!-- Input events -->
<input t-on-input="handleInput" t-att-value="state.value"/>
<input t-on-change="handleChange"/>
<input t-on-keyup.enter="handleEnter"/>

<!-- Formulários -->
<form t-on-submit.prevent="handleSubmit">
    <input type="text" t-model="state.username"/>
    <button type="submit">Enviar</button>
</form>
```

#### 5. Atributos Dinâmicos

```xml
<!-- t-att-ATTR: Atributo individual -->
<div t-att-class="state.isActive ? 'active' : ''"/>
<img t-att-src="state.imageUrl"/>
<a t-att-href="state.link"/>

<!-- t-attf-ATTR: Template string -->
<div t-attf-class="item {{ state.status }} {{ state.priority }}"/>
<img t-attf-src="/images/{{ state.productId }}.png"/>

<!-- t-att: Múltiplos atributos de uma vez -->
<div t-att="{'class': state.cssClass, 'data-id': state.id, 'title': state.tooltip}"/>
```

#### 6. Componentes

```xml
<!-- Componente básico -->
<t t-component="MySubComponent" t-props="myProps"/>

<!-- Componente com props inline -->
<t t-component="UserCard"
   t-props="{ user: state.currentUser, editable: true }"/>

<!-- Componente dinâmico -->
<t t-component="state.activeComponent" t-props="componentProps"/>

<!-- Slot (conteúdo filho) -->
<t t-component="Modal">
    <t t-set-slot="header">
        <h2>Título do Modal</h2>
    </t>
    <t t-set-slot="body">
        Conteúdo do modal...
    </t>
</t>
```

### Exemplo Completo: Dashboard Component

```xml
<templates>
    <t t-name="my_module.Dashboard">
        <div class="dashboard">
            <!-- Header com título dinâmico -->
            <header t-attf-class="dashboard-header {{ state.theme }}">
                <h1 t-esc="props.title"/>
                <button t-on-click="refresh"
                        t-att-disabled="state.loading">
                    🔄 Refresh
                </button>
            </header>

            <!-- Loading state -->
            <div t-if="state.loading" class="loading">
                <div class="spinner"/>
                Carregando dados...
            </div>

            <!-- Error state -->
            <div t-elif="state.error" class="error-message">
                ⚠️ Erro: <t t-esc="state.error"/>
                <button t-on-click="retry">Tentar novamente</button>
            </div>

            <!-- Success state -->
            <div t-else="" class="dashboard-content">
                <!-- Stats cards -->
                <div class="stats-grid">
                    <div t-foreach="state.stats" t-as="stat" t-key="stat.id"
                         t-attf-class="stat-card {{ stat.trend }}">
                        <div class="stat-value" t-esc="stat.value"/>
                        <div class="stat-label" t-esc="stat.label"/>
                        <div class="stat-change" t-if="stat.change">
                            <span t-if="stat.change > 0">📈 +</span>
                            <span t-else="">📉 </span>
                            <t t-esc="stat.change"/>%
                        </div>
                    </div>
                </div>

                <!-- Data table -->
                <table class="data-table">
                    <thead>
                        <tr>
                            <th t-foreach="state.columns" t-as="col" t-key="col.id"
                                t-on-click="() => this.sortBy(col.id)">
                                <t t-esc="col.label"/>
                                <span t-if="state.sortColumn === col.id">
                                    <t t-if="state.sortAsc">↑</t>
                                    <t t-else="">↓</t>
                                </span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr t-foreach="state.sortedData" t-as="row" t-key="row.id"
                            t-on-click="() => this.selectRow(row)"
                            t-att-class="row.id === state.selectedId ? 'selected' : ''">
                            <td t-foreach="state.columns" t-as="col" t-key="col.id">
                                <t t-esc="row[col.field]"/>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <!-- Empty state -->
                <div t-if="state.data.length === 0" class="empty-state">
                    Nenhum dado disponível
                </div>
            </div>
        </div>
    </t>
</templates>
```

---

## 🔗 Props e Communication

### Definindo Props

```javascript
class UserCard extends Component {
    static template = "my_module.UserCard";

    // Validação de props
    static props = {
        // Tipo simples
        userId: Number,

        // Tipo com valor padrão
        editable: { type: Boolean, optional: true },

        // Múltiplos tipos aceitos
        value: [String, Number],

        // Objeto com estrutura definida
        user: {
            type: Object,
            shape: {
                id: Number,
                name: String,
                email: { type: String, optional: true }
            }
        },

        // Array
        tags: { type: Array, element: String },

        // Callback
        onSave: Function,

        // Qualquer valor (não recomendado)
        data: true,

        // Props opcionais
        title: { type: String, optional: true },

        // Com valor padrão (deve ser função!)
        count: { type: Number, optional: true, default: () => 0 },
    };

    setup() {
        // Props são acessíveis via this.props
        console.log(this.props.userId);
        console.log(this.props.user.name);
    }

    handleSave() {
        // Chamar callback do pai
        this.props.onSave(this.state.data);
    }
}
```

### Parent → Child Communication (via Props)

```javascript
// Parent Component
class ParentComponent extends Component {
    static template = "my_module.Parent";
    static components = { ChildComponent };

    setup() {
        this.state = useState({
            userData: { id: 1, name: "John" },
            isEditable: true
        });
    }

    handleChildSave(data) {
        console.log("Child saved:", data);
        this.state.userData = data;
    }
}
```

```xml
<!-- Parent Template -->
<t t-name="my_module.Parent">
    <div>
        <ChildComponent
            user="state.userData"
            editable="state.isEditable"
            onSave.bind="handleChildSave"/>
    </div>
</t>
```

### Child → Parent Communication (via Callbacks)

```javascript
// Child Component
class ChildComponent extends Component {
    static template = "my_module.Child";
    static props = {
        user: Object,
        editable: Boolean,
        onSave: Function
    };

    setup() {
        this.state = useState({
            editedUser: { ...this.props.user }
        });
    }

    save() {
        // Notificar parent via callback
        this.props.onSave(this.state.editedUser);
    }
}
```

### Event Bus (Componentes Não-Relacionados)

```javascript
import { EventBus } from "@odoo/owl";

// Criar bus global
export const globalBus = new EventBus();

// Component A (emite evento)
class ComponentA extends Component {
    notifyOthers() {
        globalBus.trigger("user-updated", { userId: 123, name: "John" });
    }
}

// Component B (escuta evento)
class ComponentB extends Component {
    setup() {
        onMounted(() => {
            globalBus.addEventListener("user-updated", this.handleUserUpdate);
        });

        onWillUnmount(() => {
            globalBus.removeEventListener("user-updated", this.handleUserUpdate);
        });
    }

    handleUserUpdate(event) {
        console.log("User updated:", event.detail);
    }
}
```

---

## 🚀 Performance e Otimizações

### 1. Lazy Loading de Componentes

```javascript
import { Component, useState, onWillStart } from "@odoo/owl";

class DashboardComponent extends Component {
    static template = "my_module.Dashboard";

    setup() {
        this.HeavyChart = null;

        onWillStart(async () => {
            // Carregar componente pesado apenas quando necessário
            const module = await import('./heavy_chart_component');
            this.HeavyChart = module.HeavyChartComponent;
        });
    }
}
```

### 2. Memoization de Computed Properties

```javascript
class ProductList extends Component {
    setup() {
        this.state = useState({ products: [], filter: 'all' });

        // Cache de computed property
        this._cachedFiltered = null;
        this._lastFilter = null;
    }

    get filteredProducts() {
        // Retornar cache se filtro não mudou
        if (this.state.filter === this._lastFilter && this._cachedFiltered) {
            return this._cachedFiltered;
        }

        // Recalcular
        this._lastFilter = this.state.filter;
        this._cachedFiltered = this.state.products.filter(
            p => this.state.filter === 'all' || p.category === this.state.filter
        );

        return this._cachedFiltered;
    }
}
```

### 3. Otimização de Loops (t-key)

```xml
<!-- ❌ SEM t-key: Virtual DOM recriar TODOS os elementos a cada mudança -->
<div t-foreach="state.items" t-as="item">
    <span t-esc="item.name"/>
</div>

<!-- ✅ COM t-key: Virtual DOM reutiliza elementos existentes -->
<div t-foreach="state.items" t-as="item" t-key="item.id">
    <span t-esc="item.name"/>
</div>
```

**Impacto:**
- Sem `t-key`: 1000 items = 1000 DOM operations
- Com `t-key`: 1000 items (1 mudou) = 1 DOM operation

### 4. Debounce de Eventos

```javascript
class SearchComponent extends Component {
    setup() {
        this.state = useState({ query: '', results: [] });

        // Debounce manual
        this.searchTimeout = null;
    }

    onInput(event) {
        this.state.query = event.target.value;

        // Cancelar busca anterior
        clearTimeout(this.searchTimeout);

        // Agendar nova busca após 300ms
        this.searchTimeout = setTimeout(() => {
            this.performSearch();
        }, 300);
    }

    async performSearch() {
        this.state.results = await this.rpc('/search', {
            query: this.state.query
        });
    }
}
```

### 5. Virtual Scrolling (Grandes Listas)

```javascript
class VirtualListComponent extends Component {
    static template = "my_module.VirtualList";

    setup() {
        this.state = useState({
            items: [],        // Todos os itens (10,000+)
            visibleItems: [], // Apenas itens visíveis (~20)
            scrollTop: 0
        });

        this.itemHeight = 50; // Altura de cada item
        this.containerHeight = 600; // Altura do container

        onMounted(() => {
            this.updateVisibleItems();
        });
    }

    onScroll(event) {
        this.state.scrollTop = event.target.scrollTop;
        this.updateVisibleItems();
    }

    updateVisibleItems() {
        const startIndex = Math.floor(this.state.scrollTop / this.itemHeight);
        const endIndex = startIndex + Math.ceil(this.containerHeight / this.itemHeight);

        this.state.visibleItems = this.state.items.slice(startIndex, endIndex + 1);
    }
}
```

**Benefício:** Renderizar 20 items ao invés de 10,000 = **500x mais rápido!**

---

## 🔌 Integração com Odoo

### RPC Calls

```javascript
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class OdooIntegrationComponent extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.state = useState({ data: [] });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        // Método 1: RPC direto
        const result = await this.rpc("/my/custom/route", {
            param1: "value1"
        });

        // Método 2: ORM service
        const records = await this.orm.searchRead(
            "res.partner",
            [["is_company", "=", true]],
            ["name", "email", "phone"]
        );

        this.state.data = records;
    }

    async createRecord() {
        const newId = await this.orm.create(
            "res.partner",
            [{ name: "New Partner", email: "test@example.com" }]
        );
        console.log("Created partner ID:", newId);
    }

    async updateRecord(id, values) {
        await this.orm.write(
            "res.partner",
            [id],
            values
        );
    }

    async deleteRecord(id) {
        await this.orm.unlink("res.partner", [id]);
    }
}
```

### Notification Service

```javascript
import { useService } from "@web/core/utils/hooks";

class MyComponent extends Component {
    setup() {
        this.notification = useService("notification");
    }

    showSuccess() {
        this.notification.add("Operação realizada com sucesso!", {
            type: "success"
        });
    }

    showWarning() {
        this.notification.add("Atenção: dados incompletos", {
            type: "warning"
        });
    }

    showError() {
        this.notification.add("Erro ao salvar dados", {
            type: "danger",
            sticky: true  // Não desaparece automaticamente
        });
    }
}
```

### Action Service

```javascript
import { useService } from "@web/core/utils/hooks";

class MyComponent extends Component {
    setup() {
        this.action = useService("action");
    }

    openFormView(resId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'res.partner',
            res_id: resId,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    openListView() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'sale']],
            context: { search_default_my_orders: 1 },
        });
    }
}
```

---

## 🎨 Padrões e Best Practices

### 1. Estrutura de Arquivos

```
my_module/
├── static/
│   └── src/
│       ├── components/
│       │   ├── dashboard/
│       │   │   ├── dashboard.js
│       │   │   ├── dashboard.xml
│       │   │   └── dashboard.scss
│       │   ├── user_card/
│       │   │   ├── user_card.js
│       │   │   ├── user_card.xml
│       │   │   └── user_card.scss
│       │   └── index.js (exports)
│       ├── services/
│       │   ├── data_service.js
│       │   └── notification_service.js
│       └── utils/
│           └── helpers.js
```

### 2. Naming Conventions

```javascript
// ✅ BOM: PascalCase para componentes
class UserDashboard extends Component { }
class ProductCard extends Component { }

// ✅ BOM: camelCase para métodos e variáveis
handleClick() { }
loadUserData() { }

// ✅ BOM: Template names com namespace
static template = "my_module.UserDashboard";
static template = "my_module.ProductCard";

// ❌ RUIM: snake_case em JavaScript
class user_dashboard extends Component { }  // NÃO!

// ❌ RUIM: Template sem namespace
static template = "UserDashboard";  // Conflitos!
```

### 3. Error Handling

```javascript
class RobustComponent extends Component {
    setup() {
        this.state = useState({
            data: [],
            loading: false,
            error: null
        });

        // Captura de erros
        onError((error) => {
            console.error("Component error:", error);
            this.state.error = error.message;
            this.notification.add("Erro inesperado", { type: "danger" });
        });
    }

    async loadData() {
        this.state.loading = true;
        this.state.error = null;

        try {
            const data = await this.rpc('/my/endpoint');
            this.state.data = data;
        } catch (error) {
            console.error("Failed to load data:", error);
            this.state.error = "Falha ao carregar dados. Tente novamente.";
            throw error; // onError vai capturar
        } finally {
            this.state.loading = false;
        }
    }
}
```

### 4. Code Splitting

```javascript
// main.js
import { Component } from "@odoo/owl";

class MainApp extends Component {
    static template = "my_module.MainApp";

    setup() {
        this.DashboardComponent = null;
    }

    async openDashboard() {
        if (!this.DashboardComponent) {
            // Carregar apenas quando necessário
            const module = await import('./components/dashboard/dashboard');
            this.DashboardComponent = module.DashboardComponent;
        }
        // Mostrar dashboard...
    }
}
```

---

## 🐛 Troubleshooting

### Problema 1: Component Não Re-renderiza

**Sintoma:** Mudanças no estado não aparecem na UI

**Causas e Soluções:**

```javascript
// ❌ CAUSA: Modificação direta de array/objeto SEM useState
this.data.push(newItem);  // NÃO triggará re-render!

// ✅ SOLUÇÃO: Usar useState ou reatribuir
this.state.data = [...this.state.data, newItem];

// ❌ CAUSA: Mutação profunda em objeto não-reativo
this.state.user.profile.name = "New Name";  // Não é profundo!

// ✅ SOLUÇÃO: Reatribuir objeto completo
this.state.user = {
    ...this.state.user,
    profile: { ...this.state.user.profile, name: "New Name" }
};

// ✅ SOLUÇÃO 2: Usar reactive() para reatividade profunda
import { reactive } from "@odoo/owl";
this.state = reactive({ user: { profile: { name: "John" } } });
this.state.user.profile.name = "New Name";  // Funciona!
```

### Problema 2: "Cannot read property of undefined"

**Sintoma:** Erro ao acessar propriedades em template

**Solução:**

```xml
<!-- ❌ RUIM: Sem verificação -->
<div t-esc="state.user.profile.name"/>  <!-- Erro se user não existe! -->

<!-- ✅ BOM: Verificar antes -->
<div t-if="state.user and state.user.profile">
    <t t-esc="state.user.profile.name"/>
</div>

<!-- ✅ BOM: Optional chaining (JavaScript moderno) -->
<div t-esc="state.user?.profile?.name or 'N/A'"/>
```

### Problema 3: Memory Leaks

**Sintoma:** Memória cresce continuamente

**Causa:** Event listeners não removidos

**Solução:**

```javascript
setup() {
    this.handleResize = this.handleResize.bind(this);

    onMounted(() => {
        window.addEventListener('resize', this.handleResize);
    });

    // ⚠️ CRITICAL: SEMPRE remover listeners!
    onWillUnmount(() => {
        window.removeEventListener('resize', this.handleResize);
    });
}
```

### Problema 4: Props Não Atualizando

**Sintoma:** Component filho não reflete mudanças em props

**Solução:**

```javascript
class ChildComponent extends Component {
    static props = {
        user: Object
    };

    setup() {
        // ❌ RUIM: Copiar props para estado sem atualizar
        this.state = useState({
            localUser: this.props.user  // Nunca atualizará!
        });

        // ✅ BOM: Usar onWillUpdateProps
        this.state = useState({
            localUser: this.props.user
        });

        onWillUpdateProps((nextProps) => {
            this.state.localUser = nextProps.user;
        });

        // ✅ MELHOR: Usar props diretamente no template
        // Sem copiar para estado
    }
}
```

---

## 📚 Recursos e Referências

### Documentação Oficial
- **OWL GitHub:** https://github.com/odoo/owl
- **OWL Playground:** https://odoo.github.io/owl/playground/
- **Odoo Developer Docs:** https://www.odoo.com/documentation/17.0/developer/reference/frontend/owl.html

### Ferramentas
- **Odoo Debug Mode:** Ativar com `?debug=1` na URL
- **Browser DevTools:** React DevTools funciona parcialmente com OWL
- **Performance Profiler:** Chrome DevTools Performance tab

### Migração de Widgets para OWL
- **Odoo 14-16 → 17+:** Guia oficial de migração
- **Widget → Component:** Mapeamento de conceitos
- **Class system:** OWL usa ES6 classes nativas

---

## 🎯 Checklist de Migração (Odoo 15 → 17)

Quando migrarmos o projeto atual para Odoo 17+:

- [ ] Substituir todos Widgets por OWL Components
- [ ] Converter `_t()` para sistema de tradução OWL
- [ ] Migrar event handlers (`on_click` → `t-on-click`)
- [ ] Atualizar chamadas RPC para usar Services
- [ ] Converter QWeb templates para sintaxe OWL
- [ ] Implementar testes QUnit para componentes
- [ ] Adicionar TypeScript types (opcional)
- [ ] Testar performance com Virtual DOM
- [ ] Atualizar documentação de desenvolvimento

---

## 💡 Conclusão

**OWL 2.0 é o futuro do frontend Odoo:**
- ✅ Reativo e performático
- ✅ Baseado em padrões modernos (ES6, Proxies)
- ✅ Fácil de testar
- ✅ TypeScript ready

**Para nosso projeto (Odoo 15):**
- ⚠️ Ainda usa Widgets legado
- 📅 Planejar migração para Odoo 17+ em 2025/2026
- 📚 Conhecimento OWL útil para entender direção do Odoo

---

**Criado:** 2025-11-17
**Fontes:** 95+ artigos, docs oficiais, GitHub
**Status:** ✅ Conhecimento Consolidado e Salvo Localmente
**Próximo:** Python/Odoo ORM Mastery
