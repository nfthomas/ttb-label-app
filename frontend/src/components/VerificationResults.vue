<!-- VerificationResults.vue -->
<template>
  <div v-if="results" class="verification-results">
    <!-- Success State -->
    <Card v-if="results.success && !results.error" class="success-card">
      <template #content>
        <div class="flex align-items-center mb-3">
          <CheckCircle class="success-icon mr-2" size="32" />
          <h2 class="text-xl font-bold">✅ Label Verification Successful</h2>
        </div>
        <p class="mb-4">All required information matches between the form and label image.</p>
        
        <div class="details-panel p-3 border-round">
          <div v-for="(field, key) in results.fields" :key="key" class="field-result mb-2">
            <span class="mr-2">✓</span>
            <span class="field-name">{{ formatFieldName(key) }}:</span>
            <span class="field-value">{{ field.value }}</span>
            <span class="verified-tag">Verified</span>
          </div>
        </div>
      </template>
    </Card>

    <!-- Failure State -->
    <Card v-else-if="!results.success && !results.error" class="error-card">
      <template #content>
        <div class="flex align-items-center mb-3">
          <AlertOctagon class="error-icon mr-2" size="32" />
          <h2 class="text-xl font-bold">❌ Label Verification Failed</h2>
        </div>
        <p class="mb-4">Discrepancies found between form and label image.</p>

        <div class="details-panel p-3 border-round">
          <div v-for="(field, key) in results.fields" :key="key" class="field-result mb-2">
            <template v-if="field.matches">
              <span class="success-check mr-2">✓</span>
              <span class="field-name">{{ formatFieldName(key) }}:</span>
              <span class="field-value">{{ field.value }}</span>
              <span class="verified-tag">Verified</span>
            </template>
            <template v-else>
              <span class="error-x mr-2">✗</span>
              <span class="field-name">{{ formatFieldName(key) }}:</span>
              <span class="field-value error-text">
                Expected: {{ field.expected }}
                <br />
                Found: {{ field.value || 'Not detected' }}
              </span>
            </template>
          </div>
        </div>
      </template>
    </Card>

    <!-- Error State -->
    <Card v-else class="warning-card">
      <template #content>
        <div class="flex align-items-center mb-3">
          <AlertTriangle class="warning-icon mr-2" size="32" />
          <h2 class="text-xl font-bold">⚠️ Unable to Process Image</h2>
        </div>
        <p class="error-message mb-4">{{ results.error || 'An unexpected error occurred' }}</p>
      </template>
    </Card>

    <!-- OCR Debug Panel -->
    <Card v-if="results.ocrText" class="results debug-panel">
      <template #content>
        <Accordion :activeIndex="[]">
          <AccordionTab header="View Raw OCR Text">
            <pre class="ocr-text">{{ results.ocrText }}</pre>
          </AccordionTab>
        </Accordion>
      </template>
    </Card>
  </div>
</template>

<script>
import { CheckCircle, AlertOctagon, AlertTriangle } from 'lucide-vue-next'

export default {
  name: 'VerificationResults',
  components: {
    CheckCircle,
    AlertOctagon,
    AlertTriangle
  },
  props: {
    results: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatFieldName(key) {
      return key
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
    }
  }
}
</script>

<style scoped>
.verification-results {
  margin-top: 2rem;
}

.success-card :deep(.p-card-content) {
  background-color: #f0fdf4;
  border: 1px solid #86efac;
}

.error-card :deep(.p-card-content) {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
}

.warning-card :deep(.p-card-content) {
  background-color: #fffbeb;
  border: 1px solid #fef3c7;
}

.success-icon {
  color: #22c55e;
}

.error-icon {
  color: #ef4444;
}

.warning-icon {
  color: #f59e0b;
}

.details-panel {
  background: rgba(255, 255, 255, 0.5);
}

.field-result {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.field-name {
  font-weight: 600;
  min-width: 120px;
}

.success-check {
  color: #22c55e;
}

.error-x {
  color: #ef4444;
}

.error-text {
  color: #ef4444;
}

.verified-tag {
  background: #dcfce7;
  color: #166534;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  margin-left: auto;
}

.ocr-text {
  white-space: pre-wrap;
  font-family: monospace;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}
</style>