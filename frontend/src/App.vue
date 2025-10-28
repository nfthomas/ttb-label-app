<script setup>
import { onMounted } from 'vue';
import { healthCheck } from '@/services/api';
import { useToast } from 'primevue/usetoast';
import VerificationPage from './views/VerificationPage.vue';

const toast = useToast();

onMounted(async () => {
  try {
    await healthCheck();
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Backend Offline',
      detail: 'The backend is currently unavailable. Please try again later.',
      life: 5000,
    });
  }
});
</script>

<template>
  <Toast />
  <VerificationPage />
</template>
