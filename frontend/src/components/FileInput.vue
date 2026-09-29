<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{ (event: 'file-selected', file: File): void }>()

// const fileInput = ref<HTMLInputElement | null>(null)
const uploadError = ref('')
const selectedFileName = ref('')
const isDragActive = ref(false)

const JSON_EXTENSIONS = ['.json']
const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']

function isJsonFile(file: File): boolean {
  const name = file.name.toLowerCase()
  return JSON_EXTENSIONS.some((ext) => name.endsWith(ext))
}

function isImageFile(file: File): boolean {
  const name = file.name.toLowerCase()
  return file.type.startsWith('image/') || IMAGE_EXTENSIONS.some((ext) => name.endsWith(ext))
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input?.files?.[0]
  handleSelectedFile(file)
  // 清空 input，保证连续选择同一个文件时也能触发 change
  input.value = ''
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  isDragActive.value = false
  const file = event.dataTransfer?.files?.[0]
  handleSelectedFile(file)
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
  isDragActive.value = true
}

function handleDragLeave() {
  isDragActive.value = false
}

function handleSelectedFile(file: File | undefined) {
  uploadError.value = ''
  selectedFileName.value = ''

  if (!file) {
    uploadError.value = '请选择一个 JSON 文件或一张包含二维码的图片。'
    return
  }

  if (!isJsonFile(file) && !isImageFile(file)) {
    uploadError.value = '只支持 .json 文件或图片（PNG / JPG 等）。'
    return
  }

  selectedFileName.value = file.name
  emit('file-selected', file)
}
</script>

<template>
  <div
    class="upload-card"
    :class="{ 'drag-active': isDragActive }"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <div class="dropzone">
      <p>将 .json 纪念章文件或包含二维码的图片（PNG）拖拽到此处，或点击按钮选择文件。</p>
      <p class="dropzone-hint">选择图片时，会识别图片中的二维码，并读取其中的 JSON 作为纪念章数据。</p>
      <label class="upload-label" for="json-upload">选择纪念章文件</label>
      <input
        id="json-upload"
        ref="fileInput"
        type="file"
        accept="application/json,.json,image/png,image/jpeg,image/webp,image/gif,image/bmp,.png,.jpg,.jpeg,.webp,.gif,.bmp"
        @change="handleFileChange"
      />
    </div>

    <p class="file-name" v-if="selectedFileName">已选文件：{{ selectedFileName }}</p>
    <p class="error-message" v-if="uploadError">{{ uploadError }}</p>
  </div>
</template>

<style scoped>
.upload-card {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.upload-card.drag-active {
  border-color: #2563eb;
  background-color: #eff6ff;
}

.dropzone {
  display: grid;
  gap: 1rem;
  align-items: center;
  justify-items: center;
  text-align: center;
  padding: 1.5rem;
  border: 2px dashed #cbd5e1;
  border-radius: 14px;
  background: #f8fafc;
}

.dropzone p {
  margin: 0;
  color: #64748b;
}

.dropzone .dropzone-hint {
  font-size: 0.85rem;
  color: #94a3b8;
}

.upload-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.9rem 1.2rem;
  border-radius: 9999px;
  background: #2563eb;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.upload-label:hover {
  background: #1d4ed8;
}

input[type='file'] {
  display: none;
}

.file-name,
.error-message {
  margin: 0;
  color: #334155;
}

.error-message {
  color: #b91c1c;
}
</style>
