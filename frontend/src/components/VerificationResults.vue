<!-- VerificationResults.vue -->
<template>
  <div v-if="results" class="verification-results">
    <!-- Success State -->
    <Card v-if="results.success && !results.error" class="success-card">
      <template #content>
        <div class="flex align-items-center gap-2">
          <CheckCircle class="success-icon" size="28" />
          <h2 class="text-xl font-bold">Label Verification Successful</h2>
        </div>
        <p class="mt-3 mb-4">
          All required information matches between the form and label image.
        </p>

        <div class="details-panel p-3 border-round">
          <div
            v-for="(matched, key) in results.matches"
            :key="key"
            class="field-result mb-2"
          >
            <span class="mr-2">✓</span>
            <span class="field-name">{{ formatFieldName(key) }}:</span>
            <span class="verified-tag">Verified</span>
          </div>
        </div>
      </template>
    </Card>

    <!-- Failure State -->
    <Card v-else-if="!results.success && !results.error" class="error-card">
      <template #content>
        <div class="flex align-items-center gap-2">
          <AlertOctagon class="error-icon" size="28" />
          <h2 class="text-xl font-bold">Label Verification Failed</h2>
        </div>
        <p class="mt-3 mb-4">
          Discrepancies found between form and label image.
        </p>

        <div class="details-panel p-3 border-round">
          <div
            v-for="(matched, key) in results.matches"
            :key="key"
            class="field-result mb-2"
            :class="{ success: matched, failure: !matched }"
          >
            <span v-if="matched" class="success-check mr-2">✓</span>
            <span v-else class="error-x mr-2">✗</span>
            <span class="field-name">{{ formatFieldName(key) }}:</span>
            <span v-if="matched" class="verified-tag">Verified</span>
            <div v-else>
              <div class="expected-value mt-1 pl-4">
                <span class="text-sm text-500"
                  >(expected {{ results.expected_values[key] }})</span
                >
              </div>
              <div v-if="results.close_matches[key]" class="mt-2 pl-4">
                <div class="text-sm text-500">Close matches found:</div>
                <div
                  v-for="(match, idx) in results.close_matches[key]"
                  :key="idx"
                  class="text-sm text-red-700"
                >
                  {{ match }}
                </div>
              </div>
              <span v-else class="text-sm text-red-700 ml-6">Not found</span>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Error State -->
    <Card v-else class="warning-card">
      <template #content>
        <div class="flex align-items-center gap-2">
          <AlertTriangle class="warning-icon" size="28" />
          <h2 class="text-xl font-bold">Unable to Process Image</h2>
        </div>
        <p class="error-message mt-3 mb-4">
          {{ results.error || 'An unexpected error occurred' }}
        </p>
        <div v-if="isImageError(results.error)" class="image-requirements mt-3">
          <h3 class="text-lg mb-2">Image Requirements:</h3>
          <ul class="list-none p-0">
            <li>• File type must be JPEG or PNG</li>
            <li>• Maximum file size: 5MB</li>
            <li>• Image should be clear and well-lit</li>
            <li>• Text should be readable and not blurry</li>
          </ul>
        </div>
      </template>
    </Card>

    <!-- OCR Debug Panel -->
    <Card
      v-if="results.raw_ocr_text || results.image_info"
      class="results debug-panel mt-3"
    >
      <template #content>
        <Accordion :activeIndex="[]">
          <AccordionTab v-if="results.raw_ocr_text" header="View Raw OCR Text">
            <pre class="ocr-text">{{ results.raw_ocr_text }}</pre>
          </AccordionTab>
          <AccordionTab v-if="results.image_info" header="Image Information">
            <h3 class="text-lg mb-2">Image Information</h3>
            <div class="grid">
              <div class="col-6 md:col-3">
                <div class="text-500">Dimensions</div>
                <div>
                  {{ results.image_info.width }}x{{
                    results.image_info.height
                  }}px
                </div>
              </div>
              <div class="col-6 md:col-3">
                <div class="text-500">File Size</div>
                <div>{{ formatFileSize(results.image_info.file_size) }}</div>
              </div>
              <div class="col-6 md:col-3">
                <div class="text-500">Format</div>
                <div>{{ results.image_info.format }}</div>
              </div>
            </div>
          </AccordionTab>
        </Accordion>
      </template>
    </Card>
  </div>
</template>

<script>
import { CheckCircle, AlertOctagon, AlertTriangle } from 'lucide-vue-next';

export default {
  name: 'VerificationResults',
  components: {
    CheckCircle,
    AlertOctagon,
    AlertTriangle,
  },
  props: {
    results: {
      type: Object,
      required: true,
    },
  },
  methods: {
    formatFieldName(key) {
      return key
        .replace(/_/g, ' ') // Replace underscores with spaces
        .replace(/([A-Z])/g, ' $1') // Add space before capital letters
        .replace(/^./, (str) => str.toUpperCase()) // Capitalize first letter
        .replace(/\s+/g, ' ') // Remove any double spaces
        .trim(); // Remove any leading/trailing spaces
    },
    formatFileSize(sizeInKB) {
      if (!sizeInKB) return 'Unknown';
      return sizeInKB < 1024
        ? `${Math.round(sizeInKB)}KB`
        : `${(sizeInKB / 1024).toFixed(1)}MB`;
    },
    isImageError(error) {
      if (!error) return false;
      return (
        error.toLowerCase().includes('image') ||
        error.toLowerCase().includes('file') ||
        error.toLowerCase().includes('text')
      );
    },
  },
};
</script>

<style scoped>
.verification-results {
  max-width: 800px;
  margin: 2rem auto 0;
}

/* Card styles */
.success-card :deep(.p-card-content),
.error-card :deep(.p-card-content),
.warning-card :deep(.p-card-content) {
  padding: 1.5rem;
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

/* Icons */
.success-icon {
  color: #22c55e;
}

.error-icon {
  color: #ef4444;
}

.warning-icon {
  color: #f59e0b;
}

/* Status indicators */
.success-check {
  color: #22c55e;
}

.error-x {
  color: #ef4444;
}

.error-text {
  color: #ef4444;
}

/* Content sections */
.details-panel {
  background-color: rgba(255, 255, 255, 0.5);
  margin-top: 1.5rem;
  border-radius: 0.5rem;
  overflow: hidden;
}

.field-result {
  display: flex;
  align-items: flex-start;
  padding: 0.75rem;
}

.field-result:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.field-result.success {
  background-color: rgba(0, 200, 0, 0.05);
}

.field-result.failure {
  background-color: rgba(255, 0, 0, 0.05);
}

.field-name {
  font-weight: 600;
  min-width: 120px;
}

.verified-tag {
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  background-color: #22c55e;
  color: white;
  margin-left: auto;
}

.expected-value {
  font-style: italic;
  color: #6b7280;
}

/* Image requirements */
.image-requirements {
  background-color: rgba(255, 237, 213, 0.4);
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #fed7aa;
  margin-top: 1.5rem;
}

.image-requirements ul li {
  margin: 0.75rem 0;
  color: #9a3412;
}

/* Debug panel */
.ocr-text {
  font-family: monospace;
  white-space: pre-wrap;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  max-height: 300px;
  overflow-y: auto;
}
</style>
