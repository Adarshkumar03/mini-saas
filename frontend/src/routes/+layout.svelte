<script>
  import { onMount } from "svelte";
  let { children } = $props();
  import "../app.css";
  import { initializeUserStore } from "$lib/stores";

  onMount(() => {
    initializeUserStore();
  });
</script>
{@render children()}