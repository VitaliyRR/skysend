(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function setupHeader() {
    const header = document.querySelector("[data-header]");
    const sentinel = document.getElementById("top-sentinel");
    if (!header || !sentinel || !("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(([entry]) => {
      header.classList.toggle("is-scrolled", !entry.isIntersecting);
    });
    observer.observe(sentinel);
  }

  function setupMenu() {
    const dialog = document.getElementById("site-menu");
    const open = document.querySelector("[data-menu-open]");
    const close = document.querySelector("[data-menu-close]");
    if (!dialog || !open || !close || typeof dialog.showModal !== "function") return;

    const shut = () => {
      if (dialog.open) dialog.close();
    };
    const desktop = window.matchMedia("(min-width: 75rem)");

    open.addEventListener("click", () => {
      dialog.showModal();
      open.setAttribute("aria-expanded", "true");
      document.body.classList.add("menu-open");
      close.focus();
    });
    close.addEventListener("click", shut);
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) shut();
    });
    dialog.addEventListener("close", () => {
      open.setAttribute("aria-expanded", "false");
      document.body.classList.remove("menu-open");
      if (!desktop.matches) open.focus({ preventScroll: true });
    });
    dialog.querySelectorAll("a").forEach((link) => link.addEventListener("click", shut));
    desktop.addEventListener("change", (event) => {
      if (event.matches) shut();
    });
  }

  function setupDropdowns() {
    const hover = window.matchMedia("(hover: hover) and (pointer: fine)");
    document.querySelectorAll("[data-nav-menu]").forEach((menu) => {
      const summary = menu.querySelector("summary");
      if (!summary) return;
      menu.addEventListener("pointerenter", () => {
        if (hover.matches) menu.open = true;
      });
      menu.addEventListener("pointerleave", () => {
        if (!menu.contains(document.activeElement)) menu.open = false;
      });
      menu.addEventListener("focusout", () => {
        window.setTimeout(() => {
          if (!menu.contains(document.activeElement)) menu.open = false;
        });
      });
      menu.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        event.preventDefault();
        menu.open = false;
        summary.focus();
      });
    });
  }

  function setupLightbox() {
    const dialog = document.getElementById("media-dialog");
    const image = dialog?.querySelector("[data-lightbox-image]");
    const title = dialog?.querySelector("#media-dialog-title");
    const caption = dialog?.querySelector("[data-lightbox-caption]");
    const close = dialog?.querySelector("[data-lightbox-close]");
    if (!dialog || !image || !title || !caption || !close || typeof dialog.showModal !== "function") return;

    let trigger = null;
    const shut = () => {
      if (dialog.open) dialog.close();
    };
    document.querySelectorAll("[data-lightbox-src]").forEach((control) => {
      control.addEventListener("click", (event) => {
        event.preventDefault();
        trigger = control;
        const label = control.dataset.lightboxCaption || control.dataset.lightboxAlt || "Изображение";
        image.src = control.dataset.lightboxSrc || "";
        image.alt = control.dataset.lightboxAlt || "";
        title.textContent = label;
        caption.textContent = `${label}. Внешний вид зависит от версии и настроек ПО.`;
        dialog.showModal();
        document.body.classList.add("dialog-open");
        close.focus();
      });
    });
    close.addEventListener("click", shut);
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) shut();
    });
    dialog.addEventListener("close", () => {
      document.body.classList.remove("dialog-open");
      image.removeAttribute("src");
      trigger?.focus({ preventScroll: true });
    });
  }

  function setupReveals() {
    const sections = [...document.querySelectorAll("[data-reveal]")];
    if (!sections.length || reducedMotion.matches || !("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -48px 0px" },
    );
    sections.forEach((section) => observer.observe(section));
    document.documentElement.classList.add("reveal-ready");
  }

  const normalize = (value) =>
    String(value || "")
      .trim()
      .toLocaleLowerCase("ru-RU")
      .replaceAll("ё", "е")
      .replace(/\s+/g, " ");

  function initials(name) {
    const words = String(name).match(/[A-Za-zА-Яа-яЁё0-9]+/g) || [];
    return words.slice(0, 2).map((word) => word[0]).join("").toUpperCase() || "SS";
  }

  function createProviderCard(provider) {
    const item = document.createElement("li");
    item.className = "provider-card";
    let visual;
    if (provider.logo) {
      visual = document.createElement("img");
      visual.className = "provider-card__logo";
      visual.src = provider.logo;
      visual.alt = "";
      visual.loading = "lazy";
      visual.decoding = "async";
      visual.width = 150;
      visual.height = 150;
    } else {
      visual = document.createElement("span");
      visual.className = "provider-card__fallback";
      visual.setAttribute("aria-hidden", "true");
      visual.textContent = initials(provider.name);
    }
    const copy = document.createElement("span");
    const name = document.createElement("strong");
    const category = document.createElement("small");
    name.textContent = provider.name;
    category.textContent = provider.category;
    copy.append(name, category);
    item.append(visual, copy);
    return item;
  }

  function pageSequence(current, total) {
    const values = new Set([1, total, current - 2, current - 1, current, current + 1, current + 2]);
    return [...values].filter((value) => value >= 1 && value <= total).sort((a, b) => a - b);
  }

  async function setupProviderCatalog() {
    const app = document.querySelector("[data-provider-app]");
    if (!app) return;
    const results = app.querySelector("[data-provider-results]");
    const count = app.querySelector("[data-provider-count]");
    const pages = app.querySelector("[data-provider-pages]");
    const empty = app.querySelector("[data-provider-empty]");
    const form = app.querySelector("[data-provider-form]");
    const search = app.querySelector("[data-provider-search]");
    const chips = [...app.querySelectorAll("[data-provider-category]")];
    const resets = [...app.querySelectorAll("[data-provider-reset]")];
    if (!results || !count || !pages || !empty || !search) return;
    let submitSearch = () => {};
    form?.addEventListener("submit", (event) => {
      event.preventDefault();
      submitSearch();
    });

    let payload;
    try {
      const response = await fetch("/data/providers.json", { credentials: "same-origin" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      payload = await response.json();
    } catch (_error) {
      count.textContent = "Показано 30 записей. Поиск временно недоступен.";
      return;
    }

    const all = payload.providers || [];
    const perPage = 30;
    let selectedCategory = "all";
    let currentPage = 1;
    let searchTimer;

    const filtered = () => {
      const query = normalize(search.value);
      return all.filter((provider) => {
        const categoryMatches = selectedCategory === "all" || provider.category_id === selectedCategory;
        return categoryMatches && (!query || normalize(provider.name).includes(query));
      });
    };

    const renderPagination = (totalPages) => {
      pages.replaceChildren();
      if (totalPages <= 1) return;

      const addButton = (label, page, options = {}) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        button.setAttribute("aria-label", options.aria || `Страница ${page}`);
        if (options.current) button.setAttribute("aria-current", "page");
        if (options.disabled) button.disabled = true;
        button.addEventListener("click", () => {
          currentPage = page;
          render();
          count.focus?.({ preventScroll: true });
        });
        pages.append(button);
      };

      addButton("←", Math.max(1, currentPage - 1), {
        aria: "Предыдущая страница",
        disabled: currentPage === 1,
      });
      let previous = 0;
      for (const value of pageSequence(currentPage, totalPages)) {
        if (previous && value - previous > 1) {
          const separator = document.createElement("span");
          separator.textContent = "…";
          separator.setAttribute("aria-hidden", "true");
          pages.append(separator);
        }
        addButton(String(value), value, { current: value === currentPage });
        previous = value;
      }
      addButton("→", Math.min(totalPages, currentPage + 1), {
        aria: "Следующая страница",
        disabled: currentPage === totalPages,
      });
    };

    const render = () => {
      const list = filtered();
      const totalPages = Math.max(1, Math.ceil(list.length / perPage));
      currentPage = Math.min(currentPage, totalPages);
      const start = (currentPage - 1) * perPage;
      const visible = list.slice(start, start + perPage);
      results.replaceChildren(...visible.map(createProviderCard));
      results.hidden = visible.length === 0;
      empty.hidden = visible.length !== 0;
      count.textContent = list.length
        ? `Найдено: ${list.length}. Показано ${start + 1}–${start + visible.length}.`
        : "Найдено: 0.";
      renderPagination(list.length ? totalPages : 0);
    };

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        selectedCategory = chip.dataset.providerCategory || "all";
        currentPage = 1;
        chips.forEach((item) => {
          const active = item === chip;
          item.classList.toggle("is-active", active);
          item.setAttribute("aria-pressed", String(active));
        });
        render();
      });
    });
    search.addEventListener("input", () => {
      window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(() => {
        currentPage = 1;
        render();
      }, 120);
    });
    submitSearch = () => {
      window.clearTimeout(searchTimer);
      currentPage = 1;
      render();
      count.focus({ preventScroll: true });
    };
    resets.forEach((button) => {
      button.addEventListener("click", () => {
        search.value = "";
        selectedCategory = "all";
        currentPage = 1;
        chips.forEach((chip) => {
          const active = chip.dataset.providerCategory === "all";
          chip.classList.toggle("is-active", active);
          chip.setAttribute("aria-pressed", String(active));
        });
        render();
        search.focus();
      });
    });
    render();
  }

  setupHeader();
  setupMenu();
  setupDropdowns();
  setupLightbox();
  setupReveals();
  setupProviderCatalog();
})();
