<template>
    <div class="w-full max-w-2xl border border-[#ffffff31] bg-[#0a0a0a] rounded-lg shadow-xl text-[#e6e6e6] p-4">
        <div class="space-y-4">
            <div class="w-full border border-white/20 p-4 rounded-md bg-[#0a0a0a] flex flex-col gap-3">
                <audio ref="audioPlayerOrig" :src="srcOrig" @timeupdate="onTimeUpdate('orig')" @loadedmetadata="onLoadedMetadata('orig')" @ended="isPlayingOrig = false"></audio>
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        <span class="px-1.5 py-0.5 rounded text-[10px] bg-white/10 text-white/40 uppercase">Оригинал</span>
                    </div>
                    <span class="text-[10px] font-mono text-white/40">
                    <span class="text-white">{{ formatTime(currentTimeOrig) }}</span> / {{ formatTime(durationOrig) }}</span>
                </div>

                <div class="flex items-center gap-4">
                    <button @click="togglePlay('orig')" class="size-10 flex items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 transition shrink-0">
                        <RiPlayFill v-if="!isPlayingOrig" />
                        <RiPauseLine v-else />
                    </button>

                    <div @mousedown="startDragging($event, 'orig')" @touchstart="startDragging($event, 'orig')" class="relative flex-1 h-1.5 bg-white/10 rounded-full cursor-pointer group touch-none">
                        <div class="absolute inset-y-0 left-0 bg-[#979797] rounded-full pointer-events-none" :style="{ width: progressOrig + '%' }"></div>
                        <div class="absolute top-1/2 -translate-y-1/2 size-3 bg-white rounded-full shadow-md pointer-events-none" :style="{ left: `calc(${progressOrig}% - 6px)` }"></div>
                    </div>

                    <a :href="srcOrig" download class="size-10 flex items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 transition shrink-0" title="Скачать аудио">
                        <RiDownload2Line />
                    </a>
                </div>

                <div class="w-full border border-white/10 rounded-md overflow-hidden bg-white/5">
                    <div class="flex items-center justify-between pr-3">
                        <div class="flex items-center gap-1 p-1">
                            <button @click="isTextOpenOrig = !isTextOpenOrig" class="p-2 text-white/60 hover:text-white hover:bg-white/5 rounded-md transition-colors flex items-center justify-center">
                                <RiArrowDownSLine v-if="isTextOpenOrig" size="20" />
                                <RiArrowRightSLine v-else size="20" />
                            </button>
                            <span class="text-xs font-bold uppercase tracking-wider text-white/40 select-none">Транскрипция</span>
                        </div>
                        <button @click="downloadAsFile(props.textOrig, 'original_transcription.txt')" 
                        class="p-2 text-white/60 hover:text-white transition-colors" > 
                            <RiDownload2Line size="20" />
                        </button> 
                     </div>
                    <div v-show="isTextOpenOrig" class="p-4 border-t border-white/10 bg-black/20">
                        <p class="text-sm leading-relaxed text-white/80 whitespace-pre-wrap">{{ props.textOrig || 'Текст оригинала не загружен...' }}</p>
                    </div>
                </div>
            </div>

            <div class="w-full border border-white/20 p-4 rounded-md bg-[#0a0a0a] flex flex-col gap-3">
                <audio ref="audioPlayerEdit" :src="srcEdit" @timeupdate="onTimeUpdate('edit')" @loadedmetadata="onLoadedMetadata('edit')" @ended="isPlayingEdit = false"></audio>
        
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        <span class="px-1.5 py-0.5 rounded text-[10px] bg-white/10 text-white/40 uppercase">Изменено</span>
                    </div>
                    <span class="text-[10px] font-mono text-white/40">
                    <span class="text-white">{{ formatTime(currentTimeEdit) }}</span> / {{ formatTime(durationEdit) }}</span>
                </div>

                <div class="flex items-center gap-4">
                    <button @click="togglePlay('edit')" class="size-10 flex items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 transition shrink-0">
                        <RiPlayFill v-if="!isPlayingEdit" />
                        <RiPauseLine v-else />
                    </button>
          
                    <div @mousedown="startDragging($event, 'edit')" @touchstart="startDragging($event, 'edit')" class="relative flex-1 h-1.5 bg-white/10 rounded-full cursor-pointer group touch-none">
                        <div v-for="(zone, index) in redZones" :key="index" class="absolute inset-y-0 bg-[#7e2828] pointer-events-none" :style="getZoneStyle(zone)"></div>
                        <div class="absolute inset-y-0 left-0 bg-[#979797] rounded-full pointer-events-none" :style="{ width: progressEdit + '%' }"></div>
                        <div class="absolute top-1/2 -translate-y-1/2 size-3 bg-white rounded-full shadow-md pointer-events-none z-10" :style="{ left: `calc(${progressEdit}% - 6px)` }"></div>
                    </div>

                    <a :href="srcEdit" download class="size-10 flex items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 transition shrink-0" title="Скачать аудио">
                        <RiDownload2Line />
                    </a>
                </div>

                <div class="w-full border border-white/10 rounded-md overflow-hidden bg-white/5">
                    <div class="flex items-center justify-between pr-3">
                        <div class="flex items-center gap-1 p-1">
                            <button @click="isTextOpenEdit = !isTextOpenEdit" class="p-2 text-white/60 hover:text-white hover:bg-white/5 rounded-md transition-colors flex items-center justify-center">
                                <RiArrowDownSLine v-if="isTextOpenEdit" size="20" />
                                <RiArrowRightSLine v-else size="20" />
                            </button>
                            <span class="text-xs font-bold uppercase tracking-wider text-white/40 select-none">Транскрипция</span>
                        </div>
                        <button @click="downloadAsFile(cleanTextForDownload, 'edited_transcription.txt')" 
                        class="p-2 text-white/60 hover:text-white transition-colors">
                            <RiDownload2Line size="20" />
                        </button> 
                    </div>
                    <div v-show="isTextOpenEdit" class="p-4 border-t border-white/10 bg-black/20">
                        <p class="text-sm leading-relaxed text-white/80 whitespace-pre-wrap" v-html="redactedText"></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { RiPlayFill, RiPauseLine, RiDownload2Line, RiArrowDownSLine, RiArrowRightSLine } from '@remixicon/vue'

const props = defineProps<{
    srcOrig: string;
    srcEdit: string;
    textOrig?: string;
    textEdit?: string;
    redZonesData?: Array<{start: number, width: number}>;
}>();

const downloadAsFile = (content: string | undefined, fileName: string) => {
    if (!content) return;
  
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
  
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
  
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  
    window.URL.revokeObjectURL(url);
};

const cleanTextForDownload = computed(() => {
    if (!props.textEdit) return '';
    return props.textEdit.replace(/<d>(.*?)<\/d>/g, '[REDACTED]');
});

const redZones = ref(props.redZonesData || []);
const isTextOpenOrig = ref(false);
const isTextOpenEdit = ref(true);

watch(() => props.redZonesData, (newVal) => {
    redZones.value = newVal || [];
});

const redactedText = computed(() => {
    if (!props.textEdit) return 'Текст изменений не загружен..';
    return props.textEdit.replace(/<d>(.*?)<\/d>/g, '<span class="bg-[#EF444433] text-[#f87171] font-mono">[REDACTED]</span>');
});

const audioPlayerOrig = ref<HTMLAudioElement | null>(null);
const isPlayingOrig = ref(false);
const currentTimeOrig = ref(0);
const durationOrig = ref(0);
const progressOrig = ref(0);

const audioPlayerEdit = ref<HTMLAudioElement | null>(null);
const isPlayingEdit = ref(false);
const currentTimeEdit = ref(0);
const durationEdit = ref(0);
const progressEdit = ref(0);

const isDragging = ref(false);

const getZoneStyle = (zone: { start: number, width: number }) => {
    if (!durationEdit.value) return { display: 'none' };
    return {
        left: `${(zone.start / durationEdit.value) * 100}%`,
        width: `${(zone.width / durationEdit.value) * 100}%`
    };
};

const togglePlay = (type: 'orig' | 'edit') => {
    const player = type === 'orig' ? audioPlayerOrig.value : audioPlayerEdit.value;
    const state = type === 'orig' ? isPlayingOrig : isPlayingEdit;
    if (!player) return;
    player.paused ? (player.play(), state.value = true) : (player.pause(), state.value = false);
};

const onTimeUpdate = (type: 'orig' | 'edit') => {
    if (isDragging.value) return;
    const player = type === 'orig' ? audioPlayerOrig.value : audioPlayerEdit.value;
    if (!player) return;
    if (type === 'orig') {
        currentTimeOrig.value = player.currentTime;
        progressOrig.value = (player.currentTime / player.duration) * 100;
    } else {
        currentTimeEdit.value = player.currentTime;
        progressEdit.value = (player.currentTime / player.duration) * 100;
    }
};

const onLoadedMetadata = (type: 'orig' | 'edit') => {
    const player = type === 'orig' ? audioPlayerOrig.value : audioPlayerEdit.value;
    if (player) {
        if (type === 'orig') durationOrig.value = player.duration;
    else durationEdit.value = player.duration;
    }
};

const startDragging = (event: MouseEvent | TouchEvent, type: 'orig' | 'edit') => {
    isDragging.value = true;
    const bar = event.currentTarget as HTMLElement;
    const player = type === 'orig' ? audioPlayerOrig.value : audioPlayerEdit.value;
  
    const move = (e: MouseEvent | TouchEvent) => {
    const rect = bar.getBoundingClientRect();
    const clientX = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;
    const percent = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100));
    if (type === 'orig') progressOrig.value = percent;
    else progressEdit.value = percent;
    };

    const stop = () => {
        isDragging.value = false;
        if (player) {
        const p = type === 'orig' ? progressOrig.value : progressEdit.value;
        player.currentTime = (p / 100) * player.duration;
        }
        window.removeEventListener('mousemove', move as any);
        window.removeEventListener('mouseup', stop);
        window.removeEventListener('touchmove', move as any);
        window.removeEventListener('touchend', stop);
    };

    window.addEventListener('mousemove', move as any);
    window.addEventListener('mouseup', stop);
    window.addEventListener('touchmove', move as any);
    window.addEventListener('touchend', stop);
    move(event);
};

const formatTime = (time: number) => {
    if (!time || isNaN(time)) return "0:00";
    const min = Math.floor(time / 60);
    const sec = Math.floor(time % 60);
    return `${min}:${sec.toString().padStart(2, '0')}`;
};
</script>

<style scoped>
:deep(d) {
    color: #f87171; 
    background-color: #EF444433;
    padding: 0 2px;
    border-radius: 2px;
}
</style>