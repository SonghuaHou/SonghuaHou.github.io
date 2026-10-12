// 移动端菜单开关：点击按钮展开/收起全屏导航。
const btn = document.querySelector<HTMLButtonElement>("[data-menu-btn]");
const nav = document.querySelector<HTMLElement>("[data-mobile-nav]");
const iconOpen = document.querySelector<HTMLElement>("[data-icon-open]");
const iconClose = document.querySelector<HTMLElement>("[data-icon-close]");

function setOpen(open: boolean) {
  if (!btn || !nav) return;
  btn.setAttribute("aria-expanded", String(open));
  nav.classList.toggle("is-open", open);
  nav.setAttribute("aria-hidden", String(!open));
  if (iconOpen) iconOpen.style.opacity = open ? "0" : "1";
  if (iconClose) iconClose.style.opacity = open ? "1" : "0";
  document.body.style.overflow = open ? "hidden" : "";
}

btn?.addEventListener("click", () => {
  const open = btn.getAttribute("aria-expanded") === "true";
  setOpen(!open);
});

// 点击移动端导航里的链接后自动收起
nav?.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setOpen(false)));
