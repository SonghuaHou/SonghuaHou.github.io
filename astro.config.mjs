// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  output: "static",
  // ↓↓↓ 改成你自己的 GitHub Pages 地址（仓库名建议用 <用户名>.github.io，根路径）
  //     例如用户名是 johndoe，就填 https://johndoe.github.io
  site: "https://SonghuaHou.github.io",
  // 若你把站点放在子路径仓库（如 johndoe.github.io/portfolio），
  // 取消下一行注释并改成对应仓库名：base: "/portfolio",
  // base: "/",
  // sitemap-index.xml for search engines; the 404 page is left out.
  integrations: [sitemap({ filter: (page) => !/\/404\/?$/.test(page) })],
});
