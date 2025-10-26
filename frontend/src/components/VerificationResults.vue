<!-- VerificationResults.vue -->
<template>
  <div v-if="results" class="verification-results">
    <!-- Success State -->
    <Card v-if="results.success && !results.error" class="success-card">
      <template #content>
        <div class="flex align-items-center mb-3">
          <CheckCircle class="success-icon mr-2" size="32" />
          <h2 class="text-xl font-bold">Label Verification Successful</h2>
        </div>
        <p class="mb-4">
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
            <Tooltip v-if="getTooltip(key)">
              <template #target>
                <InfoIcon size="16" class="ml-2" />
              </template>
              <template #content>
                <div v-html="getTooltip(key)"></div>
              </template>
            </Tooltip>
          </div>
        </div>
      </template>
    </Card>

    <!-- Failure State -->
    <Card v-else-if="!results.success && !results.error" class="error-card">
      <template #content>
        <div class="flex align-items-center mb-3">
          <AlertOctagon class="error-icon mr-2" size="32" />
          <h2 class="text-xl font-bold">Label Verification Failed</h2>
        </div>
        <p class="mb-4">Discrepancies found between form and label image.</p>

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
              <div v-else class="text-sm text-red-700">Not found</div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Error State -->
    <Card v-else class="warning-card">
      <template #content>
        <div class="flex align-items-center mb-3">
          <AlertTriangle class="warning-icon mr-2" size="32" />
          <h2 class="text-xl font-bold">Unable to Process Image</h2>
        </div>
        <p class="error-message mb-4">
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
import {
  CheckCircle,
  AlertOctagon,
  AlertTriangle,
  Info as InfoIcon,
} from 'lucide-vue-next';

export default {
  name: 'VerificationResults',
  components: {
    CheckCircle,
    AlertOctagon,
    AlertTriangle,
    InfoIcon,
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
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, (str) => str.toUpperCase());
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
    getTooltip(field) {
      const tooltips = {
        brand_name: 'Brand name as it appears on the label',
        product_type: 'Type of alcoholic beverage (e.g., Vodka, Whiskey)',
        alcohol_content: 'Alcohol by volume (ABV) percentage',
        net_contents: 'Volume of the container (e.g., 750 mL)',
        government_warning: 'Required government warning statement',
      };
      return tooltips[field];
    },
  },
};
</script>

<style scoped>
.verification-results {
  max-width: 800px;
  margin: 0 auto;
}

.image-info-card {
  background-color: #f8f9fa;
}

.details-panel {
  background-color: rgba(0, 0, 0, 0.03);
}

.field-result {
  display: flex;
  align-items: flex-start;
  padding: 0.5rem;
  border-radius: 4px;
}

.field-result.success {
  background-color: rgba(0, 200, 0, 0.05);
}

.field-result.failure {
  background-color: rgba(255, 0, 0, 0.05);
}

.field-name {
  font-weight: 600;
  margin-right: 0.5rem;
  min-width: 120px;
}

.verified-tag {
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 12px;
  background-color: #22c55e;
  color: white;
  margin-left: auto;
}

.success-check {
  color: #22c55e;
}

.error-x {
  color: #ef4444;
}

.error-text {
  color: #dc2626;
}

.image-requirements {
  background-color: rgba(255, 237, 213, 0.4);
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #fed7aa;
}

.image-requirements ul li {
  margin: 0.5rem 0;
  color: #9a3412;
}

.ocr-text {
  font-family: monospace;
  white-space: pre-wrap;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  max-height: 300px;
  overflow-y: auto;
}

.tooltip-icon {
  cursor: help;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.tooltip-icon:hover {
  opacity: 1;
}
</style>

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
