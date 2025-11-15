import { createApp } from "vue";

import App from "./App.vue";
import { router } from "@/router/index.js";
import pinia from "@/store/index.js";

import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import ElementPlus from "element-plus";

import "element-plus/dist/index.css";
import "./style.css";

const app = createApp(App);

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  // @ts-ignore
  app.component(key, component);
}

app.use(pinia);
app.use(router);
app.use(ElementPlus);
app.mount("#app");
