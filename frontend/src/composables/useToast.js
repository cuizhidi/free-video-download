import { reactive } from "vue";

const toast = reactive({ visible: false, message: "", type: "error" });
let timer = null;

export function useToast() {
  function showToast(msg, type = "error") {
    clearTimeout(timer);
    toast.visible = true;
    toast.message = msg;
    toast.type = type;
    timer = setTimeout(() => {
      toast.visible = false;
    }, 4000);
  }
  return { toast, showToast };
}
