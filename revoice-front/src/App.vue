<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { RiUpload2Line, RiFileMusicLine } from '@remixicon/vue';
import Editor from './Editor.vue';

const fileInput = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);
const isUploaded = ref(false);
const isLoading = ref(false);

const selectedFile = ref<File | null>(null);
const fileDuration = ref<string | null>(null);

const audioUrls = ref({ original: '', edit: '' });
const transcriptions = ref({ orig: '', edit: '' });
const redZonesData = ref([]);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = 2;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const handleFileSelect = (event: any) => {
  const files = event.target.files || event.dataTransfer.files;
  if (!files.length) return;

  const file = files[0];

  if (file.size > 25 * 1024 * 1024) {
    alert('Файл слишком большой! Лимит 25 МБ.');
    return;
  }

  selectedFile.value = file;

  const objectUrl = URL.createObjectURL(file);
  const audio = new Audio();
  audio.src = objectUrl;

  audio.onloadedmetadata = () => {
    const duration = audio.duration;

    if (duration > 90) {
      alert('Аудио не должно быть длиннее 1.5 минут!');

      selectedFile.value = null;
      fileDuration.value = null;

      URL.revokeObjectURL(objectUrl);
      return;
    }

    fileDuration.value = formatDuration(duration);
    URL.revokeObjectURL(objectUrl);
  };
};

const uploadFile = async () => {
  if (!selectedFile.value) {
    alert('Сначала выберите файл!');
    return;
  }

  isLoading.value = true;

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await axios.post(
      'http://81.177.222.220:8000/upload/',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );

    audioUrls.value = response.data.urls;
    transcriptions.value = response.data.transcriptions;
    redZonesData.value = response.data.red_zones;

    isUploaded.value = true;
  } catch (error) {
    console.error('Ошибка при загрузке:', error);
    alert('Произошла ошибка при загрузке файла. Проверьте консоль бэкенда.');
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-[#000000] bg-gradient-to-t from-[#049bff2c] smooth-bg to-black flex flex-col items-center justify-center p-8 space-y-12 overflow-hidden font-ibm">
    
    <div class="flex flex-col items-center text-center">
      <h1 class="text-5xl text-[#e6e6e6] font-black font-rowdies">ReVoice</h1>
        <p class="text-white/45 max-w-md mt-2">MVP-решение для защиты приватности в аудио-файлах с помощью AI.</p>
    </div>

  <Editor v-if="isUploaded" :src-orig="audioUrls.original" :src-edit="audioUrls.edit" :text-orig="transcriptions.orig" :text-edit="transcriptions.edit" :red-zones-data="redZonesData"/>
    <template v-else>
      <div @click="triggerFileInput" @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="isDragging = false; handleFileSelect($event)" :class="[
          'w-80 h-80 border-2 border-dashed rounded-lg flex flex-col items-center justify-center gap-4 backdrop-blur-3xl duration-150 shadow-md cursor-pointer',
           isDragging ? 'border-white scale-105 bg-white/10' : 'border-[#ffffff86] opacity-90 hover:opacity-100', selectedFile ? 'border-white/75 bg-white-500/10' : '' ]">
        <input type="file" ref="fileInput" class="hidden" accept="audio/*" @change="handleFileSelect" />

        <template v-if="selectedFile">
          <div class="flex flex-col items-center w-full px-6 animate-in fade-in zoom-in duration-300">
            <div class="my-8 w-full flex flex-col items-center justify-center">
              
              <div class="flex justify-center mb-4">
                <RiFileMusicLine size="92px" color="#ffffff" />
              </div>

              <p class="text-[#e6e6e6] font-medium text-center truncate w-full max-w-65">
                {{ selectedFile.name }}
              </p>
              
            </div>

            <div class="w-full flex justify-between items-center border-t border-white/10 pt-4 px-2 ", style="border-image-source: linear-gradient(to right, #ffffff00, #ffffff1c, #ffffff00); border-image-slice: 1;">
              <div class="flex flex-col items-start">
                <span class="text-white/30 text-[10px] uppercase tracking-wider">Размер</span>
                <span class="text-[#e6e6e6] text-sm font-mono">{{ formatSize(selectedFile.size) }}</span>
              </div>

              <div class="flex flex-col items-end ">
                <span class="text-white/30 text-[10px] uppercase tracking-wider">Длительность</span>
                <span class="text-[#ffffff] text-sm font-mono font-bold">
                  {{ fileDuration || '--:--' }}
                </span>
              </div>
            </div>

          </div>
        </template>
        <template v-else>
          <RiUpload2Line size="64px" color="#e6e6e6"/> 
          <div class="text-center">
            <p class="text-[#e6e6e6] text-sm">
              {{ isDragging ? 'Бросайте файл сюда' : 'Нажмите или перетащите файл' }}
            </p>
            <p class="text-[#e6e6e6]/60 text-xs mt-2">
              Аудио файлы. До 25 MB.
            </p>
          </div>
        </template>
      </div>

      <div class="w-full max-w-lg border border-white/20 bg-[#0a0a0a] p-4 rounded-lg shadow-xl text-[#e6e6e6]">
        <div class="flex flex-row items-end gap-3">
          <div class="flex-1 flex flex-col text-left gap-1">
            <p>Режим:</p>
            <select class="w-full appearance-none sm:w-auto h-12 border border-white/20 bg-[#070707] rounded-md text-center font-bold hover:bg-[#0a0a0a] duration-150 outline-none focus:border-white/40">
              <!--<option value="faster">FASTER</option>-->
              <option value="quality">QUALITY</option>
            </select>
          </div>

          <button @click="uploadFile" :disabled="!selectedFile || isLoading" :class="[
              'h-12 px-8 bg-[#ebebeb] text-black font-black uppercase text-sm rounded-md duration-150 opacity-95 disabled:opacity-80 disabled:cursor-not-allowed hover:opacity-100', selectedFile && !isLoading ]">
            {{ isLoading ? 'Загрузка...' : 'Начать' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>