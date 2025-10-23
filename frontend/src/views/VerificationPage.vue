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
                  placeholder="Enter brand name"
                  class="full-width large-input"
                  :class="{ 'p-invalid': errors.brandName }"
                />
                <small v-if="errors.brandName" class="p-error">{{ errors.brandName }}</small>
              </div>

              <!-- Product Type -->
              <div class="form-group">
                <label for="productType" class="label">Product Class/Type</label>
                <InputText
                  id="productType"
                  v-model="formData.productType"
                  placeholder="e.g., Kentucky Straight Bourbon Whiskey, IPA, Vodka"
                  class="full-width large-input"
                  :class="{ 'p-invalid': errors.productType }"
                />
                <small v-if="errors.productType" class="p-error">{{ errors.productType }}</small>
              </div>

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
                />
                <small v-if="errors.alcoholContent" class="p-error">{{ errors.alcoholContent }}</small>
              </div>

              <!-- Net Contents -->
              <div class="form-group">
                <label for="netContents" class="label">Net Contents</label>
                <InputText
                  id="netContents"
                  v-model="formData.netContents"
                  placeholder="e.g., 750 mL, 12 fl oz"
                  class="full-width large-input"
                />
              </div>
            </div>

            <!-- Image Upload Section -->
            <div class="form-group">
              <label class="label">Label Image</label>
              <FileUpload
                name="labelImage"
                @select="handleFileSelect"
                @clear="clearImage"
                :showUploadButton="false"
                :multiple="false"
                accept="image/jpeg,image/png"
                :maxFileSize="10000000"
                class="full-width file-upload"
                :class="{ 'p-invalid': errors.image }"
              >
                <template #empty>
                  <div class="flex flex-col items-center justify-center p-5">
                    <i class="pi pi-upload border-2 border-dashed rounded-full p-5 text-4xl text-gray-400"></i>
                    <p class="mt-4 text-center text-gray-600">Drag and drop files here to upload, or click to browse.</p>
                  </div>
                </template>
              </FileUpload>
              <small v-if="errors.image" class="p-error">{{ errors.image }}</small>
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
import { ref, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { verifyLabel } from '@/services/api'
import VerificationResults from '@/components/VerificationResults.vue'
import Toast from 'primevue/toast'

const toast = useToast();

// Form data
const formData = ref({
  brandName: '',
  productType: '',
  alcoholContent: null,
  netContents: '',
})

// File handling state
const selectedFile = ref(null)
const errors = ref({})

// UI state
const isLoading = ref(false)
const verificationResults = ref(null)

// Computed properties
const isFormValid = computed(() => {
  return (
    formData.value.brandName &&
    formData.value.productType &&
    formData.value.alcoholContent !== null &&
    selectedFile.value &&
    Object.keys(errors.value).length === 0
  )
})

// Watchers to clear errors on input
watch(() => formData.value.brandName, (value) => {
  if (value) delete errors.value.brandName;
});
watch(() => formData.value.productType, (value) => {
  if (value) delete errors.value.productType;
});
watch(() => formData.value.alcoholContent, (value) => {
  if (value !== null) delete errors.value.alcoholContent;
});


// Methods
const validateForm = () => {
  const newErrors = {}

  if (!formData.value.brandName) {
    newErrors.brandName = 'Brand name is required'
  }

  if (!formData.value.productType) {
    newErrors.productType = 'Product type is required'
  }

  if (formData.value.alcoholContent === null) {
    newErrors.alcoholContent = 'Alcohol content is required'
  } else {
    const abv = parseFloat(formData.value.alcoholContent)
    if (isNaN(abv) || abv < 0 || abv > 100) {
      newErrors.alcoholContent = 'Please enter a valid alcohol content (0-100%)'
    }
  }

  if (!selectedFile.value) {
    newErrors.image = 'Label image is required'
  }

  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const handleFileSelect = (event) => {
  const file = event.files[0]
  if (file) {
    selectedFile.value = file
    delete errors.value.image
  }
}

const clearImage = () => {
  selectedFile.value = null
}

const handleSubmit = async () => {
  if (!validateForm()) {
    toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Please fill in all required fields.', life: 3000 });
    return
  }

  isLoading.value = true
  verificationResults.value = null // Clear previous results
  
  try {
    const data = new FormData()
    data.append('brand_name', formData.value.brandName)
    data.append('product_type', formData.value.productType)
    data.append('alcohol_content', formData.value.alcoholContent)
    data.append('net_contents', formData.value.netContents)
    data.append('image', selectedFile.value)
    
    const response = await verifyLabel(data)
    verificationResults.value = {
      success: response.success,
      fields: {
        brandName: {
          value: response.results?.brandName?.value,
          expected: formData.value.brandName,
          matches: response.results?.brandName?.matches
        },
        productType: {
          value: response.results?.productType?.value,
          expected: formData.value.productType,
          matches: response.results?.productType?.matches
        },
        alcoholContent: {
          value: response.results?.alcoholContent?.value,
          expected: formData.value.alcoholContent,
          matches: response.results?.alcoholContent?.matches
        },
        netContents: {
          value: response.results?.netContents?.value,
          expected: formData.value.netContents,
          matches: response.results?.netContents?.matches
        }
      },
      error: response.error,
      ocrText: response.ocrText
    }

    const toastMessage = verificationResults.value.success
      ? { severity: 'success', summary: 'Verification Successful', detail: 'All fields match the label image.' }
      : { severity: 'warn', summary: 'Verification Failed', detail: 'Some fields do not match the label image.' }
    
    toast.add({ ...toastMessage, life: 5000 })
  } catch (error) {
    verificationResults.value = {
      success: false,
      error: error.message || 'An unexpected error occurred during verification.',
      fields: {}
    }
    toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'An unexpected error occurred.', life: 5000 })
  } finally {
    isLoading.value = false
  }
}
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
}
</style>