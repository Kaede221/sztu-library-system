import { createPinia } from "pinia";
import persistPiniaPlugin from "pinia-plugin-persistedstate";

const pinia = createPinia();
pinia.use(persistPiniaPlugin);

export default pinia;

// 统一暴露内容
export * from "./user.ts";
