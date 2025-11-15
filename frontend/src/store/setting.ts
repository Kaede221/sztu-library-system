import { defineStore } from "pinia";
import { ref } from "vue";

export const useSettingStore = defineStore(
  "common-settings",
  () => {
    // 切换动画的时间
    const transitionDuration = ref(300);

    // 设置切换动画的时间
    const setTransitionDuration = (newVal: number) => {
      transitionDuration.value = newVal;
    };

    return {
      transitionDuration,
      setTransitionDuration,
    };
  },
  {
    persist: true,
  },
);
