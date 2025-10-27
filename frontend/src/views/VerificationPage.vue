<!-- VerificationPage.vue -->
<template>
  <div class="container">
    <Toast position="top-right" />
    <div class="center">
      <Card>
        <template #title>
          <h1 class="text-2xl font-bold text-gray-900">
            Alcohol Label Verification
          </h1>
        </template>
        <template #content>
          <form @submit.prevent="handleSubmit" class="form">
            <div class="form-section">
              <!-- Brand Name -->
              <div class="form-group">
                <label for="brandName" class="label">Brand Name</label>
                <InputText
                  id="brandName"
                  v-model="formData.brandName"
                  placeholder="Brand name"
                  class="full-width large-input"
                  :class="{ 'p-invalid': errors.brandName }"
                  v-tooltip.right="
                    'Enter the brand name of the alcohol product'
                  "
                />
                <small v-if="errors.brandName" class="p-error">{{
                  errors.brandName
                }}</small>
              </div>

              <!-- Product Type -->
              <div class="form-group">
                <label for="productType" class="label"
                  >Product Class/Type</label
                >
                <InputText
                  id="productType"
                  v-model="formData.productType"
                  placeholder="e.g., Kentucky Straight Bourbon Whiskey, IPA, Vodka"
                  class="full-width large-input"
                  :class="{ 'p-invalid': errors.productType }"
                  v-tooltip.right="
                    'Enter the type or class of the alcoholic beverage'
                  "
                />
                <small v-if="errors.productType" class="p-error">{{
                  errors.productType
                }}</small>
              </div>

              <!-- Feature Toggles -->
              <Splitter class="no-lines">
                <SplitterPanel
                  class="flex align-items-center justify-content-center"
                  :size="3"
                  :minSize="2"
                >
                  <InputSwitch v-model="formData.fuzzyMatch" />
                </SplitterPanel>
                <SplitterPanel
                  class="flex align-items-start justify-content-start"
                  :size="90"
                >
                  Enable approximate text matching for better results
                </SplitterPanel>
              </Splitter>

              <Splitter class="no-lines">
                <SplitterPanel
                  class="flex align-items-center justify-content-center"
                  :size="3"
                  :minSize="2"
                >
                  <InputSwitch v-model="formData.checkGovernmentWarning" />
                </SplitterPanel>
                <SplitterPanel
                  class="flex align-items-start justify-content-start"
                  :size="90"
                >
                  Check for government warning on the label
                </SplitterPanel>
              </Splitter>

              <!-- Alcohol Content -->
              <div class="form-group">
                <label for="alcoholContent" class="label">ABV %</label>
                <InputNumber
                  id="alcoholContent"
                  v-model="formData.alcoholContent"
                  mode="decimal"
                  :minFractionDigits="1"
                  :maxFractionDigits="1"
                  :min="0"
                  :max="100"
                  placeholder="0.0"
                  class="full-width large-input"
                  :class="{ 'p-invalid': errors.alcoholContent }"
                  suffix=" %"
                  v-tooltip.right="
                    'Enter the alcohol by volume (ABV) percentage'
                  "
                />
                <small v-if="errors.alcoholContent" class="p-error">{{
                  errors.alcoholContent
                }}</small>
              </div>

              <!-- Net Contents -->
              <div class="form-group">
                <label for="netContents" class="label">Net Contents</label>
                <InputText
                  id="netContents"
                  v-model="formData.netContents"
                  placeholder="e.g., 750 mL, 12 fl oz"
                  class="full-width large-input"
                  v-tooltip.right="
                    'Enter the net contents as it appears on the label (optional)'
                  "
                />
              </div>
            </div>
            <!-- Image Upload Section -->
            <div class="form-group">
              <label class="label"> Label Image </label>
              <small class="text-gray-600 mb-2 text-lg"
                >Cancel previous image before attempting to choose a new
                one</small
              >

              <FileUpload
                ref="fileUpload"
                name="labelImage"
                @select="handleFileSelect"
                @clear="clearImage"
                @error="handleUploadError"
                :showUploadButton="false"
                :multiple="false"
                accept="image/jpeg,image/png"
                :maxFileSize="5242880"
                :customUpload="true"
                class="full-width file-upload"
                :class="{ 'p-invalid': errors.image }"
              >
                <template #empty>
                  <div class="flex flex-col items-center justify-center p-5">
                    <i
                      class="pi pi-upload border-2 border-dashed rounded-full p-5 text-4xl text-gray-400"
                    ></i>
                    <p class="mt-4 text-center text-gray-600">
                      Drag and drop image here, or click Choose to browse
                      <br />
                      <small class="text-gray-500">
                        Supported formats: JPEG, PNG | Max size: 5MB
                      </small>
                    </p>
                  </div>
                </template>
                <template #content>
                  <div v-if="selectedImage" class="image-preview">
                    <div class="image-info text-sm text-gray-600 mb-2">
                      <div>Size: {{ formatFileSize(selectedImage.size) }}</div>
                      <div v-if="imageDimensions">
                        Dimensions: {{ imageDimensions.width }}x{{
                          imageDimensions.height
                        }}px
                      </div>
                    </div>
                  </div>
                </template>
              </FileUpload>
              <small v-if="errors.image" class="p-error block mt-2">{{
                errors.image
              }}</small>
              <small v-if="imageWarning" class="text-orange-700 block mt-2">
                ⚠️ {{ imageWarning }}
              </small>
            </div>

            <!-- Submit Button -->
            <Button
              type="submit"
              label="Verify Label"
              class="submit-button"
              :loading="isLoading"
              :disabled="!isFormValid"
            />
          </form>
        </template>
      </Card>

      <Transition name="fade">
        <VerificationResults
          v-if="verificationResults"
          :results="verificationResults"
          class="mt-6"
        />
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { verifyLabel } from '@/services/api';
import VerificationResults from '@/components/VerificationResults.vue';
import Toast from 'primevue/toast';

const toast = useToast();

// Form data
const formData = ref({
  brandName: '',
  productType: '',
  alcoholContent: null,
  netContents: '',
  fuzzyMatch: false,
  checkGovernmentWarning: false,
});

// File handling state
const selectedFile = ref(null);
const selectedImage = ref(null);
const imageDimensions = ref(null);
const imageWarning = ref('');
const errors = ref({});
const fileUpload = ref(null);

// UI state
const isLoading = ref(false);
const verificationResults = ref(null);

// Watchers to clear errors on input
watch(
  () => formData.value.brandName,
  (value) => {
    if (value) delete errors.value.brandName;
  }
);
watch(
  () => formData.value.productType,
  (value) => {
    if (value) delete errors.value.productType;
  }
);
watch(
  () => formData.value.alcoholContent,
  (value) => {
    if (value !== null) delete errors.value.alcoholContent;
  }
);

// Computed properties
const isFormValid = computed(() => {
  return (
    formData.value.brandName &&
    formData.value.productType &&
    formData.value.alcoholContent !== null &&
    selectedFile.value &&
    Object.keys(errors.value).length === 0
  );
});

// Image handling methods
const formatFileSize = (bytes) => {
  if (!bytes) return '0 KB';
  const kb = bytes / 1024;
  return kb < 1024 ? `${Math.round(kb)} KB` : `${(kb / 1024).toFixed(1)} MB`;
};

const getImageDimensions = (file) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      resolve({
        width: img.width,
        height: img.height,
      });
    };
    img.src = URL.createObjectURL(file);
  });
};

const checkImageQuality = async (file, dimensions) => {
  const warnings = [];

  // Check resolution
  if (dimensions.width < 800 || dimensions.height < 800) {
    warnings.push('Image resolution is low, which may affect text recognition');
  }

  // Check file size
  if (file.size < 50 * 1024) {
    // Less than 50KB
    warnings.push(
      'Image file size is very small, which may indicate low quality'
    );
  }

  return warnings.length > 0 ? warnings.join('. ') : '';
};

const handleFileSelect = async (event) => {
  const file = event.files[0];
  imageWarning.value = '';

  if (file) {
    selectedFile.value = file;
    selectedImage.value = file;

    try {
      const dims = await getImageDimensions(file);
      imageDimensions.value = dims;

      const warning = await checkImageQuality(file, dims);
      if (warning) {
        imageWarning.value = warning;
      }
    } catch (err) {
      console.error('Error processing image:', err);
    }

    delete errors.value.image;
  }
};

const handleUploadError = (error) => {
  if (error.type === 'max-file-size') {
    errors.value.image = 'File size exceeds maximum limit of 5MB';
  }
};

const clearImage = () => {
  selectedFile.value = null;
  selectedImage.value = null;
  imageDimensions.value = null;
  imageWarning.value = '';
  if (fileUpload.value) {
    fileUpload.value.clear();
  }
};

// Form validation and submission
const validateForm = () => {
  const newErrors = {};

  if (!formData.value.brandName) {
    newErrors.brandName = 'Brand name is required';
  }

  if (!formData.value.productType) {
    newErrors.productType = 'Product type is required';
  }

  if (formData.value.alcoholContent === null) {
    newErrors.alcoholContent = 'Alcohol content is required';
  } else {
    const abv = parseFloat(formData.value.alcoholContent);
    if (isNaN(abv) || abv < 0 || abv > 100) {
      newErrors.alcoholContent =
        'Please enter a valid alcohol content (0-100%)';
    }
  }

  if (!selectedFile.value) {
    newErrors.image = 'Label image is required';
  }

  errors.value = newErrors;
  return Object.keys(newErrors).length === 0;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    toast.add({
      severity: 'error',
      summary: 'Validation Error',
      detail: 'Please fill in all required fields.',
      life: 3000,
    });
    return;
  }

  isLoading.value = true;
  verificationResults.value = null; // Clear previous results

  try {
    const data = new FormData();
    data.append('brand_name', formData.value.brandName);
    data.append('product_type', formData.value.productType);
    data.append('alcohol_content', formData.value.alcoholContent);
    data.append('net_contents', formData.value.netContents);
    data.append('fuzzy_match', formData.value.fuzzyMatch);
    data.append(
      'check_government_warning',
      formData.value.checkGovernmentWarning
    );
    data.append('image', selectedFile.value);

    const response = await verifyLabel(data);

    verificationResults.value = {
      success: response.success,
      message: response.message,
      matches: response.matches,
      close_matches: response.close_matches || {},
      expected_values: {
        brand_name: formData.value.brandName,
        product_type: formData.value.productType,
        alcohol_content: formData.value.alcoholContent.toString(),
        net_contents: formData.value.netContents,
        government_warning: formData.value.checkGovernmentWarning
          ? 'government warning'
          : '',
      },
      raw_ocr_text: response.raw_ocr_text,
      image_info: response.image_info,
    };

    if (response.success) {
      toast.add({
        severity: 'success',
        summary: 'Verification Successful',
        detail: response.message,
        life: 5000,
      });
    } else if (!response.success) {
      toast.add({
        severity: 'warn',
        summary: 'Verification Failed',
        detail: response.message,
        life: 5000,
      });
    }
  } catch (error) {
    console.error('Verification error:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail:
        error.response?.data?.detail ||
        'Failed to process the verification request',
      life: 5000,
    });

    verificationResults.value = {
      success: false,
      error: error.response?.data?.detail || 'An unexpected error occurred',
      expected_values: {
        brand_name: formData.value.brandName,
        product_type: formData.value.productType,
        alcohol_content: formData.value.alcoholContent.toString(),
        net_contents: formData.value.netContents,
        government_warning: formData.value.checkGovernmentWarning
          ? 'government warning'
          : '',
      },
    };
  } finally {
    isLoading.value = false;
  }
};
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.center {
  max-width: 800px;
  margin: 0 auto;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  font-weight: 600;
  color: #374151;
}

.full-width {
  width: 100%;
}

.submit-button {
  margin-top: 1rem;
  min-height: 40px;
}

.no-lines .p-splitter-gutter {
  display: none;
}

.no-lines {
  border: none;
  outline: none;
}
</style>
