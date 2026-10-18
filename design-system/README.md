# Sistema de Diseño — CANACO Editorial

> Sistema de diseño para una plataforma de noticias, publicaciones y artículos científicos
> con administración por categorías y panel de superadmin.

---

## 1. Filosofía de Diseño

**Estilo base:** *Minimalismo Cálido + Editorial Grid*

La plataforma se inspira en el rigor de una publicación académica y la calidez de un
medio de noticias cercano. La interfaz **desaparece** para que el contenido (artículos,
noticias, investigaciones) sea el protagonista.

### Principios rectores
| Principio | Aplicación |
|---|---|
| **Limpio** | Espacio en blanco generoso, sin decoración innecesaria. |
| **Cálido** | Paleta terrosa (arena, terracota, ámbar, olivo). Cero morados/azules fríos. |
| **Jerárquico** | La tipografía serif marca la pauta; el lector siempre sabe dónde está. |
| **Funcional** | Cada elemento del panel admin tiene un propósito claro. |
| **Accesible** | Contraste AA mínimo (4.5:1), foco visible, navegación por teclado. |

### ❌ Prohibido
- Degradados morados (`#7C3AED`, `#A78BFA`) o azules fríos (`#2563EB`, `#3B82F6`).
- Sombras exageradas o efectos "neón".
- Fuentes decorativas de baja legibilidad en cuerpo de texto.

---

## 2. Paleta de Colores (Cálida)

### Colores Primarios
| Token | HEX | Uso |
|---|---|---|
| `--color-primary` | `#B45309` | Terracota/ámbar profundo — marca, CTAs principales |
| `--color-primary-hover` | `#92400E` | Estado hover de acciones primarias |
| `--color-primary-light` | `#FEF3C7` | Fondos suaves, badges informativos |
| `--color-secondary` | `#4D7C0F` | Verde olivo — acciones secundarias, éxito |
| `--color-accent` | `#D97706` | Ámbar — acentos, enlaces activos |

### Superficies y Fondos
| Token | HEX | Uso |
|---|---|---|
| `--color-bg` | `#FDFBF7` | Fondo general (arena muy claro) |
| `--color-surface` | `#FFFFFF` | Tarjetas, modales, contenedores |
| `--color-surface-alt` | `#F5F1EA` | Superficie alterna (secciones) |
| `--color-border` | `#E7E0D3` | Bordes y divisores |

### Texto
| Token | HEX | Uso |
|---|---|---|
| `--color-text` | `#2B2621` | Texto principal (marrón casi negro) |
| `--color-text-muted` | `#6B6259` | Texto secundario, metadatos |
| `--color-text-inverse` | `#FFFFFF` | Texto sobre fondos oscuros |

### Estados Semánticos
| Token | HEX | Uso |
|---|---|---|
| `--color-success` | `#4D7C0F` | Aprobado / publicado |
| `--color-warning` | `#D97706` | Pendiente / borrador |
| `--color-danger` | `#B91C1C` | Bloqueado / eliminar |
| `--color-info` | `#0E7490` | Informativo (único azul permitido: verde-cian cálido) |

> **Nota:** el único "azul" tolerado es `#0E7490` (teal) usado con moderación para
> información neutra. Nunca como color de marca ni en degradados.

---

## 3. Tipografía

**Par elegido: Academic/Research** — ideal para artículos científicos y noticias.

| Rol | Fuente | Peso | Uso |
|---|---|---|---|
| **Títulos (Heading)** | `Crimson Pro` (serif) | 600–700 | H1, H2, títulos de artículos |
| **Cuerpo (Body)** | `Atkinson Hyperlegible` (sans) | 400–700 | Texto, UI, formularios |

```html
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Crimson+Pro:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Escala tipográfica
| Token | Tamaño | Uso |
|---|---|---|
| `--text-xs` | `12px` | Etiquetas, captions |
| `--text-sm` | `14px` | Metadatos, ayudas |
| `--text-base` | `16px` | Cuerpo de texto |
| `--text-lg` | `18px` | Cuerpo destacado / resúmenes |
| `--text-xl` | `22px` | Subtítulos |
| `--text-2xl` | `28px` | H3 |
| `--text-3xl` | `36px` | H2 |
| `--text-4xl` | `48px` | H1 / hero |

---

## 4. Espaciado (Escala base 4px)

| Token | Valor | Token | Valor |
|---|---|---|---|
| `--space-1` | `4px` | `--space-6` | `24px` |
| `--space-2` | `8px` | `--space-8` | `32px` |
| `--space-3` | `12px` | `--space-10` | `40px` |
| `--space-4` | `16px` | `--space-12` | `48px` |
| `--space-5` | `20px` | `--space-16` | `64px` |

---

## 5. Radios y Sombras

| Token | Valor | Uso |
|---|---|---|
| `--radius-sm` | `6px` | Inputs, badges |
| `--radius-md` | `10px` | Botones, tarjetas |
| `--radius-lg` | `16px` | Modales, paneles |
| `--radius-full` | `9999px` | Avatares, pills |

| Token | Valor | Uso |
|---|---|---|
| `--shadow-sm` | `0 1px 3px rgba(43,38,33,.06)` | Elevación sutil |
| `--shadow-md` | `0 4px 12px rgba(43,38,33,.08)` | Tarjetas |
| `--shadow-lg` | `0 12px 28px rgba(43,38,33,.12)` | Modales, dropdowns |

---

## 6. Componentes Clave del Sistema

### 6.1 Tarjeta de Publicación (Artículo/Noticia)
```
┌─────────────────────────────┐
│  [Imagen portada 16:9]      │
│  ▸ CATEGORÍA  ·  12 Oct     │  ← badge + metadatos
│  Título del artículo        │  ← Crimson Pro, H3
│  Resumen breve de dos       │
│  líneas máximo...           │  ← Atkinson, muted
│  👁 124 visitas             │  ← footer de la tarjeta
└─────────────────────────────┘
```

### 6.2 Estados de Publicación / Comentario
| Estado | Color | Badge |
|---|---|---|
| Borrador | `--color-warning` | Ámbar suave |
| Pendiente | `--color-warning` | Ámbar suave |
| Publicado | `--color-success` | Verde olivo |
| Aprobado | `--color-success` | Verde olivo |
| Bloqueado | `--color-danger` | Rojo terracota |

### 6.3 Navegación del Panel Admin
- **Sidebar** con iconos + etiquetas: Dashboard · Publicaciones · Categorías · Comentarios · Usuarios · Archivos.
- Fondo `--color-surface`, item activo con barra lateral ámbar (`--color-primary`).
- Ancho: `260px` expandido / `72px` colapsado.

### 6.4 Tablas de datos (listados admin)
- Encabezado con fondo `--color-surface-alt`, texto uppercase `--text-xs`.
- Filas alternas sutiles, hover `--color-primary-light`.
- Wrapper `overflow-x-auto` para móvil (ver guía UX).

### 6.5 Formularios
- Labels arriba, texto `--text-sm` semibold.
- Inputs con borde `--color-border`, foco con `outline` ámbar de 2px.
- Validación en **blur** + resumen de errores arriba del formulario.

---

## 7. Accesibilidad (Requisitos mínimos)

- [ ] Contraste texto/fondo ≥ **4.5:1** (AA).
- [ ] Foco visible en TODOS los elementos interactivos (outline ámbar 2px).
- [ ] Navegación completa por teclado (tab order lógico).
- [ ] `aria-label` en iconos sin texto.
- [ ] Respetar `prefers-reduced-motion`.
- [ ] Formularios con `role="alert"` en resumen de errores.

---

## 8. Archivos del Sistema

| Archivo | Descripción |
|---|---|
| `README.md` | Este documento — guía maestra. |
| `tokens.css` | Tokens de 3 capas (primitivo → semántico → componente) listos para usar. |
| `components.css` | Especificaciones de componentes (botones, tarjetas, badges, tablas, forms). |

### Cómo integrarlo en Django
1. Copia `tokens.css` y `components.css` a `canaco/static/css/`.
2. En `base.html`, cárgalos **después** de Bootstrap:
   ```html
   <link rel="stylesheet" href="{% static 'css/tokens.css' %}">
   <link rel="stylesheet" href="{% static 'css/components.css' %}">
   ```
3. Actualiza el link de Google Fonts con el par Crimson Pro + Atkinson Hyperlegible.
