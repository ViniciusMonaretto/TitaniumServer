# IoButton Component

Um componente de botão padrão para o projeto IoCloud, desenvolvido com Angular e seguindo o design system do projeto.

## Características

- ✅ Múltiplas variantes (primary, secondary, outline, ghost, danger, success)
- ✅ Diferentes tamanhos (small, medium, large)
- ✅ Suporte a ícones (Material Icons)
- ✅ Estados de loading e disabled
- ✅ Acessibilidade completa
- ✅ Responsivo
- ✅ Design único baseado no estilo do IoCloud
- ✅ Gradientes elegantes e efeitos visuais
- ✅ Animações suaves e efeito ripple
- ✅ Sombras dinâmicas e hover effects

## Uso Básico

```html
<io-button (clicked)="onButtonClick()">
  Clique aqui
</io-button>
```

## Propriedades

| Propriedade | Tipo | Padrão | Descrição |
|-------------|------|--------|-----------|
| `variant` | `'primary' \| 'secondary' \| 'outline' \| 'ghost' \| 'danger' \| 'success'` | `'primary'` | Estilo visual do botão |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | Tamanho do botão |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | Tipo do botão HTML |
| `disabled` | `boolean` | `false` | Se o botão está desabilitado |
| `loading` | `boolean` | `false` | Se o botão está em estado de loading |
| `fullWidth` | `boolean` | `false` | Se o botão ocupa toda a largura disponível |
| `icon` | `string` | `''` | Nome do ícone Material Icons |
| `iconPosition` | `'left' \| 'right'` | `'left'` | Posição do ícone |
| `ariaLabel` | `string` | `''` | Label para acessibilidade |

## Eventos

| Evento | Tipo | Descrição |
|--------|------|-----------|
| `clicked` | `EventEmitter<Event>` | Emitido quando o botão é clicado |

## Exemplos

### Variantes

```html
<!-- Primário (padrão) -->
<io-button>Primário</io-button>

<!-- Secundário -->
<io-button variant="secondary">Secundário</io-button>

<!-- Outline -->
<io-button variant="outline">Outline</io-button>

<!-- Ghost -->
<io-button variant="ghost">Ghost</io-button>

<!-- Perigo -->
<io-button variant="danger">Perigo</io-button>

<!-- Sucesso -->
<io-button variant="success">Sucesso</io-button>
```

### Tamanhos

```html
<io-button size="small">Pequeno</io-button>
<io-button size="medium">Médio</io-button>
<io-button size="large">Grande</io-button>
```

### Com Ícones

```html
<!-- Ícone à esquerda (padrão) -->
<io-button icon="save">Salvar</io-button>

<!-- Ícone à direita -->
<io-button icon="arrow_forward" iconPosition="right">Próximo</io-button>
```

### Estados

```html
<!-- Desabilitado -->
<io-button disabled="true">Desabilitado</io-button>

<!-- Loading -->
<io-button loading="true">Carregando...</io-button>

<!-- Largura total -->
<io-button fullWidth="true">Largura Total</io-button>
```

### Combinações

```html
<io-button 
  variant="primary" 
  size="large" 
  icon="download" 
  fullWidth="true" 
  (clicked)="onDownload()">
  Download Completo
</io-button>
```

## Acessibilidade

O componente inclui suporte completo para acessibilidade:

- Suporte a `aria-label` para leitores de tela
- Navegação por teclado
- Estados visuais claros para disabled e loading
- Foco visível para navegação por teclado

## Design System

O componente foi criado com um design único baseado no estilo do projeto IoCloud:

- **Gradientes**: Gradientes elegantes para cada variante (azul, cinza, vermelho, verde)
- **Cores**: Baseado nas cores do projeto (#3E5CAF, #6B7280, #1D4ED8)
- **Tipografia**: Segoe UI como fonte principal com peso 600
- **Bordas**: Border-radius de 8px (consistente com cards do projeto)
- **Sombras**: Sombras dinâmicas que mudam no hover
- **Transições**: Animações suaves de 0.2s
- **Efeitos**: Brilho sutil, ripple effect, transform no hover
- **Estados**: Hover com elevação sutil (-1px) e sombras mais pronunciadas

## Responsividade

O componente é totalmente responsivo e se adapta a diferentes tamanhos de tela:

- Em dispositivos móveis, os botões aumentam ligeiramente de tamanho para melhor usabilidade
- Mantém a legibilidade em todos os tamanhos de tela
