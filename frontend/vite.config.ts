import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  server: {
    host: "0.0.0.0",
    open: true,
  },
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      // @ts-ignore
      scss: { api: "modern-compiler" },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
});
